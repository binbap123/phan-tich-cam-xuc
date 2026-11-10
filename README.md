# Ứng dụng Học máy và Xử lý Ngôn ngữ Tự nhiên trong Phân tích Cảm xúc Đánh giá Sản phẩm Thương mại Điện tử

Đồ án cuối khóa, học phần Trí tuệ Nhân tạo Ứng dụng & Khoa học Dữ liệu.

## Cấu trúc

| Thư mục | Nội dung |
|---|---|
| `notebook/` | Toàn bộ quy trình, chạy theo thứ tự số |
| `src/` | Hàm dùng chung: nạp dữ liệu, tiền xử lý, đặc trưng, ABSA |
| `app/` | Dashboard Streamlit |
| `data/` | Dữ liệu gốc và dữ liệu đã xử lý |
| `labeling/` | Tập vàng, hướng dẫn gán nhãn |
| `models/` | Mô hình cổ điển đã huấn luyện |
| `report/` | Báo cáo Quarto, bảng kết quả, kết quả PhoBERT |
| `figures/` | Hình do notebook xuất ra |
| `demo/` | Link ứng dụng online |

## Cài đặt

Dùng Python 3.11.

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r code_requirements.txt
```

`requirements.txt` chỉ gồm thư viện để chạy app; `code_requirements.txt` gồm thêm thư viện cho notebook.

## Chạy notebook

Thứ tự: `01` → `02` → `03` → `04` → `05` → `06` → `06b` → `07` → `08` → `09` → `10`.

- `08_phobert_colab` chạy trên Google Colab có GPU. Kết quả giải nén vào `report/phobert/`.
- `06b` mất khoảng 10–15 phút. Các notebook còn lại chạy trong vài phút.

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

- **UIT-ViSD4SA:** review điện thoại có nhãn khía cạnh và cảm xúc (Phan và cộng sự, 2021).
- **Shopee:** 2.843 review của 32 sản phẩm, trong `data/final_train_dataset.csv`, lấy từ bộ dữ liệu Kaggle [Shopee and tiki reviews _ vietnamese version](https://www.kaggle.com/datasets/khngxuninh/shopee-and-tiki-reviews-vietnamese-version) (tài khoản `khngxuninh`; không có mô tả cách thu thập, giấy phép ghi Unknown; có lẫn một số review nhắc Tiki).
- **Không dấu:** 1.347 review trong `data/aug_unaccented_reviews.jsonl`, lấy từ bộ dữ liệu Kaggle [Shopee Vietnamese Product Reviews Sentiment](https://www.kaggle.com/datasets/dduongdev/shopee-vietnamese-product-reviews-sentiment) (Duong Nguyen, Apache 2.0). Đây là mẫu tổng hợp sinh từ review Shopee.vn, chưa rõ cách sinh, nên chỉ dùng để train.
- **Tập vàng:** 300 câu Shopee do người thực hiện đồ án tự gán nhãn, trong `labeling/gold_500.csv`.
