from pathlib import Path
p=Path('scripts/build_report.py');s=p.read_text(encoding='utf-8')
s=s.replace("fontSize=12,leading=18,spaceAfter=11", "fontSize=12,leading=16,spaceAfter=9")
s=s.replace("fontSize=17,leading=22,spaceAfter=18", "fontSize=17,leading=22,spaceAfter=15")
s=s.replace("('TOPPADDING',(0,0),(-1,-1),7)","('TOPPADDING',(0,0),(-1,-1),5)")
s=s.replace("('BOTTOMPADDING',(0,0),(-1,-1),7)","('BOTTOMPADDING',(0,0),(-1,-1),5)")
s=s.replace("ratio=w/image.imageWidth", "ratio=min(w/image.imageWidth, 310/image.imageHeight); w=image.imageWidth*ratio")
s=s.replace("qa.mkdir(exist_ok=True)\n    info=[]", "qa.mkdir(exist_ok=True)\n    for old_page in qa.glob('page-*.png'): old_page.unlink()\n    info=[]")
p.write_text(s,encoding='utf-8')
