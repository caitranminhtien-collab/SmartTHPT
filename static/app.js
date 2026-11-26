'use strict';
const $=s=>document.querySelector(s), main=$('#main');
let user=null, currentQuiz=null, answers={}, interval=null, submitting=false, generation=0;
const e=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function api(path,method='GET',body){const r=await fetch('/api'+path,{method,headers:{'Content-Type':'application/json'},...(body!==undefined?{body:JSON.stringify(body)}:{})});const x=await r.json();if(!r.ok)throw Error(typeof x.detail==='string'?x.detail:JSON.stringify(x.detail));return x;}
function message(err){const t=$('#message');if(t)t.textContent=err.message||err;}
function stopTimer(){if(interval)clearInterval(interval);interval=null;}
function nav(){ $('#sidebar').hidden=!user;$('#adminNav').hidden=user?.role!=='admin';$('#account').innerHTML=user?`<span class="account-name">${e(user.username)} · </span><button class="secondary" id="logout">Đăng xuất</button>`:'';if(user)$('#logout').onclick=async()=>{try{await api('/logout','POST');user=null;currentQuiz=null;stopTimer();generation++;nav();auth();}catch(err){message(err);}};}
function auth(register=false){main.innerHTML=`<section class="auth"><div class="eyebrow">BẮT ĐẦU HỌC TẬP</div><h1>Tiến bộ từng ngày.</h1><p class="muted">Luyện tập theo chuyên đề, theo dõi kết quả và cải thiện kiến thức Toán 12.</p><div class="card"><h2>${register?'Tạo tài khoản':'Đăng nhập'}</h2><form id="authForm"><label>Tên đăng nhập<input name="username" required minlength="3" maxlength="32" pattern="[a-zA-Z0-9_.\\-]+" autocomplete="username" placeholder="hocsinh12"></label><label>Mật khẩu<input type="password" name="password" required minlength="8" autocomplete="${register?'new-password':'current-password'}" placeholder="Ít nhất 8 ký tự"></label><button>${register?'Đăng ký':'Đăng nhập'}</button> <button type="button" class="secondary" id="toggle">${register?'Đã có tài khoản':'Tạo tài khoản'}</button><p id="message" class="error"></p></form></div></section>`;$('#toggle').onclick=()=>auth(!register);$('#authForm').onsubmit=async ev=>{ev.preventDefault();try{user=await api(register?'/register':'/login','POST',Object.fromEntries(new FormData(ev.target)));nav();page('home');}catch(err){message(err);}};}
async function page(name){if(!user)return;if(currentQuiz&&!confirm('Rời bài làm? Bài chưa nộp sẽ không được lưu kết quả.'))return;currentQuiz=null;stopTimer();const g=++generation;document.querySelectorAll('[data-page]').forEach(b=>b.classList.toggle('active',b.dataset.page===name));main.innerHTML='<p class="muted">Đang tải…</p>';try{let data;if(name==='home'||name==='practice')data=await api('/catalog');if(name==='lessons')data=await api('/v1/courses');if(name==='stats')data=await api('/stats');if(name==='admin')data=await api('/admin/summary');if(g!==generation)return;if(name==='home')home(data);else if(name==='practice')practice(data);else if(name==='lessons')lessons(data);else if(name==='exam')exam();else if(name==='stats')stats(data);else if(name==='admin')admin(data);}catch(err){if(g===generation)main.innerHTML=`<p class="error">${e(err.message)}</p>`;}}
function home(data){main.innerHTML=`<section class="hero"><div class="eyebrow">TOÁN 12 · PHIÊN BẢN THỬ NGHIỆM</div><h1>Học đúng phần.<br>Tiến bộ đúng hướng.</h1><p>Ôn tập theo chuyên đề, thi thử mini và xem lại từng câu sai để cải thiện kết quả.</p><div class="actions"><button id="practiceBtn">Bắt đầu luyện tập</button><button class="secondary" id="examBtn">Thi thử mini</button></div></section><div class="grid"><div class="card"><div class="label">Ngân hàng câu hỏi</div><div class="metric">${data.reduce((a,x)=>a+x.count,0)}</div><p class="muted">Câu hỏi tự biên soạn</p></div><div class="card"><div class="label">Chuyên đề</div><div class="metric">${data.length}</div><p class="muted">Toán lớp 12</p></div><div class="card"><div class="label">Phân tích</div><h2>Học từ câu sai</h2><p class="muted">Gợi ý theo kết quả thực tế</p></div></div><h2>Khám phá chuyên đề</h2><div class="grid">${data.map(x=>`<article class="card"><h3>${e(x.topic)}</h3><p class="muted">${x.count} câu hỏi</p></article>`).join('')}</div>`;$('#practiceBtn').onclick=()=>page('practice');$('#examBtn').onclick=()=>page('exam');}
const commonSubjects = ['Toán', 'Ngữ văn', 'Tiếng Anh'];
const subjectGroups = {
    natural: ['Vật lí', 'Hoá học', 'Sinh học'],
    social: ['Lịch sử', 'Địa lí', 'Giáo dục Kinh tế và Pháp luật'],
};

