#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate AMPET Proposal DOCX + PDF with brand colors 0F5D4A / D4AF37"""
import os, re
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = os.path.dirname(os.path.abspath(__file__))
MD_PATH = os.path.join(BASE, "Proposal.md")
DOCX_PATH = os.path.join(BASE, "AMPET-Proposal.docx")
PDF_PATH = os.path.join(BASE, "AMPET-Proposal.pdf")

PRIMARY_HEX = "0F5D4A"
GOLD_HEX = "D4AF37"
PRIMARY = RGBColor(0x0F, 0x5D, 0x4A)
GOLD = RGBColor(0xD4, 0xAF, 0x37)
BLACK = RGBColor(0x2C, 0x2C, 0x2C)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_BG = "EEF4F2"

def set_cell_shading(cell, color_hex):
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), color_hex)
    shd.set(qn('w:val'), 'clear')
    cell._tc.get_or_add_tcPr().append(shd)

def set_rtl(doc):
    sectPr = doc.sections[0]._sectPr
    rtl = OxmlElement('w:bidi')
    rtl.set(qn('w:val'), 'true')
    sectPr.append(rtl)

def add_para(doc, text, size=11, bold=False, color=BLACK, align=WD_ALIGN_PARAGRAPH.RIGHT):
    p = doc.add_paragraph()
    p.alignment = align
    # handle **bold** inline roughly: strip markers
    clean = text.replace("**", "")
    run = p.add_run(clean)
    run.font.name = 'Vazirmatn'
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return p

def add_heading(doc, text, level):
    clean = text.replace("**", "").strip()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run(clean)
    run.font.name = 'Vazirmatn'
    run.font.bold = True
    if level == 1:
        run.font.size = Pt(18); run.font.color.rgb = PRIMARY
    elif level == 2:
        run.font.size = Pt(14); run.font.color.rgb = PRIMARY
    else:
        run.font.size = Pt(12); run.font.color.rgb = GOLD
    # bottom border accent for h1/h2
    return p

