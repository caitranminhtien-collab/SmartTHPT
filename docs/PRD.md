# PRD SmartTHPT v0.1

## 1. Mục tiêu và người dùng

SmartTHPT giúp học sinh lớp 10–12 ôn theo chương, luyện tập, thi thử và biết nên học gì tiếp theo. Bản đầu triển khai Toán 12. Danh mục lớp → môn → chương → chuyên đề có thể mở rộng bằng dữ liệu. Giáo viên hoặc biên tập viên soạn và rà soát câu hỏi. Admin quản lý quyền, xuất bản và vận hành. Vai trò biên tập viên là đề xuất cho giai đoạn quản trị nội dung.

## 2. Phạm vi và tiêu chí nghiệm thu

| ID | Người dùng và yêu cầu | Điều kiện nghiệm thu | Giai đoạn |
|---|---|---|---|
| UC01 | Học sinh đăng ký, đăng nhập, đăng xuất | Tài khoản trùng được báo rõ, phiên hết hạn bị từ chối, học sinh chỉ đọc được dữ liệu của mình | MVP |
| UC02 | Học sinh mở lý thuyết theo chương | Chọn lớp/môn/chương, xem bài đã xuất bản và công thức KaTeX | MVP |
| UC03 | Học sinh luyện theo chuyên đề | Chọn chủ đề, API cấp câu hỏi theo bộ lọc, kiểm tra thiếu câu và giữ phiên đang làm | MVP |
| UC04 | Học sinh thi thử Toán 12 | Lưu phiên bản đề và quy tắc tính điểm, hạn nộp theo server. Hỗ trợ chọn đáp án, đúng/sai và trả lời ngắn trước khi gọi là đề mô phỏng đầy đủ | MVP theo hai đợt: mini rồi đầy đủ |
| UC05 | Học sinh nộp và xem giải | Nộp lặp trả lại kết quả đã lưu, xem điểm và lời giải sau khi nộp, đáp án ẩn trong lúc làm | MVP |
| UC06 | Biên tập viên nhập và quản lý ngân hàng | JSON → PDF/Word. Có xem trước, báo lỗi theo dòng/trang, ghi nguồn và căn cứ sử dụng, rà soát đáp án/công thức rồi mới xuất bản | MVP JSON, PDF/Word sau MVP |
| UC07 | Học sinh xem tiến độ và lộ trình | Hiển thị số mẫu và tỷ lệ đúng theo chủ đề. Khi thiếu dữ liệu, hướng dẫn làm bài chẩn đoán. Gợi ý dẫn đến bài học hoặc bài luyện cụ thể | MVP theo quy tắc, ML sau |
| UC08 | Học sinh xem dự đoán điểm | Chỉ bật sau đánh giá độc lập. Hiển thị phạm vi dự đoán, thời điểm và phiên bản mô hình, trạng thái chưa đủ dữ liệu | Sau khi có dữ liệu |
| UC09 | Admin quản trị nội dung và tài khoản | Quyền kiểm tra tại server, xuất bản và thay đổi vai trò có audit, khóa tài khoản thu hồi phiên | MVP |
| UC10 | Học sinh mua VIP | Xem quyền lợi và giá, xác nhận giao dịch từ nhà cung cấp, xử lý thông báo lặp đúng một lần, đối soát và hỗ trợ hoàn tiền | Sau MVP |

### Hành vi chi tiết

- Nội dung dùng trạng thái nháp, chờ duyệt, đã xuất bản, đã lưu trữ. Câu đã từng dùng giữ phiên bản cũ để xem lại bài làm.
- Khởi tạo bài thất bại nếu ngân hàng thiếu câu phù hợp. Server xác nhận người sở hữu, hạn nộp và kiểu đáp án. Bài hết hạn xử lý theo chính sách đã công bố trên đề.
- PDF/Word vào khu vực tạm. Nội dung trích xuất và câu có ảnh hoặc công thức được kiểm tra thủ công trước khi xuất bản. JSON có phiên bản schema và báo mục trùng. Nhập lại một lô không nhân đôi câu.
- Lộ trình theo quy tắc dựa vào tỷ lệ đúng và số lần làm. Mỗi gợi ý hiển thị lý do. Học sinh có thể mở lại lịch sử và tiếp tục từ chủ đề đề xuất.
- Mức giá, quyền lợi VIP và nhà cung cấp thanh toán sẽ được chốt trước khi triển khai UC10. Quyền truy cập được kiểm tra từ tài khoản phía server.

## 3. Chất lượng, dữ liệu và bảo mật