function lessons(courses) {
    main.innerHTML = `
        <h1>Lý thuyết THPT</h1>
        <p class="muted">Tóm tắt kiến thức trọng tâm theo Chương trình GDPT 2018.</p>
        <section class="card">
            <div class="grid">
                <label>Lớp<select id="lessonGrade">
                    <option value="10">Lớp 10</option>
                    <option value="11">Lớp 11</option>
                    <option value="12">Lớp 12</option>
                </select></label>
                <label>Khối<select id="lessonGroup">
                    <option value="natural">Tự nhiên</option>
                    <option value="social">Xã hội</option>
                </select></label>
                <label>Môn học<select id="lessonSubject"></select></label>
            </div>
            <p class="muted">Hai khối dùng để lọc nội dung trong SmartTHPT. Lịch sử nằm ở nhóm Xã hội trong bộ lọc.</p>
        </section>
        <div id="lessonContent" aria-live="polite"></div>
        <p class="muted"><a href="https://taphuan.nxbgd.vn">Sách giáo khoa điện tử của NXB Giáo dục Việt Nam</a> · <a href="https://ipub.nxbgd.vn/bai-viet/nha-xuat-ban-giao-duc-viet-nam-thong-bao-ve-viec-su-dung-sach-giao-khoa-nam-hoc-2026-2027">Danh mục sách cập nhật 2026–2027</a></p>`;

    const grade = $('#lessonGrade');
    const group = $('#lessonGroup');
    const subject = $('#lessonSubject');
    const content = $('#lessonContent');

    function renderCourse() {
        const course = courses.find(item =>
            item.grade === Number(grade.value) && item.subject === subject.value);
        if (!course) {
            content.textContent = 'Chưa có bài học cho lựa chọn này.';
            return;
        }
        const allLessons = course.chapters.flatMap(chapter => chapter.topics.flatMap(topic => topic.lessons));
        const milestones = new Map();
        (course.assessments || []).forEach((exam, index) => {
            const end = Math.ceil(allLessons.length * (index + 1) / 4);
            milestones.set(allLessons[end - 1], exam);
        });
        content.innerHTML = `
            <h2>Lớp ${e(course.grade)} · ${e(course.subject)}</h2>
            <p class="muted">Bài tự kiểm tra do SmartTHPT biên soạn. Bốn mốc đề tham khảo chia theo tiến độ ôn tập của ứng dụng. Phạm vi kiểm tra thực tế theo kế hoạch của trường.</p>
            <p class="muted">${e(course.alignment ?? "Tổng quan theo mạch kiến thức")}</p>
            ${course.chapters.map((chapter, index) => `
                <details class="card lesson-chapter" ${index === 0 ? 'open' : ''}>
                    <summary>${e(chapter.title)}</summary>
                    ${chapter.topics.flatMap(topic => topic.lessons).map(lesson => `
                        <details class="lesson-entry">
                            <summary>${e(lesson.title)}</summary>
                            <p>${e(lesson.summary)}</p>
                            ${lessonFields(lesson)}
                            ${lessonTest(lesson, allLessons)}
                        </details>${milestones.has(lesson) ? termExam(milestones.get(lesson)) : ''}`).join('')}
                </details>`).join('')}`;
    }

    function renderSubjects() {
        const previous = subject.value;
        const options = [...commonSubjects, ...subjectGroups[group.value]];
        subject.replaceChildren(...options.map(name => new Option(name, name)));
        if (options.includes(previous)) subject.value = previous;
        renderCourse();
    }

    content.onsubmit = event => {
        const form = event.target;
        if (!form.matches('.lesson-check')) return;
        event.preventDefault();
        const correct = new FormData(form).get('knowledge') === 'yes';
        form.querySelector('.check-score').textContent = correct
            ? 'Nhận biết: đúng (1/1). Phần vận dụng tự đối chiếu.'
            : 'Nhận biết: chưa đúng (0/1). Phần vận dụng tự đối chiếu.';
        form.querySelector('.check-feedback').hidden = false;
    };
    grade.onchange = renderCourse;
    group.onchange = renderSubjects;
    subject.onchange = renderCourse;
    renderSubjects();
}

