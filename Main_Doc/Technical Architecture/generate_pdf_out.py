import os, re
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display

BASE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(BASE, "Technical-Architecture.md")
PDF_OUT = os.path.join(BASE, "Technical-Architecture.pdf")

FONT_DIR = r"C:\Windows\Fonts"
FONT_REG = os.path.join(FONT_DIR, "Vazirmatn-Regular.ttf")
FONT_BOLD = os.path.join(FONT_DIR, "Vazirmatn-Bold.ttf")

PRIMARY = (15, 93, 74)      # 0F5D4A
GOLD = (212, 175, 55)       # D4AF37
LIGHT = (238, 243, 241)
BLACK = (34, 34, 34)
WHITE = (255, 255, 255)
GRAY = (120, 120, 120)

def fa(text):
    text = str(text).replace("؟", "?").replace("→", " > ").replace("←", " < ").replace("—", "-")
    lines = text.split("\n")
    return "\n".join(get_display(arabic_reshaper.reshape(line)) for line in lines)

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        self.add_font("Vazirmatn", "", FONT_REG)
        self.add_font("Vazirmatn", "B", FONT_BOLD)
    def header(self):
        if self.page_no() <= 1:
            return
        self.set_fill_color(*PRIMARY)
        self.rect(0, 0, 210, 13, "F")
        self.set_text_color(*WHITE)
        self.set_font("Vazirmatn", "B", 8)
        self.set_xy(10, 4)
        self.cell(0, 5, fa("AMPET | معماری فنی"), align="C")
        self.set_text_color(*BLACK)
        self.ln(18)
    def footer(self):
        self.set_y(-15)
        self.set_text_color(*PRIMARY)
        self.set_font("Vazirmatn", "", 7)
        self.cell(0, 5, fa(f"صفحه {self.page_no()}"), align="C")
        self.set_text_color(*BLACK)
    def h1(self, t):
        self.set_fill_color(*PRIMARY)
        x, y = 10, self.get_y()
        self.rect(x, y, 190, 11, "F")
        self.set_text_color(*WHITE)
        self.set_font("Vazirmatn", "B", 12)
        self.set_xy(x+5, y+1.5)
        self.multi_cell(180, 8, fa(t), align="R")
        self.set_text_color(*BLACK)
        self.ln(4)
    def h2(self, t):
        self.set_fill_color(*LIGHT)
        self.set_draw_color(*PRIMARY)
        x, y0 = 10, self.get_y()
        self.rect(x, y0, 190, 9, "DF")
        # gold accent bar on right
        self.set_fill_color(*GOLD)
        self.rect(196, y0, 4, 9, "F")
        self.set_text_color(*PRIMARY)
        self.set_font("Vazirmatn", "B", 10)
        self.set_xy(x+5, y0+1)
        self.multi_cell(180, 7, fa(t), align="R")
        self.set_text_color(*BLACK)
        self.ln(3)
    def h3(self, t):
        self.set_text_color(*GOLD)
        self.set_font("Vazirmatn", "B", 10)
        self.multi_cell(0, 7, fa(t), align="R")
        self.set_text_color(*BLACK)
        self.ln(1)
    def body(self, t):
        self.set_font("Vazirmatn", "", 9)
        self.set_text_color(*BLACK)
        self.multi_cell(0, 6, fa(t), align="R")
        self.ln(1.5)
    def bullet(self, t):
        self.set_font("Vazirmatn", "", 9)
        self.set_text_color(*BLACK)
        self.multi_cell(0, 6, fa("• " + t), align="R")
        self.ln(1)
    def table(self, headers, rows):
        n = len(headers)
        cw = [190/n]*n
        # check page break: rough estimate
        if self.get_y() + 10 + 7*min(len(rows)+1, 8) > 270:
            self.add_page()
        self.set_fill_color(*PRIMARY)
        self.set_text_color(*WHITE)
        self.set_font("Vazirmatn", "B", 7.5)
        # RTL: reverse display order
        hdr = list(reversed(headers))
        cwr = list(reversed(cw))
        for i, h in enumerate(hdr):
            self.cell(cwr[i], 8, fa(h), align="C", border=1, fill=True)
        self.ln()
        self.set_text_color(*BLACK)
        self.set_font("Vazirmatn", "", 7.5)
        fill = False
        for row in rows:
            # pad row
            r = list(row) + [""]*(n-len(row))
            r = list(reversed(r))
            max_lines = 1
            # simple fixed height
            h = 7
            if self.get_y() + h > 275:
                self.add_page()
            if fill:
                self.set_fill_color(*LIGHT)
            for i, c in enumerate(r):
                self.cell(cwr[i], h, fa(c)[:90], align="C", border=1, fill=fill)
            self.ln()
            fill = not fill
        self.ln(4)

