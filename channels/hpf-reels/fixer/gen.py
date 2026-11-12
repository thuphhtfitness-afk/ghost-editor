import json, subprocess, base64, os
D="/tmp/claude-0/-home-user/930efd13-33ee-5335-ac52-4e221b36c4c1/scratchpad/hpf2"
OUT={}
for name,mp4,title in [("H3","/home/user/hpf_3_split_squat_mo_goi.mp4","Bài 1 · Split squat, gối chụm vào"),("H4","/home/user/hpf_4_romanian_deadlift.mp4","Bài 2 · Romanian deadlift")]:
    spec=json.load(open(f"{D}/specs/{name}.json")); rj=json.load(open(f"{D}/specs/reel-{name}/reel.json"))
    tk=[(t["a"],t["b"]) for t in rj["takes"]]
    def et(t):
        acc=0
        for a,b in tk:
            if a-0.02<=t<=b+0.02: return acc+max(0,t-a)
            acc+=b-a
        return None
    assert len(spec["beats"])==len(rj["beats"]),(len(spec["beats"]),len(rj["beats"]))
    beats=[]
    for i,(sb,rb) in enumerate(zip(spec["beats"],rj["beats"])):
        t0=et(rb["at"]); t1=et(rb["to"]) if isinstance(rb.get("to"),(int,float)) else None
        if t0 is None: continue
        if t1 is None: t1=t0+2.5
        mid=min(t0+0.6,(t0+t1)/2)
        jp=f"{D}/ed/{name}_{i}.jpg"
        subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{mid:.2f}","-i",mp4,"-frames:v","1","-vf","scale=216:-1","-q:v","6",jp],check=True)
        img="data:image/jpeg;base64,"+base64.b64encode(open(jp,"rb").read()).decode()
        f={}
        ty=sb["type"]
        if ty in("label","note"): f["text"]=sb["text"]
        if ty=="title": 
            if sb.get("style")=="card": f.update(tag=sb["tag"],big=sb["big"],sub=sb.get("sub",""))
            else: f["text"]=sb["text"]
        if ty=="anatomy": f["title"]=sb.get("title","")
        if ty=="hiprot": f["a_title"]=sb["a"]["title"]; f["b_title"]=sb["b"]["title"]
        if ty=="guide":
            c=[s for s in sb["shapes"] if s["type"]=="circle"]
            if c: f.update(cx=c[0]["cx"],cy=c[0]["cy"],r=c[0]["r"])
        if ty=="glow": f.update(cx=sb["cx"],cy=sb["cy"],rx=sb["rx"],ry=sb["ry"])
        if ty=="fault": f.update(y=sb.get("y",760))
        if ty=="compare2": f["top_label"]=sb["top"]["label"]; f["bottom_label"]=sb["bottom"]["label"]
        beats.append({"i":i,"type":ty,"t0":round(t0,2),"t1":round(t1,2),"f":f,"img":img})
    # caption lines (output time), 6 words per line
    ws=[w for s in json.load(open(f"{D}/specs/reel-{name}/build/words.whisper.json"))["segments"] for w in s.get("words",[])]
    kept=[(w,et(w["start"])) for w in ws if any(a<=w["start"] and w["end"]<=b+0.01 for a,b in tk)]
    caps=[];cur=[]
    for w,t in kept:
        cur.append((w["word"].strip(),t))
        if len(cur)==6: caps.append({"t":round(cur[0][1],1),"text":" ".join(x for x,_ in cur)}); cur=[]
    if cur: caps.append({"t":round(cur[0][1],1),"text":" ".join(x for x,_ in cur)})
    OUT[name]={"title":title,"file":os.path.basename(mp4),"dur":round(sum(b-a for a,b in tk),1),"beats":beats,"caps":caps,"phrases":spec.get("phrases",{})}
    print(name,len(beats),len(caps))
json.dump(OUT,open(f"{D}/ed/data.json","w"),ensure_ascii=False)
print(os.path.getsize(f"{D}/ed/data.json")//1024,"KB")
