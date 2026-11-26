# Thiết kế hệ thống SmartTHPT v0.1

## Kiến trúc mục tiêu

```mermaid
flowchart TD
  Web["React · Tailwind · KaTeX"] --> API["FastAPI"]
  API --> PG["PostgreSQL"]
  API --> Redis["Redis"]
  API --> Worker["Worker nhập đề"]
  Worker --> Tệp["Kho tệp riêng"]
  Worker --> PG
  PG --> ML["Huấn luyện ngoại tuyến"]
  ML --> Registry["Kho phiên bản mô hình"]
  Registry --> API
```

FastAPI tổ chức theo tài khoản, nội dung, đánh giá, phân tích và thanh toán. PostgreSQL là nơi lưu dữ liệu nghiệp vụ. Redis hỗ trợ phiên, giới hạn tần suất và công việc nền khi triển khai. Quá trình huấn luyện chạy riêng. API chỉ nạp phiên bản đã duyệt. Hệ thống hiện chạy FastAPI, SQLite và JavaScript tĩnh.

API mục tiêu dưới `/api/v1` gồm `auth`, `catalog`, `lessons`, `attempts`, `insights`, `admin/imports` và `billing`. Giữ API nguyên mẫu khi chuyển từng luồng. Chuyển SQLite sang PostgreSQL bằng migration có đối chiếu số bản ghi và kiểm tra các bài đã chấm. Migrate lược đồ trước, diễn tập nhập dữ liệu sau, chuyển lưu lượng khi kiểm thử đạt.

## Use Case

| Tác nhân | Use Case | Luồng phụ |
|---|---|---|
| Học sinh | UC01–05, UC07, UC08, UC10 | Phiên hết hạn, thiếu câu phù hợp, nộp lặp, thiếu dữ liệu dự đoán, thanh toán chờ xử lý |
| Biên tập viên | UC06 | Tệp sai định dạng, câu trùng, thiếu bằng chứng quyền, bản nháp bị yêu cầu sửa |
| Admin | UC09, duyệt UC06 | Thu hồi phiên tài khoản khóa, lưu lịch sử duyệt, rà soát thay đổi vai trò |
| Nhà cung cấp thanh toán | UC10 | Webhook trùng, sai chữ ký, giao dịch hoàn tiền |

UC03/04 tạo bài. UC05 xử lý nộp và lưu kết quả. UC07 dùng kết quả đã lưu. UC08 đọc dự đoán từ mô hình đủ điều kiện. UC06 yêu cầu duyệt trước khi câu hỏi được dùng ở UC03/04.

## Activity Diagram — nộp bài

```mermaid
flowchart TD
  S["Học sinh gửi bài"] --> A{"Phiên hợp lệ và đúng chủ bài?"}
  A -- Không --> B["Từ chối yêu cầu"]
  A -- Có --> C{"Đã chấm?"}
  C -- Có --> D["Trả kết quả đã lưu"]
  C -- Chưa --> E{"Còn hạn và đáp án hợp lệ?"}
  E -- Không --> F["Áp dụng chính sách hết hạn hoặc báo lỗi"]
  E -- Có --> G["Chấm theo phiên bản đề"]
  G --> H["Lưu đáp án và điểm trong một giao dịch"]
  H --> D
```

## DFD mức 0

```mermaid
flowchart TD
  HS["Học sinh"] -->|"Thông tin đăng nhập, thao tác học, bài làm"| SYS(("SmartTHPT"))
  SYS -->|"Bài học, đề, kết quả, lộ trình"| HS
  AD["Biên tập viên và Admin"] -->|"Nội dung, quyết định duyệt và phân quyền"| SYS
  SYS -->|"Trạng thái nhập, báo cáo, audit"| AD
  SYS -->|"Yêu cầu giao dịch"| PAY["Nhà cung cấp thanh toán"]
  PAY -->|"Kết quả giao dịch"| SYS
```

## DFD mức 1

```mermaid
flowchart TD
  HS["Học sinh"] --> P1(("1. Tài khoản"))
  P1 <-->|"Tài khoản, vai trò, phiên"| D1[("D1 Tài khoản")]
  HS --> P2(("2. Học và làm bài"))
  P2 -->|"Nội dung và điểm"| HS
  D2[("D2 Nội dung")] -->|"Bài học và bản câu hỏi đã duyệt"| P2
  P2 -->|"Lượt làm và đáp án đã chấm"| D3[("D3 Kết quả")]
  D3 --> P3(("3. Phân tích học tập"))
  P3 -->|"Tiến độ và gợi ý"| HS
  AD["Biên tập viên và Admin"] --> P4(("4. Quản trị"))
  P4 -->|"Bản đã duyệt"| D2
  P4 -->|"Nhật ký"| D4[("D4 Audit")]
  HS --> P5(("5. Thanh toán"))
  P5 <--> PAY["Nhà cung cấp thanh toán"]
  P5 -->|"Giao dịch và quyền VIP"| D5[("D5 Thanh toán")]
```

## ERD mục tiêu

```mermaid
erDiagram
  SUBJECT ||--o{ COURSE : organizes
  COURSE ||--o{ CHAPTER : contains
  CHAPTER ||--o{ TOPIC : contains
  TOPIC ||--o{ LESSON : contains
  TOPIC ||--o{ QUESTION : categorizes
  QUESTION ||--o{ QUESTION_VERSION : versions
  SOURCE ||--o{ QUESTION_VERSION : supports
  USER ||--o{ ATTEMPT : starts
  ASSESSMENT_VERSION o|--o{ ATTEMPT : assigns
  ATTEMPT ||--o{ ATTEMPT_ITEM : contains
  QUESTION_VERSION ||--o{ ATTEMPT_ITEM : freezes
  USER ||--o{ SUBSCRIPTION : owns
  SUBSCRIPTION ||--o{ PAYMENT : records
```

| Nhóm | Ràng buộc chính |
|---|---|
| Danh mục | COURSE duy nhất theo lớp và môn. CHAPTER, TOPIC có thứ tự và slug duy nhất trong cha |
| Nội dung | QUESTION_VERSION duy nhất theo câu và số phiên bản. Lưu kiểu câu, dữ liệu chấm, lời giải, nguồn và trạng thái duyệt. ASSESSMENT_VERSION lưu danh sách phiên bản câu và biểu điểm |
| Đánh giá | ATTEMPT lưu người làm, hạn nộp, trạng thái, tổng điểm. ATTEMPT_ITEM lưu phiên bản câu, thứ tự, đáp án học sinh và điểm. Khóa hàng lúc chấm để xử lý đồng thời |
| Nhập và audit | IMPORT_BATCH giữ trạng thái và kết quả từng mục. AUDIT_EVENT giữ người thực hiện, đối tượng, thời điểm và hành động |
| Thanh toán | PAYMENT có khóa duy nhất theo mã giao dịch bên cung cấp. Thay đổi trạng thái thanh toán và quyền VIP trong cùng giao dịch |
| ML | MODEL_RUN tham chiếu phiên bản dữ liệu, Git SHA và metrics. PREDICTION tham chiếu run, mã học sinh, mốc thời gian và giá trị dự đoán |

## Quy trình Git và chạy trên Windows

Mỗi tính năng dùng nhánh `feat/...`, sửa lỗi dùng `fix/...`, tài liệu dùng `docs/...`. Mở PR vào `main` và đọc kết quả CI trước khi merge. Gọi script qua Python trong venv để tránh phụ thuộc ExecutionPolicy.

```powershell
Set-Location D:\SmartTHPT
git status --short
git fetch origin
git branch -vv
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
