# HPF talking head

Gọi: "HPF talking head", "skill talking head của HPF", "edit kiểu HPF".

Talking head tiếng Việt cho coach / chuyên gia: concept và font chữ creator-aesthetic (serif nghiêng màu kem, gõ chữ,
sticker lấp lánh), cấu trúc và cảnh trám kiểu kênh fitness chuyên môn (caption 1 từ, header đánh số theo mục, tag,
emoji gom hàng, con số gạch đi, cảnh trám bằng footage tập luyện của chính mình), recap cuối.

- `SYSTEM.md` bất biến, vùng an toàn, quy trình
- `house.json` house look cố định
- `transcribe_vi.py` faster-whisper tiếng Việt, word timing
- `plate.py` cắt frame-exact từ file 3K/4K gốc + punch-in + cảnh trám -> build/plate.mp4, build/voice_raw.wav
- `overlay.py` toàn bộ đồ hoạ (PIL, RGBA stream) + snapshot duyệt (`--still`) + danh sách SFX (`--events`)
- `final.sh` ghép plate + overlay + giọng + SFX, master -14 LUFS, H.264 1080x1920 30 fps
- `fetch_assets.sh` font có dấu tiếng Việt (Be Vietnam Pro, Playfair Display, Oswald; OFL) + emoji Fluent 3D (MIT)
- `example/plan.py` reel đầu tiên: "Dân văn phòng giảm cân sao cho đỡ stress?" (DJI 0081 + cảnh trám 0084)

Chạy trên Linux/macOS, chỉ cần ffmpeg, Python 3 (Pillow, numpy, faster-whisper). Không cần HyperFrames.
