"""Speech islands (silero VAD via faster-whisper) for the silence cut: vad.py wav/<clip>.wav build/vad_<clip>.json"""
import sys, wave, json, numpy as np
from faster_whisper.vad import get_speech_timestamps, VadOptions
w = wave.open(sys.argv[1]); a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
ts = get_speech_timestamps(a, VadOptions(threshold=0.45, min_silence_duration_ms=180, speech_pad_ms=40, min_speech_duration_ms=120))
json.dump([(t["start"] / 16000, t["end"] / 16000) for t in ts], open(sys.argv[2], "w"))
