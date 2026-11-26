# SmartTHPT — Ôn tập thông minh

MVP chạy local, có lý thuyết lớp 10–12 và bài luyện Toán 12. Đây là bản thử nghiệm kỹ thuật, không phải hệ thống thi chính thức.

Tài liệu phát triển gồm [PRD](docs/PRD.md) và [thiết kế hệ thống](docs/THIET_KE.md).

## 1. Khởi chạy trên Windows (VS Code / PowerShell)

Giải nén SmartTHPT.zip, mở thư mục SmartTHPT trong VS Code. Cần Python 3.11 hoặc 3.12 (64-bit).

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Nếu chỉ cài Python 3.11, thay `py -3.12` bằng `py -3.11`. Có thể dùng `python -m venv .venv` nếu lệnh `py` không có. Không cần kích hoạt venv hoặc đổi ExecutionPolicy. Nếu cổng 8000 đang bận, đổi sang 8001.

- Học sinh: http://127.0.0.1:8000 — bấm Tạo tài khoản, dùng tên đăng nhập không dấu, mật khẩu ít nhất 8 ký tự.
- Kiểm tra server: http://127.0.0.1:8000/api/health
- API Swagger: http://127.0.0.1:8000/docs
- Admin: mở terminal khác tại cùng thư mục, chạy:

```powershell
.\.venv\Scripts\python.exe -m app.manage create-admin admin
```

Nhập mật khẩu 2 lần (terminal không hiện ký tự khi gõ). Đăng xuất tài khoản học sinh, đăng nhập bằng admin, chọn Quản trị & ML. Không có mật khẩu mặc định. Dừng server bằng Ctrl+C.

## 2. Chức năng

