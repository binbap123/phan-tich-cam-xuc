# Danh sách việc

Trạng thái: `chua-lam`, `dang-lam`, `cho-kiem-tra`, `xong`.

| # | Việc | Người làm | Kiểm tra | Trạng thái | Tiêu chí xong |
|---|---|---|---|---|---|
| 1 | Hỏi giảng viên: làm cá nhân, số nhóm, mã đề, rubric nào áp dụng | Người dùng | | xong | 09/11: người dùng làm cá nhân. Mã đề Project 09. Người dùng xác nhận chấm theo rubric trong file hướng dẫn tiểu luận (PDF 23/10); yêu cầu Project 09 chỉ là nội dung đề. Bảng phân công chỉ một người |
| 2 | Render PDF sạch, trang bìa đầy đủ | Claude | Codex | chua-lam | `check.py` đạt phần PDF |
| 3 | Rà app: 3 tab, What-if, top từ khóa | Claude | Codex | cho-kiem-tra | Không lỗi trong trình duyệt |
| 4 | Deploy Streamlit Cloud, thêm link vào `demo/README.md` | Người dùng | Claude | chua-lam | Link mở được |
| 5 | Quay video 2–3 phút | Người dùng | | xong | 09/11: người dùng quyết định bỏ, chỉ nộp link app. Đã xóa phần video ở `demo/README.md` và báo cáo |
| 6 | Gán lại 60 câu, tính kappa | Người dùng | Claude | xong | 08/11: người dùng quyết định bỏ (rubric PDF không yêu cầu). Đã xóa khỏi `check.py`, notebook 03, báo cáo. Nên ghi vào hạn chế: tập vàng một người gán |
| 7 | Điền `nhom_loi` trong `error_analysis.csv` (người dùng giao Codex ngày 08/11) | Codex | Claude | cho-kiem-tra | Đã đủ 40/40; nhóm lỗi do Codex đề xuất, cần Claude/người dùng duyệt (R6) |
| 8 | Xem xét `scripts/` và kết quả `*_retrain` | Codex | Claude | cho-kiem-tra | Có kết luận dùng hay bỏ trong `REVIEW.md` |
| 9 | Viết các chỗ `[VIẾT]` và ô nhận xét (người dùng giao Codex ngày 08/11) | Codex | Claude | cho-kiem-tra | 0 chỗ viết trống; 21 ô bảng chạy được; bản HTML để đọc; `check.py` 28/34, còn bìa/demo/PDF và kiểm tra màu word cloud sai (R6) |
| 10 | Nhờ 3–5 người dùng thử | Người dùng | | xong | 09/11: người dùng quyết định bỏ (chỉ là điểm thưởng). Đã xóa bảng phản hồi ở `demo/README.md`, kiểm tra trong `check.py`; báo cáo ghi là hướng phát triển |
| 11 | Restart & Run All toàn bộ notebook | Claude | Codex | chua-lam | `check.py` đạt phần notebook |
| 13 | Duyệt `train_250_duyet.xlsx`, tự gán `test_moi_200.xlsx` (100 câu đầu thêm khía cạnh) | Người dùng | Claude | xong | Đã duyệt 250 câu train. 08/11: người dùng quyết định không gán test mới, dùng tập vàng và ViSD test có sẵn |
| 14 | Train lại TF-IDF, PhoBERT với nhãn mới; đánh giá ABSA trên test mới | Claude | Codex | cho-kiem-tra | 08/11 người dùng chọn nhãn mới (mục tiêu Recall neg). Đã chạy lại notebook 04–07, 09, 10; số trên vàng là thăm dò |
| 12 | Đóng gói `.zip`, nộp bài | Claude, Người dùng | Codex | chua-lam | `check.py` đạt toàn bộ |
