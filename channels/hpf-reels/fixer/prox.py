import json, subprocess, os, shutil
D="/tmp/claude-0/-home-user/930efd13-33ee-5335-ac52-4e221b36c4c1/scratchpad"
for name in ["H3","H4"]:
    spec=json.load(open(f"{D}/hpf2/specs/{name}.json")); rj=json.load(open(f"{D}/hpf2/specs/reel-{name}/reel.json"))
    src=os.path.realpath(f"{D}/hpf2/specs/reel-{name}/assets/talk.mp4")
    tk=[(t["a"],t["b"]) for t in rj["takes"]]
    ox,oy=[float(x.strip('%'))/100 for x in spec.get("origin","50% 60%").split()]
    tmp=f"{D}/hpf2/ed/pt_{name}"; shutil.rmtree(tmp,ignore_errors=True); os.makedirs(tmp)
    lst=open(f"{tmp}/l.txt","w")
    for i,(a,b) in enumerate(tk):
        z=1.08 if i%2 else 1.0
        w=int(1080/z)//2*2; h=int(1920/z)//2*2; x=int((1080-w)*ox); y=int((1920-h)*oy)
        subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{max(0,a-1):.3f}","-i",src,"-ss","1" if a>=1 else f"{a:.3f}","-t",f"{b-a:.3f}","-vf",f"crop={w}:{h}:{x}:{y},scale=360:640,fps=24","-c:v","libx264","-preset","veryfast","-crf","31","-pix_fmt","yuv420p","-g","24","-c:a","aac","-b:a","56k","-ac","1","-ar","44100",f"{tmp}/{i:02d}.mp4"],check=True)
        lst.write(f"file '{tmp}/{i:02d}.mp4'\n")
    lst.close()
    subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i",f"{tmp}/l.txt","-c","copy","-movflags","+faststart",f"{D}/hpf2/ed/{name}_clean.mp4"],check=True)
    shutil.rmtree(tmp)
    d=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"{D}/hpf2/ed/{name}_clean.mp4"],capture_output=True,text=True).stdout)
    print(name,round(os.path.getsize(f"{D}/hpf2/ed/{name}_clean.mp4")/1e6,1),"MB",round(d,1),"s vs",round(sum(b-a for a,b in tk),1))
