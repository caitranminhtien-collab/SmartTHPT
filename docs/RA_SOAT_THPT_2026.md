# Rà soát SmartTHPT · 26/11/2026

Cơ sở là main tại commit 145a7be. Mã hiện tại dùng FastAPI, SQLite và JavaScript tĩnh.

| Phần | Kết quả rà soát |
|---|---|
| Giao diện | Đã thay bộ lọc hai khối bằng các nhóm Bắt buộc, Lựa chọn và Tự chọn. Danh mục và nguồn lấy từ API. |
| API và phân quyền | Danh mục dùng phiên đăng nhập. Bài nộp truy vấn theo người sở hữu. Nhập ngân hàng cần quyền admin. API quản lý học liệu và CRUD đầy đủ vẫn thiếu. |
| SQLite | Giữ bảng hiện tại, bổ sung chỉ mục cho hạn phiên, danh mục câu hỏi và lịch sử làm bài. Câu hỏi chưa có khoá liên kết đến bài học. |
| Bài tập và chấm điểm | Bài luyện có lưu điểm và lịch sử, hiện chỉ lấy ngân hàng Toán 12. Tự kiểm tra cuối bài chạy trong trình duyệt và chưa lưu tiến độ. Chưa có ngân hàng đủ dạng và bốn mức cho từng bài. |
| Nội dung | 27 tổ hợp có học liệu ôn tập do AI biên soạn. Toán 12 và Vật lí 11 đã được đối chiếu mục lục tham khảo. Yêu cầu cần đạt, học liệu các môn còn thiếu và các cụm chuyên đề cần rà theo từng lớp và từng văn bản. |
| Đề định kỳ | Liên kết nguồn nhà trường theo năm cụ thể. Mốc hiển thị dựa trên tiến độ ôn của ứng dụng, chưa được ánh xạ theo phân phối chương trình của từng trường. |

## Căn cứ đã tra

- Thông tư 32/2018/TT-BGDĐT được sử dụng cùng các sửa đổi. Thông tư 20/2021 sửa Điều 3; Thông tư 13/2022 sửa chương trình tổng thể và Lịch sử. Khung THPT có 4 môn lựa chọn và 3 cụm chuyên đề ở mỗi lớp. [Văn bản hợp nhất và chương trình tổng thể](https://moet.gov.vn/content/vanban/Lists/VBPQ/Attachments/1483/vbhn-chuong-trinh-tong-the.pdf)
- Thông tư 17/2025/TT-BGDĐT cập nhật một số chương trình môn học, có phần áp dụng cho Lịch sử 10, Giáo dục kinh tế và pháp luật 10, Địa lí 12. [Thông tư và phụ lục](https://vanban.chinhphu.vn/?classid=1&docid=215347&pageid=27160)
- Công văn 5208 ngày 07/08/2026 hướng dẫn triển khai năm học 2026–2027. [Toàn văn trên Cổng Chính phủ](https://xaydungchinhsach.chinhphu.vn/cong-van-so-5208-bgddt-gdpt-huong-dan-thuc-hien-nhiem-vu-giao-duc-pho-thong-nam-hoc-2026-2027-119260808110247193.htm)
