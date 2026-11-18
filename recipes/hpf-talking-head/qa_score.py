"""Self-critique pass (learned from xilo-opus-video): sheets to judge a finished reel like a stranger would, plus a
score log. Writes <out>-sheet.jpg (a frame every 2 s), <out>-phone.jpg (the same at 360 px wide: can you still read it?),
and appends a scoring template to qa/review_log.md. Fix the 3 worst problems, re-render, score again until every line >= 8.
usage: qa_score.py finals/reel.mp4 --out qa/reel [--strip 4.1]   (--strip: 12 consecutive frames around a fast move)"""
import argparse, subprocess, os, json, datetime
ap = argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("--out", required=True)
ap.add_argument("--strip", type=float, action="append", default=[])
a = ap.parse_args()
os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.video],
                           capture_output=True, text=True).stdout)
n = int(dur // 2) + 1; cols = 10; rows = (n + cols - 1) // cols
for name, w in (("sheet", 216), ("phone", 360)):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.video, "-vf",
                    f"fps=1/2,scale={w}:-2,drawtext=fontfile=/root/.fonts/BeVietnamPro-SemiBold.ttf:text='%{{pts\\:hms}}':x=4:y=4:"
                    f"fontsize={max(12, w // 16)}:fontcolor=yellow:box=1:boxcolor=black@0.6,tile={cols if name == 'sheet' else 5}x"
                    f"{rows if name == 'sheet' else (n + 4) // 5}", "-frames:v", "1", f"{a.out}-{name}.jpg"], check=True)
for s in a.strip:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s}", "-i", a.video, "-vf", "scale=320:-2,tile=12x1",
                    "-frames:v", "1", f"{a.out}-strip-{s}.jpg"], check=True)
log = os.path.join(os.path.dirname(a.out) or ".", "review_log.md")
with open(log, "a") as f:
    f.write(f"""
## {os.path.basename(a.video)} · {datetime.datetime.now():%Y-%m-%d %H:%M}
| hạng mục | điểm 1-10 | ghi chú |
|---|---|---|
| hook: 2 giây đầu có giữ người xem không | | |
| đọc được trên điện thoại (bản 360 px) | | |
| chuyển động: không có đoạn trơ, không trượt đều máy móc | | |
| mỗi 2-4 giây có thứ mới (cắt khung, chữ, emoji, cảnh trám) | | |
| bố cục: không chạm mặt, không chồng chữ, không trống một mảng | | |
| đúng lời host / đúng sửa đổi của chủ kênh (taste.json) | | |
| âm-hình khớp: SFX đúng lúc, nhạc không át giọng | | |
3 lỗi nặng nhất (kèm giây):
1.
2.
3.
""")
print(f"{a.out}-sheet.jpg  {a.out}-phone.jpg  log -> {log}")