function lessonTest(lesson, allLessons) {
    const statements = allLessons.filter(item => item !== lesson && item.summary !== lesson.summary);
    const index = allLessons.indexOf(lesson);
    const alternatives = [lesson, statements[index % statements.length],
        statements[(index + 1) % statements.length]];
    const ordered = alternatives.slice(index % 3).concat(alternatives.slice(0, index % 3));
    return `<details class="card"><summary>Tự kiểm tra sau bài học</summary>
        <form class="lesson-check">
            <fieldset><legend>Chọn kiến thức phù hợp nhất với bài vừa học.</legend>
            ${ordered.map(item => `<label class="option"><input required type="radio" name="knowledge"
              value="${item === lesson ? 'yes' : 'no'}"><span>${e(item.summary)}</span></label>`).join('')}</fieldset>
            <label>Giải thích cách áp dụng kiến thức của bài vào một ví dụ cụ thể.
              <textarea name="application" required></textarea></label>
            <button>Nộp bài tự kiểm tra</button>
            <div class="check-feedback" hidden aria-live="polite">
              <p class="check-score"></p><p><strong>Kiến thức cần nhớ.</strong> ${e(lesson.rule || lesson.summary)}</p>
              <p><strong>Ví dụ để tự đối chiếu phần vận dụng.</strong> ${e(lesson.example)}</p>
            </div>
        </form></details>`;
}

function termExam(exam) {
    if (!exam.url) return `<section class="card"><h3>${e(exam.title)}</h3><p>Chưa có đề đã xác minh cho môn này.</p></section>`;
    return `<section class="card"><h3>${e(exam.title)}</h3>
        <p>${e(exam.publisher)} · Năm học ${e(exam.year)}</p>
        <a href="${e(exam.url)}" target="_blank" rel="noopener">${e(exam.linkLabel || 'Xem đề và đáp án trên trang trường')}</a>
        ${exam.file ? ` · <a href="${e(exam.file)}" target="_blank" rel="noopener">Các mã đề của môn</a>` : ''}</section>`;
}

