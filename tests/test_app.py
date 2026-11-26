import tempfile
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from app import main
from app.seed import make_questions

class TestApp(unittest.TestCase):
    def test_full_flow(self):
        with tempfile.TemporaryDirectory() as temp:
            original=main.DB;main.DB=Path(temp)/'test.sqlite3'
            try:
                with TestClient(main.app) as client:
                    self.assertEqual(client.get('/').status_code,200)
                    health = client.get('/api/health')
                    self.assertEqual(health.status_code, 200)
                    self.assertEqual(health.json(), {'status': 'ok'})
                    self.assertEqual(client.get('/api/catalog').status_code,401)
                    self.assertEqual(client.get('/api/v1/courses').status_code, 401)
                    self.assertEqual(client.post('/api/register',json={'username':'student1','password':'testpass123'}).status_code,200)
                    cat=client.get('/api/catalog').json();self.assertEqual(sum(x['count'] for x in cat),60)
                    courses = client.get('/api/v1/courses')
                    self.assertEqual(courses.status_code, 200)
                    course, = courses.json()
                    self.assertEqual((course['grade'], course['subject']), (12, 'Toán'))
                    self.assertEqual(len(course['chapters']), 3)
                    topics = [topic for chapter in course['chapters'] for topic in chapter['topics']]
                    self.assertTrue(set(t['title'] for t in topics) <= {row['topic'] for row in cat})
                    for topic in topics:
                        self.assertTrue(topic['lessons'])
                        for lesson in topic['lessons']:
                            self.assertTrue(lesson['example'])
                    self.assertEqual(client.get('/api/admin/summary').status_code,403)
                    q=client.post('/api/quizzes',json={'mode':'practice','topic':cat[0]['topic'],'count':10}).json()
                    self.assertEqual(len(q['questions']),10);self.assertNotIn('answer',q['questions'][0])
                    with main.db() as c: answers={x['id']:c.execute('SELECT answer FROM questions WHERE id=?',(x['id'],)).fetchone()[0] for x in q['questions']}
                    r=client.post(f"/api/quizzes/{q['id']}/submit",json={'answers':answers});self.assertEqual(r.status_code,200);self.assertEqual(r.json()['score'],10)
                    self.assertEqual(client.post(f"/api/quizzes/{q['id']}/submit",json={'answers':answers}).status_code,409)
                    self.assertEqual(client.get('/api/stats').json()['topics'][0]['percent'],100)
                    exam=client.post('/api/quizzes',json={'mode':'exam','count':10}).json();self.assertIsNotNone(exam['deadline'])
                    self.assertEqual(client.post('/api/logout').status_code,200)
                    self.assertEqual(client.get('/api/me').status_code,401)
                    with main.db() as c:c.execute("INSERT INTO users(username,password,role) VALUES(?,?,'admin')",('admin',main.hash_password('securepass123')))
                    self.assertEqual(client.post('/api/login',json={'username':'admin','password':'securepass123'}).status_code,200)
                    self.assertEqual(client.get('/api/admin/summary').json()['questions'],60)
                    self.assertEqual(client.post('/api/admin/classify',json={'prompt':'Tính tích phân từ 0 đến 2 của hàm số 2x.'}).json()['topic'],'Nguyên hàm – tích phân')
                    self.assertEqual(client.post('/api/admin/import',json={'questions':make_questions()[:1]}).json()['duplicates'],1)
                    item=dict(make_questions()[0],prompt='Câu hỏi kiểm thử thêm mới')
                    self.assertEqual(client.post('/api/admin/import',json={'questions':[item]}).json()['inserted'],1)
            finally:main.DB=original
    def test_questions(self):
        rows=make_questions();self.assertEqual(len(rows),60);self.assertEqual(len(set(r['prompt'] for r in rows)),60)
        for r in rows:self.assertEqual(len(set(r['options'])),4);self.assertIn(r['answer'],range(4))
if __name__=='__main__':unittest.main()
