import cv2, sys, json
src, a, b = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
cap=cv2.VideoCapture(src); fps=cap.get(5)
FW,FH=int(cap.get(3)),int(cap.get(4)); K=960/max(FW,FH); SW,SH=int(FW*K),int(FH*K)
d=cv2.FaceDetectorYN.create(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),'..','..','library','models','face_detection_yunet_2023mar.onnx'),'',(SW,SH),0.6)
REF=tuple(map(float,sys.argv[5].split(','))) if len(sys.argv)>5 else (750,650)
MINH=float(sys.argv[6]) if len(sys.argv)>6 else 110
prev=None; out=[]
t=a
while t<=b:
    cap.set(cv2.CAP_PROP_POS_MSEC,t*1000); ok,f=cap.read()
    if not ok: break
    _,fs=d.detect(cv2.resize(f,(SW,SH)))
    c=[((x+w/2)/K,(y+h/2)/K,h/K) for x,y,w,h,*_ in (fs if fs is not None else []) if h/K>MINH]
    if c:
        # coach = nearest to previous, else the one closest to x=750 (or largest after the pan)
        ref = prev or REF
        p = min(c, key=lambda q:(q[0]-ref[0])**2+(q[1]-ref[1])**2)
        if prev is None or abs(p[0]-prev[0])<260: prev=(p[0],p[1])
    out.append([round(t,2), round(prev[0]), round(prev[1])] if prev else [round(t,2),None,None])
    t+=0.5
json.dump(out, open(sys.argv[4],"w")); print(out[::6])
