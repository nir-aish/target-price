import re, json, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

F="/tmp/dwfx/dwf/documents/9A16333D-5016-4BB4-99E5-6D16BFE3DFD7/sections/com.autodesk.dwf.ePlot_C1B1EC69-5460-41D7-A2D2-A93ECB77E4A3/FixedPage.fpage"
data=open(F,encoding='utf-8',errors='replace').read()
NUM=r'-?\d+(?:\.\d+)?(?:[eE]-?\d+)?'
PATH=re.compile(r'<Path\b[^>]*?Data="([^"]*)"[^>]*?/>')
ATTR=re.compile(r'(?:Stroke|Fill)="(#[0-9A-Fa-f]+)"')
def pp(d):
    toks=re.findall(r'[MmLlHhVvCcAaZz]|'+NUM,d);P=[];x=y=0.;i=0;c=None
    while i<len(toks):
        t=toks[i]
        if t.isalpha():c=t;i+=1
        if i>=len(toks):break
        if c in('M','L'):x=float(toks[i]);y=float(toks[i+1]);i+=2;P.append((x,y))
        elif c in('m','l'):x+=float(toks[i]);y+=float(toks[i+1]);i+=2;P.append((x,y))
        elif c=='H':x=float(toks[i]);i+=1;P.append((x,y))
        elif c=='h':x+=float(toks[i]);i+=1;P.append((x,y))
        elif c=='V':y=float(toks[i]);i+=1;P.append((x,y))
        elif c=='v':y+=float(toks[i]);i+=1;P.append((x,y))
        elif c in('Z','z'):pass
        else:
            j=i
            while j<len(toks) and not toks[j].isalpha():j+=1
            i=j
    return P
# collect blue segments
blue=[]
for m in PATH.finditer(data):
    seg=data[max(0,m.start()-160):m.start()+60]
    cols=ATTR.findall(m.group(0)) or ATTR.findall(seg)
    if not cols: continue
    if cols[0].upper() not in ('#007FFF','#0080FF'): continue
    P=pp(m.group(1))
    if len(P)>=2: blue.append(P)
print("blue polylines",len(blue))

# one square window (flat coords) - B2 floor3 top row
x0,x1,y0,y1=411000,434500,2500,19500
res=8.0
W=int((x1-x0)/res); H=int((y1-y0)/res)
im=Image.new('L',(W,H),0); dr=ImageDraw.Draw(im)
for P in blue:
    if not any(x0-2000<=px<=x1+2000 and y0-2000<=py<=y1+2000 for px,py in P): continue
    pts=[((px-x0)/res,(py-y0)/res) for px,py in P]
    dr.line(pts,fill=255,width=2)
arr=(np.asarray(im)>0).astype(np.uint8)
print("blue filled px",int(arr.sum()))
# bridge dashed gaps
for it in [2,3,4,5]:
    d=ndi.binary_closing(ndi.binary_dilation(arr,iterations=it),iterations=it)
    lbl,n=ndi.label(~d)
    border=set(np.unique(np.concatenate([lbl[0],lbl[-1],lbl[:,0],lbl[:,-1]])))
    cnt=np.bincount(lbl.ravel())
    areas=sorted([round(cnt[i]*(res/1000)**2,1) for i in range(1,n+1) if i not in border and 20<cnt[i]*(res/1000)**2<340],reverse=True)
    print("dilate/close=%d -> cells=%d areas=%s"%(it,len(areas),areas))