- Tài khoản học sinh, đăng nhập, đăng xuất; phân quyền Admin.
- 60 câu hỏi tự biên soạn từ 12 mẫu toán, 6 chuyên đề, mỗi chuyên đề 10 câu. Tập dữ liệu nhỏ và nhiều biến thể tương tự, không đủ làm ngân hàng ôn thi hoàn chỉnh.
- Mục **Lý thuyết** chia lớp 10–12 theo hai khối. Môn chung gồm Toán, Ngữ văn, Tiếng Anh. Tự nhiên thêm Vật lí, Hoá học, Sinh học. Xã hội thêm Lịch sử, Địa lí, Giáo dục Kinh tế và Pháp luật. Đây là cách phân nhóm trong ứng dụng. Theo chương trình THPT sửa đổi năm 2022, Lịch sử có phần nội dung bắt buộc.
- Các bài ôn tự biên soạn theo mạch kiến thức, có thể khác tên và thứ tự từng bộ sách. Nguồn đối chiếu gồm [Thông tư 32/2018/TT-BGDĐT](https://vbpl.moj.gov.vn/bogiaoducdaotao/Pages/vbpq-toanvan.aspx?ItemID=146721), [chương trình chi tiết các môn](https://thphudinh.hcm.edu.vn/tin-tuc-su-kien/chuong-trinh-tong-the-va-chuong-trinh-chi-tiet-cac-mon-hoc-va-hoat-dong-giao-du/ctmb/21820/412126), [văn bản hợp nhất đến 2022](https://moet.gov.vn/content/vanban/Lists/VBPQ/Attachments/1483/vbhn-ttu-322018-202021-132022-ttbgddt.pdf) và [sửa đổi năm 2025](https://thuvienphapluat.vn/van-ban/giao-duc/Thong-tu-17-2025-TT-BGDDT-sua-doi-Thong-tu-32-2018-TT-BGDDT-Chuong-trinh-giao-duc-pho-thong-672806.aspx). Dữ liệu nằm trong `data/courses.json`.
- Luyện chuyên đề 10 câu, thi thử mini 10/20/30 câu có đồng hồ; chấm điểm phía server, xem lời giải.
- Lịch sử, tỷ lệ đúng theo chuyên đề, gợi ý hai chuyên đề cần ôn (ít nhất 3 lượt trả lời mỗi chuyên đề). Đây là thống kê và quy tắc, không phải ML dự đoán năng lực.
- Admin xem số lượng tài khoản, câu hỏi, bài đã nộp; thử phân loại câu hỏi bằng ML; nhập JSON tối đa 200 câu/lần, bỏ qua prompt trùng.
- Dữ liệu SQLite tự khởi tạo tại `data/smartthpt.sqlite3`, không yêu cầu PostgreSQL trong MVP. Cấu trúc câu hỏi lưu grade và subject, nhưng giao diện luyện tập hiện chỉ Toán 12.

## 3. Cấu trúc

```text
SmartTHPT/
  app/
    main.py       # API, DB, chấm điểm, thống kê, auth
    manage.py     # CLI tạo admin
    ml.py         # TF-IDF ký tự + LinearSVC
    seed.py       # Sinh câu hỏi mẫu
  static/
    index.html    # Giao diện
    style.css
    app.js
  data/
    questions.json # 60 câu gốc, có lời giải
    import_example.json # Mẫu cấu trúc nhập
  tests/
    test_app.py
  requirements.txt
  requirements-dev.txt
```

## 4. Nhập dữ liệu

Dùng file JSON mảng đối tượng hoặc đối tượng có key `questions`. Ví dụ trong `data/import_example.json`. Các trường `grade`, `subject`, `topic`, `prompt`, `options` (4 lựa chọn), `answer` (chỉ số 0=A,1=B,2=C,3=D), `explanation`, `difficulty`, `source`. Chỉ nhập nội dung đã kiểm tra đáp án, quyền sử dụng. Không tự động sao chép kho đề của bên thứ ba. Hiện chưa hỗ trợ PDF/Word, LaTeX, ảnh đề, câu đúng/sai hoặc trả lời ngắn.

## 5. Machine Learning

`app/ml.py` fit pipeline TF-IDF n-gram ký tự + LinearSVC trên 60 câu mẫu theo 6 nhãn. Admin nhập một câu để nhận chuyên đề đề xuất. Mô hình hiện không tự học từ JSON nhập thêm, không có đánh giá độc lập và không đưa ra xác suất tin cậy. Các câu cùng mẫu rất giống nhau nên không nên chia ngẫu nhiên theo từng biến thể để báo cáo độ chính xác; khi xây dữ liệu thực tế hãy chia theo họ câu hỏi/nguồn và có tập kiểm thử độc lập.

Các bước sau: xây bộ dữ liệu có nhãn do giáo viên kiểm duyệt, so sánh Naive Bayes/Logistic Regression/SVM (macro-F1, confusion matrix, phân tách theo nguồn), ghi lại phiên bản mô hình; sau đó thu thập lịch sử làm bài với cơ chế bảo vệ dữ liệu học sinh trước khi nghiên cứu mô hình dự đoán đúng/sai, mức độ thành thạo hoặc điểm thi.

## 6. Kiểm thử

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Kiểm thử API tự động dùng database tạm, không sửa dữ liệu thật. Kiểm tra đăng ký, phân quyền, danh mục, tạo bài, không lộ đáp án trước nộp, chấm điểm, chống nộp lại, thống kê, đăng nhập admin, phân loại, nhập JSON và tính duy nhất câu hỏi.

## 7. Giới hạn trước khi triển khai công khai

MVP chỉ chạy localhost. Chưa có rate limiting, xác minh/khôi phục tài khoản, cơ chế xóa/xuất dữ liệu học sinh, sao lưu, giám sát, quy trình kiểm duyệt đầy đủ, thanh toán, VIP, đăng ký phụ huynh, HTTPS triển khai hay kiểm thử an ninh. Không mở Cloudflare Tunnel cho bản này như một dịch vụ công khai. Cần rà soát quyền riêng tư trẻ em, bản quyền đề, thêm bảo mật, chuyển PostgreSQL nếu cần mở rộng và kiểm thử tải. Đề mini chưa theo cấu trúc đề thi chính thức, chưa có đầy đủ các dạng câu hỏi.
