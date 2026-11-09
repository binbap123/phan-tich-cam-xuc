# Ghi chú dữ liệu (đầu ra ngày 22–24/10)

Số liệu lấy từ `notebook/01_eda.ipynb` và `notebook/02_clean_split.ipynb` (chạy ngày 28/10). Bảng đầy đủ các bước làm sạch nằm trong `data/processed/cleaning_steps.csv`.

## 1. Câu trả lời của giảng viên

- Chưa có xác nhận của giảng viên về cách tính điểm nguồn Shopee có sẵn. Báo cáo mô tả dùng tệp CSV trong dự án, không tuyên bố đã tự cào dữ liệu.
- PDF rubric ngày 23/10 quy định tối đa 45 trang, không tính code/mã nguồn. Không còn dùng mốc 30 trang của hướng dẫn phụ; PDF không nêu miễn trừ toàn bộ phụ lục.

## 2. Ba nguồn dữ liệu

| Nguồn | Gốc | Sau làm sạch | Nhãn | Vai trò |
|---|---|---|---|---|
| A: ViSD4SA | 11.122 (7.785 / 1.112 / 2.225) | 10.510 (train 7.344 / dev 1.046 / test 2.120) | cụm từ → nhãn câu | train 3 lớp, ABSA |
| B: Shopee CSV | 2.843 | 2.548 → train 1.794 (22 sp), kho vàng 746 (10 sp) | sao (nhãn yếu) | train + tập vàng + kinh doanh |
| Aug: JSONL | 1.347 | 1.205 | pos/neg | chỉ train |

## 3. Phân bố nhãn

| Nguồn | pos | neg | neu |
|---|---|---|---|
| A (cả 3 tập, trước khi bỏ trùng) | 6.638 (63,1%) | 3.456 (32,9%) | 419 (4,0%) |
| B (nhãn sao, 2.548 câu) | 1.709 (67,1%) | 597 (23,4%) | 242 (9,5%) |
| Aug | 652 | 553 | 0 |

Nếu mô hình đoán "pos" cho mọi câu Shopee, accuracy là 0,689 nhưng F1-macro chỉ 0,272. Vì vậy phải báo F1-macro.

## 4. Các bước làm sạch Shopee

| Bước | Số dòng |
|---|---|
| File gốc | 2.843 |
| Bỏ rác giao diện "Tổng quan… Trợ lý AI tổng hợp" | 2.723 |
| Bỏ nhãn mục template rồi khử trùng | 2.556 |
| Bỏ review dưới 2 từ | 2.548 |
| Chia theo sản phẩm (`GroupShuffleSplit`, random_state=42) | train 1.802 / kho vàng 746 |
| Bỏ 8 câu train trùng với kho vàng | train 1.794 |

## 5. Ghi chú khác

- ViSD4SA: 122 cụm có `end` vượt độ dài câu (nhiều nhất 25 ký tự), đã cắt lại. 331 câu chưa chuẩn NFC. 225 review không có cụm nào. 39% review có nhiều cảm xúc khác nhau.
- Có 2 tên sản phẩm Shopee lưu ở dạng NFD (áo bra, bình giữ nhiệt). Đã chuẩn hóa NFC trước khi chia và ghép bảng ngành hàng.
- Aug: file hiện có 1.347 dòng (hướng dẫn ghi 1.348), nên sau khi lọc còn 1.205 thay vì 1.206. 55 dòng có `*`, tab hoặc dấu `"` thừa, đã thay bằng khoảng trắng.
- Bảng sản phẩm → ngành hàng: `data/processed/product_category.csv`, gồm 9 ngành. Ngành do Claude gán theo từ khóa trong tên sản phẩm, **cần bạn kiểm tra lại**.
- Ví dụ review 4–5 sao có lời chê (đối chiếu `data/processed/shopee_predicted.csv`, bổ sung 08/11):
  - `shp_1413`, 4 sao: “đúng đúng đúng Khó chỉnh giờ”.
  - `shp_1450`, 5 sao: “đúng đúng Nhưng không chỉ cách chỉnh giờ ai biết chỉ mình với”.
  - `shp_2329`, 5 sao: “giao hàng nhanh, nước hoa thì mùi ko vừa ý cho lắm”.

## Cập nhật bản thảo ngày 08/11

Các thống kê ở trên mô tả phiên bản chuẩn bị dữ liệu ban đầu. Kết quả chính hiện tại đọc từ `report/main_results.csv`; nhãn train Shopee có gán lại, còn word cloud EDA dùng nhãn sao ban đầu. Mọi phân tích trên tập vàng đã xem đều là thăm dò. Báo cáo và ô nhận xét notebook đã được Codex hỗ trợ viết; nhóm cần duyệt trước khi nộp.
