# Luật chung cho Claude và Codex

Đồ án: Project 09, phân tích cảm xúc review tiếng Việt. Hạn nộp 23:59 ngày 11/11/2026.

## Tài liệu quyết định

1. `huong_dan_tieu_luan_va_rubric_cuoi_khoa.pdf` (23/10) quyết định cách chấm và cách trình bày.
2. Đề Project 09 quy định nội dung phải có: phân loại 3 lớp, ABSA, word cloud từng lớp, top 3 vấn đề, dashboard.
3. `HUONG_DAN_DO_AN.md` là hướng dẫn phụ. Nếu khác PDF thì theo PDF.

## Vai trò

- **Một bên sửa, một bên kiểm tra.** Mỗi việc có đúng một người sửa, ghi ở `harness/TASKS.md`.
- **Claude** làm code, notebook, app, render PDF và đóng gói.
- **Codex** phản biện: đọc thay đổi, đối chiếu rubric, ghi vào `harness/REVIEW.md`. Không sửa file khác, trừ khi người dùng giao đích danh.
- **Người dùng** viết phần phân tích, duyệt việc xong, quyết định khi hai bên bất đồng.
- Không hai bên cùng chạy lệnh ghi file. Trước khi sửa, xem `git status` và trạng thái việc trong `TASKS.md`.

## Luật về kết quả

- Tập vàng không dùng để chọn mô hình, tham số hay ngưỡng. Phân tích làm sau khi xem tập vàng phải ghi là thăm dò.
- Không train trên tập vàng. Aug chỉ dùng để train.
- Chia dữ liệu và CV theo sản phẩm.
- Mọi con số trong báo cáo phải đến từ `report/*.csv` hoặc notebook.
- Ghi rõ F1-macro đo trên tập nào. Từ 08/11 kết quả chính dùng nhãn train gán lại (PhoBERT: 0,779 trên ViSD4SA test; 0,704 trên tập vàng Shopee, thăm dò). Bản nhãn sao: 0,808 và 0,617. Không nói "đạt F1 ≥ 0,75 trên Shopee".
- Chỉ số kinh doanh chính là Recall lớp tiêu cực; luôn báo kèm F1-macro.
- Giả định chi phí và ROI phải ghi là giả định.
- Kết quả thí nghiệm mới chỉ được dùng sau khi bên còn lại kiểm tra. `scripts/`, `report/*_retrain/`, `models/*_retrain/` chưa được kiểm tra.

## Luật về nội dung

- Không viết thay các chỗ `[VIẾT]`, nhận xét, persona hay top 3 vấn đề, trừ khi người dùng yêu cầu rõ. Có thể góp ý.
- Không commit hoặc push nếu người dùng chưa yêu cầu.
- Tuyên bố sử dụng AI phải nêu cả Claude và ChatGPT/Codex.

## Quy trình một việc

1. Nhận việc trong `TASKS.md`, đổi trạng thái thành `dang-lam`.
2. Làm xong, chạy `.venv/Scripts/python.exe harness/check.py`, đổi thành `cho-kiem-tra`.
3. Bên còn lại ghi nhận xét vào `REVIEW.md`, mỗi mục gồm vị trí, tiêu chí rubric, vấn đề, đề xuất và mức độ.
4. Người làm kiểm chứng từng mục, sửa hoặc ghi lý do không sửa.
5. Người dùng duyệt thì đổi thành `xong`.
