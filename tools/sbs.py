import sys
from PIL import Image, ImageDraw, ImageFont, ImageChops
a,b,out=sys.argv[1:4]
A=Image.open(a).convert('RGB');B=Image.open(b).convert('RGB')
H=max(A.height,B.height);pad=20;top=50
im=Image.new('RGB',(A.width+B.width+pad*3,H+top+pad),'white')
d=ImageDraw.Draw(im)
try: f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',max(12,min(26,A.width//22)))
except: f=ImageFont.load_default()
d.text((pad,12),'ORIGINAL' if A.width<600 else 'ORIGINAL  gate2024.iisc.ac.in',fill=(0,80,89),font=f)
d.text((A.width+pad*2,12),'CLONE' if A.width<600 else 'CLONE  localhost:8080',fill=(190,161,80),font=f)
im.paste(A,(pad,top));im.paste(B,(A.width+pad*2,top))
im.save(out)
# similarity on overlapping region
h=min(A.height,B.height);w=min(A.width,B.width)
diff=ImageChops.difference(A.crop((0,0,w,h)),B.crop((0,0,w,h))).convert('L')
hist=diff.histogram();px=sum(hist[41:])
print(f'{out}: size orig={A.size} clone={B.size} differing_px={px/(w*h)*100:.2f}%')