def add_table(doc, headers, rows):
    table = doc.add_table(rows=1+len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        p = cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(h.replace("**","").strip())
        run.font.name = 'Vazirmatn'; run.font.size = Pt(10); run.font.bold = True
        run.font.color.rgb = WHITE
        set_cell_shading(cell, PRIMARY_HEX)
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = table.rows[r+1].cells[c]
            cell.text = ""
            p = cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(val.replace("**","").strip())
            run.font.name = 'Vazirmatn'; run.font.size = Pt(9)
            run.font.color.rgb = BLACK
            if r % 2 == 0:
                set_cell_shading(cell, LIGHT_BG)
    doc.add_paragraph()
    return table

def parse_markdown(md_text):
    lines = md_text.splitlines()
    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1; continue
        # heading
        m = re.match(r'^(#{1,3})\s+(.*)', line)
        if m:
            blocks.append(('h', len(m.group(1)), m.group(2)))
            i += 1; continue
        # table
        if '|' in line and i+1 < len(lines) and re.match(r'^\s*\|?[\s:\-|]+\|?\s*$', lines[i+1]):
            header = [c.strip() for c in line.strip().strip('|').split('|')]
            i += 2
            rows = []
            while i < len(lines) and '|' in lines[i] and lines[i].strip():
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i += 1
            blocks.append(('table', header, rows))
            continue
        # bullet
        if re.match(r'^\s*[-•]\s+', line) or re.match(r'^\s*\d+[\.\)]\s+', line):
            blocks.append(('bullet', re.sub(r'^\s*([-\u2022]|\d+[\.\)])\s+', '', line)))
            i += 1; continue
        # blockquote
        if line.strip().startswith('>'):
            blocks.append(('quote', line.strip().lstrip('>').strip()))
            i += 1; continue
        # hr
        if re.match(r'^\s*---+\s*$', line):
            i += 1; continue
        # paragraph (join consecutive)
        para = line.strip()
        i += 1
        while i < len(lines) and lines[i].strip() and '|' not in lines[i] and not re.match(r'^(#{1,3})\s+', lines[i]) and not re.match(r'^\s*[-•]\s+', lines[i]) and not re.match(r'^\s*\d+[\.\)]\s+', lines[i]):
            para += " " + lines[i].strip()
            i += 1
        blocks.append(('p', para))
    return blocks

def create_docx():
    with open(MD_PATH, encoding='utf-8') as f:
        md = f.read()
    blocks = parse_markdown(md)
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Vazirmatn'
    style.font.size = Pt(11)
    set_rtl(doc)

    # Cover
    for _ in range(5):
        doc.add_paragraph()
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("AMPET"); r.font.name='Vazirmatn'; r.font.size=Pt(48); r.font.bold=True; r.font.color.rgb=PRIMARY
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("سوپر اپلیکیشن خدمات حیوانات خانگی و دامپزشکی"); r.font.name='Vazirmatn'; r.font.size=Pt(20); r.font.bold=True; r.font.color.rgb=GOLD
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("پروپوزال پروژه — اسکوپ، فازبندی، زمان‌بندی و بودجه"); r.font.name='Vazirmatn'; r.font.size=Pt(13); r.font.color.rgb=BLACK
    for _ in range(3):
        doc.add_paragraph()
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("کد رنگ سازمانی:  #0F5D4A  •  #D4AF37"); r.font.name='Vazirmatn'; r.font.size=Pt(10); r.font.color.rgb=BLACK
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("۱۴ مهر ۱۴۰۵ — پیش‌نویس برای بررسی و تأیید"); r.font.name='Vazirmatn'; r.font.size=Pt(10); r.font.color.rgb=BLACK
    doc.add_page_break()

    for b in blocks:
        if b[0] == 'h':
            _, lvl, txt = b
            add_heading(doc, txt, lvl)
        elif b[0] == 'p':
            add_para(doc, b[1])
        elif b[0] == 'quote':
            add_para(doc, b[1], size=10, bold=False, color=PRIMARY)
        elif b[0] == 'bullet':
            add_para(doc, "• " + b[1].replace("**",""))
        elif b[0] == 'table':
            _, hdr, rows = b
            add_table(doc, hdr, rows)

    # Footer sign
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("AMPET  •  0F5D4A  •  D4AF37"); r.font.name='Vazirmatn'; r.font.size=Pt(10); r.font.bold=True; r.font.color.rgb=PRIMARY
    doc.save(DOCX_PATH)
    print(f"DOCX saved: {DOCX_PATH}")

# ---------- PDF ----------
def create_pdf():
    from fpdf import FPDF
    import arabic_reshaper
    from bidi.algorithm import get_display
    FONT_DIR = r"C:\Windows\Fonts"
    FR = os.path.join(FONT_DIR, "Vazirmatn-Regular.ttf")
    FB = os.path.join(FONT_DIR, "Vazirmatn-Bold.ttf")
    PRIM = (15, 93, 74); GLD = (212, 175, 55); BLK=(44,44,44); WHT=(255,255,255); LBG=(238,244,242)

    def fa(t):
        t = t.replace("؟", "?").replace("**","").replace("→", "-").replace("•", "-")
        return "\n".join([get_display(arabic_reshaper.reshape(l)) for l in t.split("\n")])

    with open(MD_PATH, encoding='utf-8') as f:
        md = f.read()
    blocks = parse_markdown(md)

    class PDF(FPDF):
        def header(self):
            if self.page_no() == 1: return
            self.set_fill_color(*PRIM); self.rect(0,0,210,13,"F")
            self.set_text_color(*WHT); self.set_font("Vazir", "B", 8)
            self.set_xy(10,4); self.multi_cell(190,5, fa("AMPET | پروپوزال پروژه"), align="C")
            self.set_text_color(*BLK)
        def footer(self):
            self.set_y(-13); self.set_fill_color(*LBG)
            self.rect(0,self.get_y(),210,13,"F")
            self.set_text_color(*PRIM); self.set_font("Vazir","",7)
            self.set_x(10); self.multi_cell(190,5, fa(f"صفحه {self.page_no()}  •  AMPET  •  0F5D4A / D4AF37"), align="C")

    pdf = PDF()
    pdf.set_auto_page_break(True, 20)
    pdf.add_font("Vazir","",FR); pdf.add_font("Vazir","B",FB)

    # Cover
    pdf.add_page()
    pdf.set_fill_color(*PRIM); pdf.rect(0,0,210,297,"F")
    pdf.set_text_color(*GLD); pdf.set_font("Vazir","B",34); pdf.set_y(70)
    pdf.set_x(10); pdf.multi_cell(190,14, fa("AMPET"), align="C")
    pdf.set_text_color(*WHT); pdf.set_font("Vazir","B",15)
    pdf.set_x(10); pdf.multi_cell(190,10, fa("سوپر اپلیکیشن خدمات حیوانات خانگی و دامپزشکی"), align="C")
    pdf.ln(4)
    pdf.set_text_color(*GLD); pdf.set_font("Vazir","B",12)
    pdf.set_x(10); pdf.multi_cell(190,8, fa("پروپوزال پروژه"), align="C")
    pdf.set_text_color(*WHT); pdf.set_font("Vazir","",10)
    pdf.set_x(10); pdf.multi_cell(190,7, fa("اسکوپ، فازبندی، زمان‌بندی و بودجه"), align="C")
    pdf.ln(10)
    # gold divider
    pdf.set_fill_color(*GLD); pdf.rect(80,pdf.get_y(),50,2,"F"); pdf.ln(8)
    pdf.set_text_color(220,220,220); pdf.set_font("Vazir","",9)
    pdf.set_x(10); pdf.multi_cell(190,7, fa("#0F5D4A  •  #D4AF37"), align="C")
    pdf.set_x(10); pdf.multi_cell(190,7, fa("۱۴ مهر ۱۴۰۵"), align="C")

    def h1(t):
        pdf.ln(2)
        pdf.set_fill_color(*PRIM); y=pdf.get_y()
        pdf.set_font("Vazir","B",13); pdf.set_text_color(*WHT)
        pdf.rect(10,y,190,11,"F"); pdf.set_xy(10,y+2)
        pdf.multi_cell(190,7, fa(t), align="C"); pdf.set_text_color(*BLK); pdf.ln(4)
    def h2(t):
        pdf.set_fill_color(*LBG); y=pdf.get_y()
        pdf.set_font("Vazir","B",11); pdf.set_text_color(*PRIM)
        pdf.rect(10,y,190,9,"F"); pdf.set_xy(10,y+1.5)
        pdf.multi_cell(190,6, fa(t), align="C"); pdf.set_text_color(*BLK); pdf.ln(3)
    def h3(t):
        pdf.set_font("Vazir","B",10); pdf.set_text_color(150,130,40)
        pdf.multi_cell(0,6, fa(t), align="R"); pdf.set_text_color(*BLK); pdf.ln(1)
    def para(t):
        pdf.set_font("Vazir","",9); pdf.set_text_color(*BLK)
        pdf.multi_cell(0,6, fa(t), align="R"); pdf.ln(2)
    def bullet(t):
        pdf.set_font("Vazir","",9); pdf.set_text_color(*BLK)
        x=pdf.get_x()
        pdf.multi_cell(0,6, fa("• "+t), align="R"); pdf.ln(1)
    def table(hdr, rows):
        n=len(hdr); W=190; cw=[W/n]*n
        pdf.set_fill_color(*PRIM); pdf.set_text_color(*WHT); pdf.set_font("Vazir","B",8)
        for i,h in enumerate(hdr):
            pdf.cell(cw[i],8, fa(h), align="C", border=1, fill=True)
        pdf.ln(); pdf.set_text_color(*BLK); pdf.set_font("Vazir","",7.5)
        fill=False
        for row in rows:
            if pdf.get_y()>250: pdf.add_page()
            # pad row
            row = list(row)+[""]*(n-len(row))
            maxh=7
            if fill: pdf.set_fill_color(*LBG)
            for i,c in enumerate(row):
                pdf.cell(cw[i],maxh, fa(str(c))[:120], align="C", border=1, fill=fill)
            pdf.ln(); fill=not fill
        pdf.ln(4)

    for b in blocks:
        if pdf.get_y()>265: pdf.add_page()
        if b[0]=='h':
            _,lvl,txt=b
            txt=txt.replace("**","").strip()
            if lvl==1: h1(txt)
            elif lvl==2: h2(txt)
            else: h3(txt)
        elif b[0]=='p': para(b[1])
        elif b[0]=='quote':
            pdf.set_font("Vazir","",8.5); pdf.set_text_color(*PRIM)
            pdf.multi_cell(0,6, fa(b[1]), align="R"); pdf.set_text_color(*BLK); pdf.ln(2)
        elif b[0]=='bullet': bullet(b[1])
        elif b[0]=='table': table(b[1], b[2])

    pdf.output(PDF_PATH)
    print(f"PDF saved: {PDF_PATH}")

if __name__ == "__main__":
    create_docx()
    create_pdf()
