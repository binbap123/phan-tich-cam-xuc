# Hướng dẫn gán nhãn tập vàng Shopee (bản nháp)

> Bản nháp do Claude soạn ngày 28/10. **Bạn đọc lại, sửa quy tắc nào chưa đồng ý, rồi mới gán.** Khi gán gặp ca khó mà guideline chưa nói tới, thêm quy tắc mới vào mục 5 và ghi vào cột `ghi_chu`.
> Ví dụ lấy từ `shopee_train.csv` (không lấy từ tập vàng, để khỏi gán sẵn trước).

## 1. File và cách làm

- File: `labeling/gold_500_to_label.csv`. Mở bằng Excel hoặc Google Sheets. Gán xong thì lưu thành `labeling/gold_500.csv` (Excel: *Save As → CSV UTF-8*).
- Số sao và tên sản phẩm **đã được ẩn** (nằm ở `gold_500_key.csv`). Đừng mở file key khi đang gán.
- Mỗi buổi gán tối đa khoảng 150 câu. Mệt thì nghỉ.
- Cột `sentiment`: gán cho **cả 500 câu**. Bốn cột khía cạnh chỉ gán ở những dòng có `gan_khia_canh = có` (200 câu đầu).

## 2. Nhãn cảm xúc (`sentiment`)

Câu hỏi để quyết định nhãn: **người mua có hài lòng với lần mua này không?**

| Nhãn | Khi nào | Ví dụ |
|---|---|---|
| `pos` | Hài lòng, khen, muốn mua lại | "Giao hàng rất nhanh, rửa mặt rất đã." |
| `neg` | Không hài lòng, chê, thất vọng, phàn nàn | "Tệ Đặt 1 loại giao 1 loại 😮‍💨" |
| `neu` | Không thể hiện hài lòng hay không, hoặc khen và chê cân nhau mà không có kết luận | "Mua dc giảm giá. Chưa dùng nên chưa biết" |

## 3. Các trường hợp khó

**3.1. Vừa khen vừa chê.** Xét theo thứ tự sau:
1. Nếu có **kết luận rõ ràng** ("nói chung là ổn", "sẽ không mua lại", "hên xui") thì theo kết luận đó.
2. Nếu không có kết luận, ý về **bản thân sản phẩm** (chất lượng, đúng mô tả, đúng hàng) được ưu tiên hơn ý về giao hàng và đóng gói.
3. Nếu vẫn cân nhau thì gán `neu`.

- "Giao hàng khá nhanh, săn sale nên đc giá tốt. Cơ mà mình trừ 1 sao do giao sai màu…" → `neg`. Lời chê về việc giao sai hàng là ý chính, người mua trừ sao vì nó.
- "Banh cũng ok nhưng mới giao về hình như bị lủng r bơm lên … là xì" → `neg`. Sản phẩm bị lỗi.
- "5 sao cho sản phẩm vì srm làm sạch nhưng k gây khô da" → `pos`. Chữ "nhưng" ở đây không mở ra lời chê.
- "Chỉ hát đc mấy giây … Nchung là hên xui" → `neg`. Lỗi chức năng, kết luận "hên xui" là không hài lòng.

**3.2. Chưa dùng sản phẩm.**
- Chỉ có "chưa dùng nên chưa biết" → `neu`.
- Có thêm lời khen giao hàng hoặc đóng gói, ví dụ "Giao hàng khá nhanh, bọc kĩ, chưa sử dụng nên chưa biết chất lượng" → `pos`, vì phần đánh giá duy nhất là lời khen.
- Có thêm lời chê, ví dụ "Chưa biết chất lượng … ông shipper … vứt đồ vào hồ nước ướt hết" → `neg`.

**3.3. Mỉa mai, nói ngược.** Gán theo **ý thật**, không theo chữ. Ví dụ "Tuyệt vời, giao cái áo rách" → `neg`. Ghi `mia_mai` vào cột `ghi_chu` để sau này phân tích lỗi.

**3.4. Chỉ mô tả, không đánh giá.** Ví dụ chỉ ghi màu, size, chất liệu ("Màu sắc: be, chất liệu: cotton") → `neu`.

**3.5. Câu rác hoặc không hiểu.** Gõ phím lung tung, hoặc câu không liên quan tới sản phẩm → gán `neu` và ghi `rac` vào `ghi_chu`. Sau này có thể quyết định bỏ những câu này khỏi tập vàng.

**3.6. Từ tục, teencode.** Không tự động coi là `neg`. Ví dụ "nón thúi vcl" → `neg` vì "thúi" mới là lời chê, còn "đẹp vcl" là `pos`.

## 4. Nhãn khía cạnh (200 câu đầu)

Mỗi cột nhận một trong bốn giá trị: `pos`, `neg`, `neu` hoặc `none`. Gán `none` khi câu **không nhắc tới** khía cạnh đó. Gán `neu` khi có nhắc tới nhưng không khen cũng không chê (ví dụ "chưa biết chất lượng").

| Cột | Gồm | Ví dụ |
|---|---|---|
| `giao_hang` | Tốc độ giao, shipper, đóng gói, hộp, tình trạng khi nhận | "ship hơi lâu, gần 2 tuần mới nhận" → `neg` |
| `chat_luong` | Chất lượng, chất liệu, độ bền, công dụng, mùi, **đúng với mô tả hoặc hình** | "Chất như giẻ lau" → `neg` |
| `gia_ca` | Giá, rẻ, đắt, đáng tiền, sale, voucher | "săn sale nên đc giá tốt" → `pos` |
| `dich_vu` | Thái độ shop, tư vấn, trả lời tin nhắn, đổi trả, bảo hành, **giao sai màu hoặc sai mẫu** (lỗi của shop) | "Khách note kỹ càng nhưng shop giao không đúng màu" → `neg` |

Một câu có thể có nhiều khía cạnh với cảm xúc trái nhau. Ví dụ "mặt hàng ok tuy nhiên ship hơi lâu" → `chat_luong = pos`, `giao_hang = neg`, `gia_ca = none`, `dich_vu = none`.

## 5. Quy tắc thêm trong lúc gán

- *(ghi thêm ở đây)*
- Với `test_moi_200.xlsx` (06/11): gán `sentiment` cho cả 200 câu, 4 cột khía cạnh chỉ gán ở dòng `gan_khia_canh = có` (100 câu đầu). Không hỏi AI, không mở file key. Dùng file này để đánh giá.

## 6. Đo độ đồng thuận

Sau khi gán xong 500 câu, đợi ít nhất một ngày rồi gán lại `labeling/gold_relabel_60.csv` (60 câu lấy từ 150 câu đầu) **mà không xem nhãn cũ**. Sau đó chạy Phần 2 của `notebook/03_gold_labeling.ipynb` để tính Cohen's kappa. Kappa từ 0,6 trở lên là chấp nhận được, từ 0,8 trở lên là tốt.
