# Minh chứng sản phẩm mẫu

- **Ứng dụng online:** <https://khoa-review-sentiment.streamlit.app/> (Streamlit Community Cloud, nhánh `rubric-cuoi-khoa`, file `app/dashboard.py`). Đã mở thử ngày 10/11/2026: phân tích một review, tab What-if và tab Tổng quan chạy không lỗi.

## Luồng thao tác gợi ý khi dùng thử

1. **Phân tích review:** nhập một review chê, xem nhãn, độ tin cậy, khía cạnh, từ ảnh hưởng và khuyến nghị.
2. **What-if:** sửa câu và xem dự đoán thay đổi; đổi số review, chi phí và ngưỡng để xem chi phí vận hành.
3. **Tổng quan:** mặc định là 2.548 review Shopee; tải file CSV (cột `text`, tùy chọn `rating`, `category`, `product`) để xem tổng quan trên dữ liệu của shop và tải kết quả. Lọc theo ngành hàng/sản phẩm, xem tỉ lệ cảm xúc, khía cạnh, từ khóa và review tiêu cực nổi bật.