def is_sep(l):
    return bool(re.match(r'^\s*\|?[\s:\-|]+\|?\s*$', l)) and '-' in l

with open(MD, encoding="utf-8") as f:
    lines = f.read().splitlines()

pdf = PDF()
pdf.add_page()
# Cover
pdf.set_fill_color(*PRIMARY)
pdf.rect(0, 0, 210, 297, "F")
pdf.set_text_color(*GOLD)
pdf.set_font("Vazirmatn", "B", 30)
pdf.set_y(60)
pdf.cell(0, 15, fa("AMPET"), align="C")
pdf.ln(15)
pdf.set_text_color(*WHITE)
pdf.set_font("Vazirmatn", "B", 18)
pdf.cell(0, 12, fa("معماری فنی"), align="C")
pdf.ln(12)
pdf.set_font("Vazirmatn", "", 11)
pdf.cell(0, 8, fa("نسخه ۱٫۰ — ۱۴۰۵/۰۷/۱۴"), align="C")
pdf.ln(10)
pdf.set_text_color(*GOLD)
pdf.set_font("Vazirmatn", "B", 10)
pdf.cell(0, 8, fa("0F5D4A  •  D4AF37"), align="C")
pdf.ln(10)
pdf.set_text_color(*WHITE)
pdf.set_font("Vazirmatn", "", 9)
pdf.multi_cell(0, 7, fa("مرجع: project-document.md + وایرفریم‌های ۲۸گانه\nمبنای قرارداد و پذیرش فنی"), align="C")

i = 0
while i < len(lines):
    line = lines[i].rstrip()
    if not line.strip():
        i += 1
        continue
    m = re.match(r'^(#{1,3})\s+(.*)', line)
    if m:
        lvl = len(m.group(1))
        txt = m.group(2).strip()
        if pdf.get_y() > 260:
            pdf.add_page()
        if lvl == 1:
            pdf.add_page()
            pdf.h1(txt)
        elif lvl == 2:
            pdf.h2(txt)
        else:
            pdf.h3(txt)
        i += 1
        continue
    if line.strip().startswith('|') and i+1 < len(lines) and is_sep(lines[i+1]):
        headers = [c.strip() for c in line.strip().strip('|').split('|')]
        i += 2
        rows = []
        while i < len(lines) and lines[i].strip().startswith('|'):
            rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
            i += 1
        pdf.table(headers, rows)
        continue
    if line.strip().startswith('>'):
        pdf.set_text_color(*PRIMARY)
        pdf.body(line.strip().lstrip('>').strip())
        pdf.set_text_color(*BLACK)
        i += 1
        continue
    if re.match(r'^\s*([-\*]|\d+[.)])\s+', line):
        t = re.sub(r'^\s*([-\*]|\d+[.)])\s+', '', line).strip()
        pdf.bullet(t)
        i += 1
        continue
    if re.match(r'^\s*---+\s*$', line):
        pdf.ln(2)
        pdf.set_draw_color(*GOLD)
        pdf.line(80, pdf.get_y(), 130, pdf.get_y())
        pdf.ln(4)
        i += 1
        continue
    if line.strip().startswith('```'):
        i += 1
        while i < len(lines) and not lines[i].strip().startswith('```'):
            pdf.set_font("Courier", "", 8)
            pdf.body(lines[i])
            i += 1
        i += 1
        continue
    pdf.body(line.strip())
    i += 1

pdf.output(PDF_OUT)
print(f"PDF saved: {PDF_OUT}")
