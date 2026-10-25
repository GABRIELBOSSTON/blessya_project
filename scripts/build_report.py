"""Render laporan lima BAB; isi dan data berada pada report_content.py.

Tooling terpisah dari aplikasi: ReportLab, PyMuPDF, font Times New Roman.
"""
from pathlib import Path
import hashlib
import json
import math
import sys
from xml.sax.saxutils import escape

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tools/packages'))
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, Preformatted, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
import pymupdf
from report_content import chapters, REFERENCES, IDENTITAS, PREFACE, ABSTRACT

WIDTH=A4[0]-128


class ReportDoc(SimpleDocTemplate):
    def afterFlowable(self,flowable):
        mark=getattr(flowable,'report_mark',None)
        if mark:
            level,title=mark
            self.marks.append({'level':level,'title':title,'page':self.page})


def process_states():
    """Diagram vektor baru untuk model keadaan umum; bukan screenshot aplikasi."""
    d=Drawing(WIDTH,270)
    ink=colors.HexColor('#244d43')
    def box(x,y,w,title):
        d.add(Rect(x,y,w,36,rx=5,ry=5,fillColor=colors.HexColor('#eef5f1'),strokeColor=ink))
        d.add(String(x+w/2,y+13,title,fontName='Bold',fontSize=11,textAnchor='middle'))
    def arrow(points,label=None,at=None):
        for a,b in zip(points,points[1:]):d.add(Line(*a,*b,strokeColor=ink,strokeWidth=1))
        x,y=points[-1];px,py=points[-2];angle=math.atan2(y-py,x-px)
        poly=[x,y,x-6*math.cos(angle-.5),y-6*math.sin(angle-.5),x-6*math.cos(angle+.5),y-6*math.sin(angle+.5)]
        d.add(Polygon(poly,fillColor=ink,strokeColor=ink))
        if label:d.add(String(*at,label,fontName='Body',fontSize=9,textAnchor='middle'))
    box(0,180,70,'New');box(145,180,80,'Ready');box(310,180,90,'Running')
    box(145,10,90,'Waiting');box(310,10,105,'Terminated')
    arrow([(70,198),(145,198)],'dibentuk',(108,210))
    arrow([(225,198),(310,198)],'dipilih',(268,210))
    arrow([(355,216),(355,250),(185,250),(185,216)],'quantum habis / dipotong',(270,260))
    arrow([(340,180),(340,120),(190,120),(190,46)],'menunggu I/O',(265,132))
    arrow([(165,46),(165,180)],'I/O selesai',(119,95))
    arrow([(385,180),(385,46)],'selesai',(416,95))
    return d


def setup_styles():
    fontdir=Path('C:/Windows/Fonts')
    for name,file in [('Body','times.ttf'),('Bold','timesbd.ttf'),('Italic','timesi.ttf')]:
        pdfmetrics.registerFont(TTFont(name,str(fontdir/file)))
    pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold',italic='Italic',boldItalic='Bold')
    styles=getSampleStyleSheet()
    definitions=[
        dict(name='Text',fontName='Body',fontSize=12,leading=16.5,spaceAfter=7,alignment=TA_JUSTIFY,allowWidows=0,allowOrphans=0),
        dict(name='Chapter',fontName='Bold',fontSize=17,leading=23,spaceAfter=20,keepWithNext=True),
        dict(name='Subhead',fontName='Bold',fontSize=13,leading=18,spaceBefore=14,spaceAfter=9,keepWithNext=True),
        dict(name='Caption',fontName='Italic',fontSize=10,leading=14,spaceBefore=7,spaceAfter=12,alignment=TA_CENTER),
        dict(name='Cell',fontName='Body',fontSize=10.5,leading=14),
        dict(name='CellHead',fontName='Bold',fontSize=10.5,leading=14,textColor=colors.white),
        dict(name='Cover',fontName='Bold',fontSize=23,leading=31,alignment=TA_CENTER,spaceAfter=25),
        dict(name='Centered',fontName='Body',fontSize=13,leading=21,alignment=TA_CENTER,spaceAfter=18),
        dict(name='CodeLocal',fontName='Courier',fontSize=9,leading=13,spaceBefore=6,spaceAfter=14),
        dict(name='Toc',fontName='Body',fontSize=10.5,leading=13),
    ]
    for definition in definitions:styles.add(ParagraphStyle(**definition))
    return styles


