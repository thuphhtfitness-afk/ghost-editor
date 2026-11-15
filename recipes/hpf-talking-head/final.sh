#!/bin/bash
# compose: plate (+0.6 s held tail) + overlay RGBA stream + voice chain + SFX -> finals/
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
S=$(cd "$HERE/../.." && pwd)
OUT=${1:-finals/HPF-talkinghead-dan-van-phong.mp4}
mkdir -p finals
EV=$(python3 "$HERE/overlay.py" --events)
END=$(echo "$EV" | python3 -c "import json,sys;print(json.load(sys.stdin)['end'])")
SFXIN=""; SFXF=""; MIX="[vo]"; i=3
while IFS=$'\t' read -r t name db; do
  SFXIN="$SFXIN -i $S/library/sfx/$name.wav"
  ms=$(python3 -c "print(int($t*1000))")
  SFXF="$SFXF[$i:a]aformat=sample_rates=48000:channel_layouts=mono,volume=${db}dB,adelay=$ms[s$i];"
  MIX="$MIX[s$i]"; i=$((i+1))
done < <(echo "$EV" | python3 -c "import json,sys;[print(f'{t}\t{n}\t{d}') for t,n,d in json.load(sys.stdin)['sfx']]")
N=$((i-2))
python3 "$HERE/overlay.py" --frames | ffmpeg -v error -stats -y \
  -i build/plate.mp4 -f rawvideo -pix_fmt rgba -s 1080x1920 -r 30 -i - -i build/voice_raw.wav $SFXIN \
  -filter_complex "[0:v]tpad=stop_mode=clone:stop_duration=1[pv];[pv][1:v]overlay=0:0:format=auto,trim=duration=$END,format=yuv420p[v];\
[2:a]aformat=sample_rates=48000:channel_layouts=mono,highpass=f=80,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120,apad[vo];\
$SFXF ${MIX}amix=inputs=$N:normalize=0:duration=first,atrim=duration=$END,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset slow -crf 17 -profile:v high -level 4.2 -maxrate 20M -bufsize 30M \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -movflags +faststart -c:a aac -b:a 256k -ar 48000 -ac 2 "$OUT"
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height -of compact "$OUT"
