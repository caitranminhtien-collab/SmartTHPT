import hashlib, hmac, json, os, random, secrets, sqlite3, time
from contextlib import contextmanager, asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, model_validator
from .seed import TOPICS
from .ml import predict_topic

ROOT=Path(__file__).resolve().parents[1]
DB=Path(os.environ.get('SMARTTHPT_DB', str(ROOT/'data'/'smartthpt.sqlite3')))
SESSION_TTL=86400*7

@contextmanager
def db():
    DB.parent.mkdir(parents=True, exist_ok=True)
    con=sqlite3.connect(DB, timeout=10)
    con.row_factory=sqlite3.Row
    con.execute('PRAGMA foreign_keys=ON')
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback(); raise
    finally: con.close()

def hash_password(password, salt=None):
    salt=salt or secrets.token_hex(16)
    return salt+':'+hashlib.scrypt(password.encode(),salt=bytes.fromhex(salt),n=16384,r=8,p=1).hex()

def check_password(password, stored):
    return hmac.compare_digest(hash_password(password,stored.split(':')[0]),stored)

def init_db():
    with db() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE COLLATE NOCASE, password TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'student');
        CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY,user_id INTEGER NOT NULL REFERENCES users(id),expires INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS questions(id INTEGER PRIMARY KEY,grade INTEGER NOT NULL,subject TEXT NOT NULL,topic TEXT NOT NULL,prompt TEXT NOT NULL UNIQUE,options TEXT NOT NULL,answer INTEGER NOT NULL,explanation TEXT NOT NULL,difficulty TEXT NOT NULL,source TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS quizzes(id TEXT PRIMARY KEY,user_id INTEGER NOT NULL REFERENCES users(id),mode TEXT NOT NULL,question_ids TEXT NOT NULL,created INTEGER NOT NULL,deadline INTEGER,submitted INTEGER);
        CREATE TABLE IF NOT EXISTS responses(quiz_id TEXT REFERENCES quizzes(id),question_id INTEGER REFERENCES questions(id),selected INTEGER,correct INTEGER NOT NULL,PRIMARY KEY(quiz_id,question_id));
        ''')
        if not c.execute('SELECT 1 FROM questions LIMIT 1').fetchone():
            for q in json.loads((ROOT/'data'/'questions.json').read_text(encoding='utf-8')): insert_question(c,q)

def insert_question(c,q):
    return c.execute('INSERT OR IGNORE INTO questions(grade,subject,topic,prompt,options,answer,explanation,difficulty,source) VALUES(?,?,?,?,?,?,?,?,?)',(q['grade'],q['subject'],q['topic'],q['prompt'],json.dumps(q['options'],ensure_ascii=False),q['answer'],q['explanation'],q['difficulty'],q['source'])).rowcount

@asynccontextmanager
async def lifespan(app):
    init_db(); yield

app=FastAPI(title='SmartTHPT',version='0.1.0',lifespan=lifespan)

@app.get('/api/health', tags=['system'])
def health():
    return {'status': 'ok'}


class Credentials(BaseModel):
    username:str=Field(min_length=3,max_length=32,pattern=r'^[a-zA-Z0-9_.-]+$')
    password:str=Field(min_length=8,max_length=128)

class QuizRequest(BaseModel):
    mode:str='practice'
    topic:str|None=None
    count:int=Field(default=10,ge=1,le=30)

class Submission(BaseModel):
    answers:dict[int,int]=Field(default_factory=dict)

class Question(BaseModel):
    grade:int=12
    subject:str='Toán'
    topic:str=Field(min_length=1,max_length=100)
    prompt:str=Field(min_length=5,max_length=4000)
    options:list[str]=Field(min_length=4,max_length=4)
    answer:int=Field(ge=0,le=3)
    explanation:str=Field(min_length=1,max_length=6000)
    difficulty:str='Cơ bản'
    source:str=Field(min_length=1,max_length=500)
    @model_validator(mode='after')
    def valid(self):
        if self.grade not in (10,11,12) or len(set(self.options))!=4 or any(not x.strip() for x in self.options): raise ValueError('Lớp hoặc phương án không hợp lệ')
        return self

class ImportRequest(BaseModel):
    questions:list[Question]=Field(min_length=1,max_length=200)

class ClassifyRequest(BaseModel):
    prompt:str=Field(min_length=5,max_length=4000)

def token_hash(token): return hashlib.sha256(token.encode()).hexdigest()

def session_user(request:Request):
    token=request.cookies.get('smartthpt_session')
    if not token: raise HTTPException(401,'Vui lòng đăng nhập')
    with db() as c:
        row=c.execute('SELECT u.id,u.username,u.role FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token=? AND s.expires>?',(token_hash(token),int(time.time()))).fetchone()
    if not row: raise HTTPException(401,'Phiên đăng nhập hết hạn')
    return dict(row)

def admin_user(user=Depends(session_user)):
    if user['role']!='admin': raise HTTPException(403,'Chỉ quản trị viên được truy cập')
    return user

def login_session(c,response,user_id):
    token=secrets.token_urlsafe(32); now=int(time.time())
    c.execute('DELETE FROM sessions WHERE expires<=?',(now,))
    c.execute('INSERT INTO sessions VALUES(?,?,?)',(token_hash(token),user_id,now+SESSION_TTL))
    response.set_cookie('smartthpt_session',token,httponly=True,samesite='strict',max_age=SESSION_TTL,secure=os.environ.get('SMARTTHPT_HTTPS')=='1')

@app.post('/api/register')
def register(body:Credentials,response:Response):
    with db() as c:
        try: cur=c.execute('INSERT INTO users(username,password) VALUES(?,?)',(body.username,hash_password(body.password)))
        except sqlite3.IntegrityError: raise HTTPException(409,'Tên đăng nhập đã tồn tại')
        login_session(c,response,cur.lastrowid)
    return {'username':body.username,'role':'student'}

@app.post('/api/login')
def login(body:Credentials,response:Response):
    with db() as c:
        row=c.execute('SELECT * FROM users WHERE username=?',(body.username,)).fetchone()
        if not row or not check_password(body.password,row['password']): raise HTTPException(401,'Sai thông tin đăng nhập')
        login_session(c,response,row['id'])
    return {'username':row['username'],'role':row['role']}

@app.post('/api/logout')
def logout(request:Request,response:Response):
    token=request.cookies.get('smartthpt_session')
    if token:
        with db() as c: c.execute('DELETE FROM sessions WHERE token=?',(token_hash(token),))
    response.delete_cookie('smartthpt_session'); return {'ok':True}

@app.get('/api/me')
def me(user=Depends(session_user)): return user

@app.get('/api/catalog')
def catalog(user=Depends(session_user)):
    with db() as c:
        return [dict(r) for r in c.execute('SELECT topic,COUNT(*) count FROM questions WHERE grade=12 AND subject=? GROUP BY topic ORDER BY topic',('Toán',))]

def public_question(row):
    return dict(id=row['id'],topic=row['topic'],prompt=row['prompt'],options=json.loads(row['options']),difficulty=row['difficulty'])

@app.post('/api/quizzes')
def create_quiz(body:QuizRequest,user=Depends(session_user)):
    if body.mode not in ('practice','exam'): raise HTTPException(400,'Chế độ không hợp lệ')
    with db() as c:
        sql='SELECT * FROM questions WHERE grade=12 AND subject=?'; args=['Toán']
        if body.topic: sql+=' AND topic=?';args.append(body.topic)
        pool=c.execute(sql,args).fetchall()
        if not pool: raise HTTPException(404,'Không có câu hỏi phù hợp')
        if body.mode=='exam' and len(pool)<body.count: raise HTTPException(400,'Không đủ câu hỏi')
        chosen=random.SystemRandom().sample(pool,min(body.count,len(pool)))
        qid=secrets.token_urlsafe(18); now=int(time.time()); deadline=now+body.count*90 if body.mode=='exam' else None
        c.execute('INSERT INTO quizzes VALUES(?,?,?,?,?,?,NULL)',(qid,user['id'],body.mode,json.dumps([r['id'] for r in chosen]),now,deadline))
    return {'id':qid,'mode':body.mode,'deadline':deadline,'questions':[public_question(r) for r in chosen]}

@app.post('/api/quizzes/{qid}/submit')
def submit(qid:str,body:Submission,user=Depends(session_user)):
    with db() as c:
        c.execute('BEGIN IMMEDIATE')
        quiz=c.execute('SELECT * FROM quizzes WHERE id=? AND user_id=?',(qid,user['id'])).fetchone()
        if not quiz: raise HTTPException(404,'Không tìm thấy bài làm')
        if quiz['submitted'] is not None: raise HTTPException(409,'Bài đã nộp')
        now=int(time.time())
        if quiz['deadline'] and now>quiz['deadline']+5: raise HTTPException(410,'Đã hết thời gian nộp bài')
        ids=json.loads(quiz['question_ids'])
        if any(i not in ids or v not in range(4) for i,v in body.answers.items()): raise HTTPException(400,'Đáp án không hợp lệ')
        results=[]
        for i in ids:
            r=c.execute('SELECT * FROM questions WHERE id=?',(i,)).fetchone(); selected=body.answers.get(i); correct=int(selected==r['answer'])
            c.execute('INSERT INTO responses VALUES(?,?,?,?)',(qid,i,selected,correct))
            results.append({**public_question(r),'selected':selected,'answer':r['answer'],'correct':bool(correct),'explanation':r['explanation'],'source':r['source']})
        c.execute('UPDATE quizzes SET submitted=? WHERE id=?',(now,qid))
    return {'score':round(10*sum(x['correct'] for x in results)/len(results),2),'results':results}

@app.get('/api/stats')
def stats(user=Depends(session_user)):
    with db() as c:
        topics=[dict(r) for r in c.execute('''SELECT q.topic,COUNT(*) total,SUM(r.correct) correct FROM responses r JOIN questions q ON q.id=r.question_id JOIN quizzes z ON z.id=r.quiz_id WHERE z.user_id=? GROUP BY q.topic''',(user['id'],))]
        history=[dict(r) for r in c.execute('''SELECT z.id,z.mode,z.submitted,COUNT(*) total,SUM(r.correct) correct FROM quizzes z JOIN responses r ON r.quiz_id=z.id WHERE z.user_id=? GROUP BY z.id ORDER BY z.submitted DESC LIMIT 20''',(user['id'],))]
    for t in topics: t['percent']=round(100*t['correct']/t['total'])
    for h in history: h['score']=round(10*h['correct']/h['total'],2)
    recommendations=sorted([t for t in topics if t['total']>=3],key=lambda t:(t['percent'],-t['total']))[:2]
    return {'topics':topics,'history':history,'recommendations':recommendations}

@app.get('/api/admin/summary')
def admin_summary(user=Depends(admin_user)):
    with db() as c:
        return {k:c.execute(sql).fetchone()[0] for k,sql in {'questions':'SELECT COUNT(*) FROM questions','students':"SELECT COUNT(*) FROM users WHERE role='student'",'submissions':'SELECT COUNT(*) FROM quizzes WHERE submitted IS NOT NULL'}.items()}

@app.post('/api/admin/classify')
def classify(body:ClassifyRequest,user=Depends(admin_user)):
    return {'topic':predict_topic(body.prompt),'experimental':True,'note':'TF-IDF + LinearSVC, huấn luyện trên câu mẫu; cần người duyệt.'}

@app.post('/api/admin/import')
def import_questions(body:ImportRequest,user=Depends(admin_user)):
    with db() as c: count=sum(insert_question(c,q.model_dump()) for q in body.questions)
    return {'inserted':count,'duplicates':len(body.questions)-count}

app.mount('/',StaticFiles(directory=ROOT/'static',html=True),name='static')