function lessonFields(lesson) {
    return [
        ['Quy tắc', lesson.rule],
        ['Ví dụ', lesson.example],
        ['Lỗi thường gặp', lesson.pitfall],
    ].filter(([, value]) => value).map(([label, value]) =>
        `<p><strong>${label}.</strong> ${e(value)}</p>`).join('');
}
function practice(data){main.innerHTML=`<div class="eyebrow">LUYỆN TẬP</div><h1>Chọn chuyên đề</h1><p class="muted">Không giới hạn thời gian. Xem đáp án và giải thích sau khi nộp.</p><div class="grid">${data.map((x,i)=>`<div class="card"><h2>${e(x.topic)}</h2><p class="muted">${x.count} câu hỏi</p><button data-topic-index="${i}">Luyện 10 câu</button></div>`).join('')}</div><p id="message" class="error"></p>`;document.querySelectorAll('[data-topic-index]').forEach(b=>b.onclick=()=>startQuiz('practice',data[Number(b.dataset.topicIndex)].topic,10));}
function exam(){main.innerHTML=`<div class="eyebrow">KIỂM TRA</div><h1>Thi thử mini</h1><div class="card"><h2>Toán 12 · Trắc nghiệm</h2><p>Bài kiểm tra mẫu, chưa mô phỏng đầy đủ cấu trúc đề tốt nghiệp THPT. Mỗi câu có một đáp án đúng.</p><label>Số câu<select id="count"><option value="10">10 câu · 15 phút</option><option value="20">20 câu · 30 phút</option><option value="30">30 câu · 45 phút</option></select></label><button id="start">Bắt đầu</button><p id="message" class="error"></p></div>`;$('#start').onclick=()=>startQuiz('exam',null,Number($('#count').value));}
async function startQuiz(mode,topic,count){const g=generation;try{const q=await api('/quizzes','POST',{mode,topic,count});if(g!==generation)return;currentQuiz=q;answers={};renderQuiz();}catch(err){message(err);}}
function renderQuiz(){const q=currentQuiz;main.innerHTML=`<div class="quiz-top"><h2>${q.mode==='exam'?'Thi thử mini':'Luyện tập'}</h2><div><span id="progress">0/${q.questions.length}</span> <span class="timer" id="timer"></span></div></div>${q.questions.map((x,i)=>`<section class="card"><div class="eyebrow">CÂU ${i+1} · ${e(x.topic)} · ${e(x.difficulty)}</div><h3>${e(x.prompt)}</h3><div class="options">${x.options.map((o,j)=>`<label class="option"><input type="radio" name="q${x.id}" data-q="${x.id}" value="${j}"><span>${'ABCD'[j]}. ${e(o)}</span></label>`).join('')}</div></section>`).join('')}<button id="submit">Nộp bài</button><p id="message" class="error"></p>`;main.querySelectorAll('input[type=radio]').forEach(b=>b.onchange=()=>{answers[b.dataset.q]=Number(b.value);$('#progress').textContent=`${Object.keys(answers).length}/${q.questions.length}`;});$('#submit').onclick=()=>submitQuiz(false);if(q.deadline){const tick=()=>{const s=Math.max(0,q.deadline-Math.floor(Date.now()/1000));if($('#timer'))$('#timer').textContent=` · ${Math.floor(s/60)}:${String(s%60).padStart(2,'0')}`;if(s===0){stopTimer();submitQuiz(true);}};interval=setInterval(tick,1000);tick();}}
async function submitQuiz(auto){if(!currentQuiz||submitting)return;const q=currentQuiz; if(!auto&&Object.keys(answers).length<q.questions.length&&!confirm('Bạn còn câu chưa trả lời. Vẫn nộp bài?'))return;submitting=true;$('#submit').disabled=true;try{const result=await api('/quizzes/'+q.id+'/submit','POST',{answers});if(currentQuiz!==q)return;stopTimer();currentQuiz=null;showResults(result);}catch(err){message(err);if($('#submit'))$('#submit').disabled=false;}finally{submitting=false;}}
function showResults(r){main.innerHTML=`<section class="hero"><div class="eyebrow">KẾT QUẢ BÀI LÀM</div><h1>${r.score}/10 điểm</h1><p>Đúng ${r.results.filter(x=>x.correct).length}/${r.results.length} câu.</p><button id="statsBtn">Xem phân tích năng lực</button></section>${r.results.map((x,i)=>`<section class="card"><div class="eyebrow">CÂU ${i+1} · ${x.correct?'ĐÚNG':'CHƯA ĐÚNG'}</div><h3>${e(x.prompt)}</h3><div class="options">${x.options.map((o,j)=>`<div class="option ${j===x.answer?'good':j===x.selected?'bad':''}">${'ABCD'[j]}. ${e(o)} ${j===x.answer?' · Đáp án đúng':''}${j===x.selected?' · Bạn chọn':''}</div>`).join('')}</div><p class="result-line"><strong>Giải thích:</strong> ${e(x.explanation)}</p><small class="muted">Nguồn: ${e(x.source)}</small></section>`).join('')}`;$('#statsBtn').onclick=()=>page('stats');}
function stats(data){main.innerHTML=`<div class="eyebrow">DỮ LIỆU HỌC TẬP</div><h1>Phân tích năng lực</h1><p class="muted">Tỷ lệ trả lời đúng từ lịch sử làm bài; không phải điểm dự báo của mô hình ML.</p><div class="grid"><section class="card"><h2>Kết quả theo chuyên đề</h2>${data.topics.length?data.topics.map(t=>`<div class="stat-line"><span>${e(t.topic)}</span><strong>${t.percent}%</strong></div><div class="bar"><i style="width:${t.percent}%"></i></div><p class="label">${t.correct}/${t.total} lượt đúng</p>`).join(''):'<p>Chưa có dữ liệu. Hãy hoàn thành một bài tập.</p>'}</section><section class="card"><h2>Gợi ý ôn tập</h2>${data.recommendations.length?data.recommendations.map((t,i)=>`<p><strong>${e(t.topic)}</strong> · ${t.percent}% đúng</p><button class="secondary" data-recommend="${i}">Luyện thêm</button>`).join(''):'<p>Cần ít nhất 3 lượt trả lời ở một chuyên đề để tạo gợi ý.</p>'}<p class="label">Gợi ý theo quy tắc ưu tiên tỷ lệ đúng thấp, chưa cá nhân hóa bằng ML.</p></section></div><section class="card"><h2>Lịch sử luyện tập</h2><table class="history"><thead><tr><th>Ngày</th><th>Chế độ</th><th>Đúng</th><th>Điểm</th></tr></thead><tbody>${data.history.map(h=>`<tr><td>${e(new Date(h.submitted*1000).toLocaleDateString('vi-VN'))}</td><td>${h.mode==='exam'?'Thi thử':'Luyện tập'}</td><td>${h.correct}/${h.total}</td><td>${h.score}</td></tr>`).join('')}</tbody></table></section><p id="message" class="error"></p>`;main.querySelectorAll('[data-recommend]').forEach(b=>b.onclick=()=>startQuiz('practice',data.recommendations[Number(b.dataset.recommend)].topic,10));}
function admin(d){main.innerHTML=`<div class="eyebrow">QUẢN TRỊ</div><h1>Ngân hàng câu hỏi & ML</h1><div class="grid">${[['Câu hỏi',d.questions],['Tài khoản học sinh',d.students],['Bài đã nộp',d.submissions]].map(x=>`<div class="card"><div class="label">${x[0]}</div><div class="metric">${x[1]}</div></div>`).join('')}</div><section class="card"><h2>ML01 · Phân loại chuyên đề</h2><p class="muted">TF-IDF + LinearSVC. Mô hình thử nghiệm chỉ huấn luyện từ câu mẫu; quản trị viên phải kiểm tra kết quả.</p><label>Câu hỏi<textarea id="prompt" placeholder="Tính tích phân của hàm số..."></textarea></label><button id="predict">Phân loại</button><p id="prediction" role="status"></p></section><section class="card"><h2>Nhập ngân hàng câu hỏi JSON</h2><p class="muted">Tối đa 200 câu/lần. Chỉ nhập câu hỏi đã kiểm tra đáp án, lời giải và quyền sử dụng. Mục answer đánh số 0–3.</p><input id="file" type="file" accept=".json,application/json"><label><input id="review" type="checkbox" style="width:auto"> Tôi đã kiểm tra nội dung và quyền sử dụng.</label><div class="actions"><button id="import">Nhập câu hỏi</button></div><p id="message" role="status"></p></section>`;$('#predict').onclick=async()=>{try{const r=await api('/admin/classify','POST',{prompt:$('#prompt').value});$('#prediction').textContent='Chuyên đề đề xuất: '+r.topic;}catch(err){$('#prediction').textContent=err.message;}};$('#import').onclick=async()=>{try{if(!$('#review').checked)throw Error('Cần xác nhận đã kiểm duyệt.');const f=$('#file').files[0];if(!f)throw Error('Chọn file JSON.');const j=JSON.parse(await f.text());const r=await api('/admin/import','POST',{questions:Array.isArray(j)?j:j.questions});$('#message').textContent=`Đã nhập ${r.inserted} câu; trùng ${r.duplicates} câu. Tải lại trang quản trị để cập nhật số lượng.`;}catch(err){message(err);}};}
document.querySelectorAll('[data-page]').forEach(b=>b.onclick=()=>page(b.dataset.page));
(async()=>{try{user=await api('/me');nav();page('home');}catch{nav();auth();}})();
