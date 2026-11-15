# HPF talking head: hệ thống (SYSTEM)

Skill talking head của HPF. Học từ 6 video reference:
- **Ref 1** (concept + font chữ): creator "aesthetic", 1 từ trắng nhỏ trên ngực, keyword lớn màu **kem** bằng **serif nghiêng**
  hoặc **condensed in hoa**, gõ chữ kiểu typewriter có con trỏ `|`, sticker ngôi sao lấp lánh, ô highlight kem.
- **Ref 2-4** (cảnh trám, hướng edit chuyên môn, fitness VN): caption 1 từ đậm trắng, tiêu đề đánh số ("4. ĐẨY DỌC"),
  tag nhãn màu cho cụm ý chính, icon/ảnh xuất hiện đúng chữ và *gom lại thành hàng* (tier list), cảnh trám là chính
  footage tập luyện của mình (full màn, caption vẫn chạy), jump cut + punch-in để giấu cắt.
- **Ref 5-6** (bổ sung): header từng mục giữ cố định ở trên ("1.) It's NOT a hobby" trắng + dòng 2 màu kem),
  tiêu đề hook serif lớn gõ chữ, ảnh/emoji hiện phía trên đầu, recap cả list ở cuối.

## Bất biến (cái làm nên style)
1. Mặt người nói **giữ nguyên màu như quay**, không grade. Chỉ có 1 gradient tối nhẹ ở đỉnh khung (0-700 px) để chữ đọc được.
2. **Không gì đè lên mặt.** Đồ hoạ chỉ ở 2 vùng an toàn: **dải tường phía trên** (y 120-700: hook, header, emoji, bảng
   giá, recap) và **vùng ngực** (y 1290-1450: tag, keyword pop, caption). Đo vị trí mặt ở mọi mức zoom trước khi đặt.
3. **Caption 1 từ một lúc**, chữ thường, Be Vietnam Pro ExtraBold 66 px trắng có bóng mềm, y = 1420. Keyword pop thay chỗ caption.
4. **Hook** (đến hết ý mở đầu): kicker trắng in hoa nhỏ có ✦ + câu hỏi lớn Playfair Display Italic màu kem `#F6EAAA`,
   gõ chữ 24 ký tự/s, con trỏ nhấp nháy, emoji ✨⭐ lấp lánh.
5. **Header theo mục**: dòng 1 "N.) CỤM IN HOA" Be Vietnam Pro ExtraBold 50 trắng, dòng 2 Playfair Italic 72 kem gõ chữ.
   Giữ suốt mục, đổi mục = tiếng lật giấy.
6. **Keyword pop**: Playfair Italic kem (cảm xúc, câu chốt) hoặc Oswald 600 in hoa trắng (từ khoá kỹ thuật: CALO,
   STRESS), có glow, pop scale 0.6 -> 1 (ease back), 0.6-2.2 s.
7. **Tag**: hộp kem bo góc, chữ mực đậm, Be Vietnam Pro SemiBold 42, ngay trên caption.
8. **Emoji 3D** (Fluent, MIT) pop đúng chữ; đồ vật trong một liệt kê **gom thành hàng** và ở lại tới hết ý; badge ✓/✗
   cho "được làm / bỏ". Emoji cảm xúc (😰😋😩🤪) đặt cạnh đầu phía khoảng trống, không chạm mặt.
9. **Con số**: số cũ Oswald trắng, gạch đỏ chạy ngang đúng chữ "xuống", số mới Oswald kem glow.
10. **Cảnh trám** = footage của chính mình (coach + khách tập), full màn, <= 25 % thời lượng, <= 3 lần/phút, đặt trên câu
    mà nó minh hoạ; caption tiếp tục chạy; vào cảnh bằng 1 whoosh nhẹ.
11. **Cắt**: chọn câu theo transcript, cắt theo thời gian từng từ (a = từ đầu - 0.12, b = từ cuối + 0.22), snap theo frame,
    hình và tiếng cắt cùng điểm, fade 8 ms. Xen kẽ zoom 1.00 / 1.18 / 1.32 (punch vào mặt) để giấu jump cut; 1.32 cho câu chốt.
12. **Recap** ở 3-4 s cuối: cả list các mục, dòng kem/trắng xen kẽ. Đuôi giữ khung cuối 0.6 s.
13. Âm thanh: giọng highpass 80 Hz + compressor nhẹ, master -14 LUFS / -1.5 dBTP. SFX tiết chế (~1 mỗi 10 s, -14..-18 dB).
    Nhạc nền: thêm từ thư viện của nền tảng lúc đăng.
14. Không chữ nào trên màn hình nói điều người nói không nói. Header/tag/recap chỉ tóm lời của họ.

## House look (cố định)
`house.json`. Mỗi reel chỉ đổi nội dung: câu chọn, header, keyword, tag, emoji, cảnh trám.

## Slot nội dung (đổi theo reel)
- `plan.py` của reel: `PIECES` (a, b, zoom, broll), `FACE`, nguồn `SRC` / `BROLL`.
- Khối **beats** trong `overlay.py` (HOOK_END, SECTIONS, POPS, TAGS, EMOJI, MARKS, PRICE, RECAP_LINES, FIX): viết lại theo
  transcript, mọi thời điểm bằng `E(<giây gốc>)` để tự khớp sau khi cắt.

## Quy trình
```bash
P=<thư mục reel>; H=$S/recipes/hpf-talking-head
bash $H/fetch_assets.sh                       # font có dấu tiếng Việt + emoji (một lần)
# tách audio 16 kHz mono vào $P/wav/<clip>.wav, rồi:
cd $P && python3 $H/transcribe_vi.py large-v3-turbo <clip>   # tx/<clip>.txt + .json (word timing)
# kiểm tra từ nghe chưa chắc bằng large-v3 trên đoạn ngắn, thêm vào FIX
cp $H/example/plan.py $P/plan.py              # sửa PIECES theo câu chọn
python3 $H/plate.py                           # build/plate.mp4 + build/voice_raw.wav
python3 $H/overlay.py --still <t1,t2,...> build/sheet.jpg bg   # duyệt: snapshot build/snap/NN.png trước
bash $H/final.sh finals/<tên>.mp4
```
Duyệt sheet trước khi render: không đồ hoạ nào chạm mặt ở shot tight 1.32, chữ không tràn mép, mỗi beat đúng chữ.