- Ưu tiên nội dung tự biên soạn hoặc có căn cứ quyền sử dụng. Lưu tác giả, nguồn, giấy phép/phạm vi, bằng chứng và người duyệt. Giữ tệp gốc riêng theo quyền.
- Thu tối thiểu dữ liệu định danh. Tách dữ liệu tài khoản khỏi dữ liệu thử nghiệm, dùng mã học sinh giả danh. Chốt quy trình đồng ý phù hợp với độ tuổi, thời hạn lưu, xuất/xóa dữ liệu trước pilot có học sinh thật.
- Trước pilot, kiểm thử phân quyền theo đối tượng, quản lý phiên, giới hạn đăng nhập và tải tệp, khôi phục sao lưu, ghi nhật ký thao tác quản trị. Dùng HTTPS và bí mật ngoài Git. Nhật ký không chứa mật khẩu, token, bài làm hoặc tệp gốc.
- Kiểm thử trọn luồng từ đăng nhập đến xem bài đã chấm, cả trên màn hình điện thoại. Bài làm ổn định khi gửi lại yêu cầu. Đặt ngưỡng hiệu năng dựa vào tải pilot đo được, ghi rõ cấu hình khi báo cáo độ trễ.
- Theo dõi hoàn thành bài luyện, quay lại học, thời gian từ mở bài đến nộp, tỷ lệ lỗi chấm, tỷ lệ câu phải sửa sau duyệt và độ phủ dữ liệu theo chuyên đề. Đo đường cơ sở trong pilot trước khi đặt chỉ tiêu.

## 4. Kế hoạch ML

| Bài toán | Nhãn và cách chia | Baseline và ứng viên | Đánh giá |
|---|---|---|---|
| Gợi ý nhãn câu hỏi | Nhãn được duyệt, giữ các biến thể cùng họ đề trong một nhóm khi chia, giữ riêng nguồn kiểm thử đủ điều kiện | Luật/từ khóa, TF-IDF + Logistic Regression, LinearSVC | Macro-F1, F1 từng nhãn, confusion matrix |
| Dự đoán trả lời đúng | Chỉ dùng dữ liệu trước thời điểm trả lời, chia theo thời gian và đánh giá riêng trên học sinh chưa gặp | Tỷ lệ đúng có làm trơn, Logistic Regression, XGBoost | Log loss, Brier score, độ hiệu chuẩn, độ phủ |
| Dự đoán điểm | Điểm của bài thi chuẩn hóa diễn ra sau thời điểm dự đoán, dùng điểm thi thật chỉ khi có dữ liệu và quyền sử dụng phù hợp | Trung bình điểm trước đó, hồi quy, XGBoost. Cân nhắc PyTorch khi quy mô dữ liệu hợp lý | MAE, RMSE, sai số theo nhóm đủ mẫu, tỷ lệ bao phủ khoảng dự đoán |

Ghi run ID, Git SHA, phiên bản và hash dữ liệu, chính sách chia, seed, cấu hình, kích thước và phân bố mẫu, metrics, ablation trên cùng cách chia, confusion matrix hoặc đồ thị sai số, file mô hình và thời điểm đánh giá. Tập kiểm thử chỉ dùng đánh giá cuối. Mỗi ablation thay một nhóm đặc trưng hoặc một lựa chọn mô hình. Dữ liệu định danh và bản ghi làm bài thô lưu ngoài Git. Khi dữ liệu chưa đạt, báo trạng thái chưa đủ dữ liệu. Mô hình phân loại câu mẫu trong nguyên mẫu chỉ minh họa kỹ thuật.

## 5. Mốc bàn giao

1. Nhập nguyên mẫu và chạy lại kiểm thử. Lưu PRD và sơ đồ làm mốc thiết kế.
2. Thêm CI, rồi xây danh mục và lý thuyết Toán 12 với migration và API. Chuyển giao diện từng luồng sang React/Tailwind/KaTeX.
3. Hoàn thiện câu hỏi, nhập JSON có duyệt, bài luyện và đề thi đủ dạng. Chạy kiểm thử điểm, hạn nộp và dữ liệu cũ.
4. Hoàn thiện quản trị, thống kê, lộ trình theo quy tắc, bảo mật và pilot. Mở nhập PDF/Word sau khi quy trình duyệt JSON ổn định.
5. Thu dữ liệu được phép, chạy ML baseline, ablation và đánh giá. Qua nghiệm thu mới hiển thị dự đoán. Triển khai VIP sau khi chốt nghiệp vụ.

Các quyết định còn mở gồm cấu trúc đề theo năm, nguồn nội dung được phép, chính sách dữ liệu khi pilot, ngưỡng đánh giá ML và mô hình giá VIP.