def render():
    styles=setup_styles()
    out=ROOT/'output/pdf/Laporan-Simulator-Sistem-Operasi.pdf'
    out.parent.mkdir(parents=True,exist_ok=True)
    toc=[]
    for chapter,subsections in chapters:
        toc.append((0,chapter))
        toc.extend((1,title) for title,_ in subsections)
    toc.append((0,'DAFTAR PUSTAKA'))
    pages={title:0 for _,title in toc}
    def heading(title,level):
        paragraph=Paragraph(escape(title),styles['Chapter' if level==0 else 'Subhead'])
        paragraph.report_mark=(level,title)
        return paragraph
    def footer(canvas,doc):
        if doc.page==1:return
        canvas.saveState();canvas.setFont('Body',9);canvas.setFillColor(colors.HexColor('#555555'))
        canvas.drawString(72,A4[1]-37,'Simulator Penjadwalan CPU dan Producer-Consumer')
        canvas.drawCentredString(A4[0]/2,32,str(doc.page));canvas.restoreState()
    def block_flow(block):
        kind=block[0]
        if kind=='p':return [Paragraph(escape(block[1]),styles['Text'])]
        if kind=='code':return [KeepTogether([Preformatted(block[1],styles['CodeLocal'],maxLineLength=79)])]
        if kind=='diagram':return [KeepTogether([process_states(),Paragraph(escape(block[2]),styles['Caption'])])]
        if kind=='image':
            picture=Image(str(ROOT/'docs/evidence'/block[1]))
            ratio=min(WIDTH/picture.imageWidth,310/picture.imageHeight)
            picture.drawWidth=picture.imageWidth*ratio;picture.drawHeight=picture.imageHeight*ratio
            return [KeepTogether([picture,Paragraph(escape(block[2]),styles['Caption'])])]
        if kind=='table':
            headers,rows=block[1:];n=len(headers)
            if n==2:widths=[WIDTH*.36,WIDTH*.64]
            elif n==3:widths=[WIDTH*.28,WIDTH*.36,WIDTH*.36]
            else:widths=[WIDTH/n]*n
            cells=[[Paragraph(escape(str(v)),styles['CellHead' if i==0 else 'Cell']) for v in row] for i,row in enumerate([headers]+rows)]
            t=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
            t.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#254b42')),
                ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f3f6f4')]),
                ('GRID',(0,0),(-1,-1),.4,colors.HexColor('#d9d9d9')),
                ('VALIGN',(0,0),(-1,-1),'TOP'),
                ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
                ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7)]))
            return [t,Spacer(1,12)]
        raise ValueError(kind)

    for iteration in range(4):
        identity=[f"Nama: {escape(IDENTITAS['nama'])}",f"NIM: {escape(IDENTITAS['nim'])}",f"Kelas: {escape(IDENTITAS['kelas'])}"]
        for key,label in [('program_studi','Program studi'),('fakultas','Fakultas'),('institusi','Institusi'),('dosen','Dosen pengampu')]:
            if IDENTITAS.get(key):identity.append(label+': '+escape(IDENTITAS[key]))
        story=[Spacer(1,53),Paragraph('Simulator Edukasi<br/>Penjadwalan CPU dan<br/>Sinkronisasi Producer-Consumer',styles['Cover']),
            Paragraph('Laporan Tugas '+escape(IDENTITAS['nama_tugas']),styles['Centered']),Spacer(1,18),
            Paragraph('Process Scheduling<br/>IPC &amp; Classical Problems',styles['Centered']),Spacer(1,47),
            Paragraph('<br/>'.join(identity),styles['Centered']),Spacer(1,24),Paragraph('2026',styles['Centered']),
            PageBreak(),Paragraph('KATA PENGANTAR',styles['Chapter'])]
        story.extend(Paragraph(escape(t),styles['Text']) for t in PREFACE)
        story.extend([Spacer(1,20),Paragraph('Blessya',styles['Text']),PageBreak(),Paragraph('ABSTRAK',styles['Chapter'])])
        story.extend(Paragraph(escape(t),styles['Text']) for t in ABSTRACT)
        story.extend([PageBreak(),Paragraph('DAFTAR ISI',styles['Chapter'])])
        rows=[]
        for level,title in toc:
            prefix='&nbsp;&nbsp;&nbsp;' if level else ''
            label=escape(title) if level else '<b>'+escape(title)+'</b>'
            rows.append([Paragraph(prefix+label,styles['Toc']),str(pages[title]) if pages[title] else ''])
        table=Table(rows,colWidths=[WIDTH-30,30])
        table.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'Body'),('FONTSIZE',(0,0),(-1,-1),10.5),('ALIGN',(1,0),(1,-1),'RIGHT'),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),1.5),('BOTTOMPADDING',(0,0),(-1,-1),1.5),('LEFTPADDING',(0,0),(-1,-1),0)]))
        story.append(table)
        for chapter,subsections in chapters:
            story.extend([PageBreak(),heading(chapter,0)])
            for title,blocks in subsections:
                story.append(heading(title,1))
                for block in blocks:story.extend(block_flow(block))
        story.extend([PageBreak(),heading('DAFTAR PUSTAKA',0)])
        for number,author,title,url in REFERENCES:
            access='24 Oktober 2026' if int(number)<=6 else '25 Oktober 2026'
            story.append(Paragraph(f'[{number}] {escape(author)}. <i>{escape(title)}</i>. Diakses {access}.<br/><link href="{url}" color="#175e50">{url}</link>',styles['Text']))
        doc=ReportDoc(str(out),pagesize=A4,leftMargin=64,rightMargin=64,topMargin=63,bottomMargin=57,
            title='Simulator Edukasi Penjadwalan CPU dan Sinkronisasi Producer-Consumer',author=IDENTITAS['nama'])
        doc.marks=[];doc.build(story,onFirstPage=footer,onLaterPages=footer)
        updated={entry['title']:entry['page'] for entry in doc.marks}
        if updated==pages:break
        pages=updated
    else:raise RuntimeError('Daftar isi belum stabil setelah empat render')

    md=['# Simulator Edukasi Penjadwalan CPU dan Sinkronisasi Producer-Consumer','',
        'Laporan Tugas '+IDENTITAS['nama_tugas'],'',
        'Nama: '+IDENTITAS['nama']+'  \nNIM: '+IDENTITAS['nim']+'  \nKelas: '+IDENTITAS['kelas'],'',
        '## Kata Pengantar','']
    # Tambahkan identitas yang diberikan pada salinan Markdown juga.
    for key,label in [('program_studi','Program studi'),('fakultas','Fakultas'),('institusi','Institusi'),('dosen','Dosen pengampu')]:
        if IDENTITAS.get(key):md.insert(-2,label+': '+IDENTITAS[key]+'  ')
    md.insert(md.index('## Kata Pengantar'),'')
    md.extend('\n\n'.join(PREFACE).splitlines());md.extend(['','## Abstrak','','\n\n'.join(ABSTRACT),''])
    for chapter,subsections in chapters:
        md.extend(['## '+chapter,''])
        for title,blocks in subsections:
            md.extend(['### '+title,''])
            for block in blocks:
                if block[0]=='p':md.extend([block[1],''])
                elif block[0]=='code':md.extend(['```text',block[1],'```',''])
                elif block[0]=='image':md.extend([f'![{block[2]}](evidence/{block[1]})',''])
                elif block[0]=='diagram':md.extend(['```mermaid','stateDiagram-v2','    [*] --> New','    New --> Ready','    Ready --> Running: dipilih','    Running --> Ready: dipotong','    Running --> Waiting: I/O','    Waiting --> Ready: I/O selesai','    Running --> Terminated: selesai','```',block[2],''])
                elif block[0]=='table':
                    h,rows=block[1:];md.extend(['| '+' | '.join(h)+' |','|'+'---|'*len(h)])
                    md.extend('| '+' | '.join(str(v) for v in row)+' |' for row in rows);md.append('')
    md.extend(['## DAFTAR PUSTAKA',''])
    for number,author,title,url in REFERENCES:
        access='24 Oktober 2026' if int(number)<=6 else '25 Oktober 2026'
        md.extend([f'[{number}] {author}. [{title}]({url}). Diakses {access}.',''])
    (ROOT/'docs/LAPORAN.md').write_text('\n'.join(md),encoding='utf-8')
    pdf=pymupdf.open(out);qa=ROOT/'docs/evidence/report-pages';qa.mkdir(exist_ok=True)
    for old in qa.glob('page-*.png'):old.unlink()
    details=[]
    for i,page in enumerate(pdf):
        page.get_pixmap(matrix=pymupdf.Matrix(1.3,1.3)).save(str(qa/f'page-{i+1:02}.png'))
        details.append({'page':i+1,'words':len(page.get_text().split()),'text_start':page.get_text()[:110]})
    first=pages[chapters[0][0]];last=pages['DAFTAR PUSTAKA']-1
    result={'pages':len(pdf),'chapters':len(chapters),'body_pages':last-first+1,
            'body_page_range':[first,last],'toc':pages,'page_details':details,
            'pdf_sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
    (ROOT/'docs/evidence/report-check.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2));pdf.close()
    assert result['body_pages']>=20, 'Isi laporan belum memenuhi minimum 20 halaman'


if __name__=='__main__':render()
