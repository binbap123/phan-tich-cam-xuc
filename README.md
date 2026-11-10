# Phân tích cảm xúc đánh giá sản phẩm thương mại điện tử

Đồ án cuối khóa học phần Trí tuệ Nhân tạo Ứng dụng & Khoa học Dữ liệu (Project 09), Trường Đại học Quản lý và Công nghệ TP.HCM (UMT).

Hệ thống phân loại review tiếng Việt thành **tiêu cực / trung lập / tích cực**, tách cảm xúc theo 4 khía cạnh (giao hàng, chất lượng, giá cả, dịch vụ), tìm top vấn đề khách phàn nàn và gợi ý việc cần làm cho chủ shop và nhân viên CSKH.

- **Ứng dụng online:** <https://khoa-review-sentiment.streamlit.app/>
- **Báo cáo:** [`report/bao_cao.pdf`](report/bao_cao.pdf) (nguồn Quarto: [`report/bao_cao.qmd`](report/bao_cao.qmd))

## Kết quả chính

| Mô hình | F1-macro ViSD4SA test | F1-macro tập vàng Shopee* | Recall tiêu cực (vàng)* |
|---|---|---|---|
| BoW + Naive Bayes (baseline) | 0,585 | 0,583 | 0,810 |
| TF-IDF + Logistic Regression (dùng trong app) | 0,720 | 0,612 | 0,835 |
| TF-IDF + LinearSVC | 0,698 | 0,601 | 0,810 |
| TF-IDF + đặc trưng nghiệp vụ + LR | 0,724 | 0,646 | 0,851 |
| PhoBERT (fine-tune trên Colab) | 0,779 | 0,704 | 0,851 |

\* Tập vàng 300 câu đã được xem trong quá trình phát triển nên các số này chỉ mang tính thăm dò. Số liệu lấy từ [`report/main_results.csv`](report/main_results.csv).

## Ứng dụng

Dashboard Streamlit gồm 3 tab:

1. **Phân tích review:** nhập một review, xem nhãn, độ tin cậy, khía cạnh, từ ảnh hưởng và khuyến nghị hành động; câu mô hình không chắc chắn được chuyển cho người đọc lại.
2. **What-if:** sửa câu (thêm phủ định, bỏ dấu…) để xem dự đoán thay đổi; nhập số review, chi phí và ngưỡng để so sánh chi phí giữa các cách sàng lọc.
3. **Tổng quan:** mặc định là 2.548 review Shopee; tải file CSV của shop (cột `text`, tùy chọn `rating`, `category`, `product`) để xem tỉ lệ cảm xúc, khía cạnh, top từ khóa, review tiêu cực nổi bật và tải kết quả.

## Cấu trúc thư mục

| Thư mục | Nội dung |
|---|---|
| `notebook/` | Toàn bộ quy trình, chạy theo thứ tự số |
| `src/` | Hàm dùng chung: nạp dữ liệu, tiền xử lý, đặc trưng, ABSA |
| `app/` | Dashboard Streamlit (`app/dashboard.py`) |
| `scripts/` | Thí nghiệm gán lại nhãn và dữ liệu không dấu |
| `data/` | Dữ liệu gốc và dữ liệu đã xử lý |
| `ViSD4SA/` | Bộ dữ liệu UIT-ViSD4SA (train/dev/test) |
| `labeling/` | Tập vàng, hướng dẫn gán nhãn, 250 câu train gán lại |
| `models/` | Mô hình cổ điển đã huấn luyện |
| `report/` | Báo cáo Quarto, bảng kết quả, kết quả PhoBERT |
| `figures/` | Hình do notebook xuất ra |
| `demo/` | Link ứng dụng và biên bản kiểm thử |

## Cài đặt

Dùng Python 3.11.

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r code_requirements.txt
```

`requirements.txt` chỉ gồm thư viện để chạy app (dùng cho Streamlit Cloud); `code_requirements.txt` gồm thêm thư viện cho notebook.

## Chạy notebook

Thứ tự: `01` → `02` → `03` → `04` → `05` → `06` → `06b` → `07` → `08` → `09` → `10`.

- `08_phobert_colab` chạy trên Google Colab có GPU; giải nén kết quả vào `report/phobert/`.
- `06b` mất khoảng 4 phút, các notebook còn lại chạy trong vài chục giây đến 1–2 phút.

## Chạy dashboard

```bash
.venv/Scripts/streamlit.exe run app/dashboard.py
```

## Render báo cáo

Chạy trong thư mục `report/`. Cần cài TinyTeX bằng `quarto install tinytex`.

```bash
quarto render bao_cao.qmd --to pdf
```

Nếu Quarto không tìm đúng Python, đặt biến môi trường `QUARTO_PYTHON` trỏ tới `.venv/Scripts/python.exe`.

## Nguồn dữ liệu

- **UIT-ViSD4SA:** review điện thoại có nhãn khía cạnh và cảm xúc (Phan và cộng sự, 2021), trong `ViSD4SA/`.
- **Shopee:** 2.843 review của 32 sản phẩm, trong `data/final_train_dataset.csv`, lấy từ bộ dữ liệu Kaggle [Shopee and tiki reviews _ vietnamese version](https://www.kaggle.com/datasets/khngxuninh/shopee-and-tiki-reviews-vietnamese-version) (tài khoản `khngxuninh`; không có mô tả cách thu thập, giấy phép ghi Unknown; có lẫn một số review nhắc Tiki).
- **Không dấu:** 1.347 review trong `data/aug_unaccented_reviews.jsonl`, lấy từ bộ dữ liệu Kaggle [Shopee Vietnamese Product Reviews Sentiment](https://www.kaggle.com/datasets/dduongdev/shopee-vietnamese-product-reviews-sentiment) (Duong Nguyen, Apache 2.0). Đây là mẫu tổng hợp sinh từ review Shopee.vn, chưa rõ cách sinh, nên chỉ dùng để train.
- **Tập vàng:** 300 câu Shopee do người thực hiện đồ án tự gán nhãn, trong `labeling/gold_500.csv`.

## Sử dụng công cụ AI

Claude (Anthropic) và ChatGPT/Codex hỗ trợ viết mã, phản biện và soạn một phần báo cáo; chi tiết trong mục "Lời cảm ơn và tuyên bố sử dụng AI" của báo cáo.
