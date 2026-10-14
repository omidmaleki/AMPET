# -*- coding: utf-8 -*-
"""
AMPET - Wireframe image generator.
Renders RTL Persian mobile-screen wireframes as PNG using Pillow.
Output: ./wireframes/*.png
"""
import os
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
# wireframes are documentation assets → kept under Main_Doc/wireframes (repo-relative)
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "Main_Doc", "wireframes"))
os.makedirs(OUT, exist_ok=True)

FONT_DIR = r"C:\Windows\Fonts"

# ---------------- geometry ----------------
SW, SH = 720, 1560          # screen
M = 20                      # canvas margin
CW, CH = SW + 2 * M, SH + 2 * M
IL, IR = 30, SW - 30        # inner content margins

# ---------------- palette ----------------
INK = "#16213E"
SUB = "#7A8496"
LINE = "#D7DCE4"
BOX = "#F3F5F8"
BRAND = "#0E7C66"
BRAND_SOFT = "#E6F4F0"
GOLD = "#C9A96E"
GOLD_SOFT = "#FAF3E4"
RED = "#C0392B"
RED_SOFT = "#FDECEA"
BLUE_SOFT = "#E9F0FE"
WHITE = "#FFFFFF"

_fcache = {}


def font(size, weight="Regular"):
    key = (size, weight)
    if key not in _fcache:
        path = os.path.join(FONT_DIR, "Vazirmatn-%s.ttf" % weight)
        if not os.path.exists(path):
            path = os.path.join(FONT_DIR, "Vazirmatn-Regular.ttf")
        _fcache[key] = ImageFont.truetype(path, int(size))
    return _fcache[key]


_reshaper = arabic_reshaper.ArabicReshaper({"delete_harakat": True,
                                            "support_ligatures": True})


def fa(s):
    s = str(s)
    try:
        return get_display(_reshaper.reshape(s))
    except Exception:
        return s


# ======================================================================
#  Phone screen engine
# ======================================================================
class Phone:
    def __init__(self, title=None, back=True, right_text=None, left_icon=None):
        self.scr = Image.new("RGB", (SW, SH), WHITE)
        self.d = ImageDraw.Draw(self.scr)
        self.y = 0
        self._statusbar()
        if title:
            self.navbar(title, back=back, right_text=right_text, left_icon=left_icon)

    # ---------- primitives ----------
    def tw(self, s, f):
        return self.d.textlength(fa(s), font=f)

    def fit(self, s, maxw, size=24, weight="Regular", minsize=11):
        while size > minsize and self.tw(s, font(size, weight)) > maxw:
            size -= 1
        return fa(s), font(size, weight)

    def txt(self, x, y, s, size=24, weight="Regular", fill=INK, anchor="ra"):
        self.d.text((x, y), fa(s), font=font(size, weight), fill=fill, anchor=anchor)

    def txt_fit(self, x, y, s, maxw, size=24, weight="Regular", fill=INK, anchor="ra"):
        t, f = self.fit(s, maxw, size, weight)
        self.d.text((x, y), t, font=f, fill=fill, anchor=anchor)

    def gap(self, h=14):
        self.y += h

    def divider(self, h=16, color=LINE):
        self.y += h // 2
        self.d.line([IL, self.y, IR, self.y], fill=color, width=2)
        self.y += h - h // 2

    # ---------- icons ----------
    def icon(self, name, cx, cy, r=13, color=INK, w=4):
        if name == "search":
            self.d.ellipse([cx - r, cy - r, cx + r - 5, cy + r - 5], outline=color, width=w)
            self.d.line([cx + r - 7, cy + r - 7, cx + r + 5, cy + r + 5], fill=color, width=w)
        elif name == "bell":
            self.d.arc([cx - r, cy - r, cx + r, cy + r - 2], 180, 360, fill=color, width=w)
            self.d.line([cx - r, cy, cx + r, cy], fill=color, width=w)
            self.d.line([cx - r, cy, cx - r, cy + 6], fill=color, width=w)
            self.d.line([cx + r, cy, cx + r, cy + 6], fill=color, width=w)
            self.d.ellipse([cx - 5, cy + 6, cx + 5, cy + 15], outline=color, width=w - 1)
        elif name == "dots":
            for dx in (-r, 0, r):
                self.d.ellipse([cx + dx - 4, cy - 4, cx + dx + 4, cy + 4], fill=color)
        elif name == "filter":
            for i, yy in enumerate((-r, 0, r)):
                self.d.line([cx - r, cy + yy, cx + r, cy + yy], fill=color, width=w - 1)
            for i, xx in enumerate((-8, 0, 8)):
                self.d.ellipse([cx + xx - 5, cy + yy * 0 - r + i * r - 5,
                                cx + xx + 5, cy - r + i * r + 5], fill=color)
        elif name == "heart":
            self.d.pieslice([cx - r, cy - r, cx, cy], 180, 360, fill=color)
            self.d.pieslice([cx, cy - r, cx + r, cy], 180, 360, fill=color)
            self.d.polygon([(cx - r, cy), (cx + r, cy), (cx, cy + r)], fill=color)
        elif name == "user":
            self.d.ellipse([cx - 7, cy - r, cx + 7, cy - r + 14], outline=color, width=w)
            self.d.pieslice([cx - r, cy - 4, cx + r, cy + r + 10], 180, 360, outline=color, width=w)
        elif name == "plus":
            self.d.line([cx - r, cy, cx + r, cy], fill=color, width=w)
            self.d.line([cx, cy - r, cx, cy + r], fill=color, width=w)
        elif name == "minus":
            self.d.line([cx - r, cy, cx + r, cy], fill=color, width=w)
        elif name == "camera":
            self.d.rounded_rectangle([cx - r, cy - 7, cx + r, cy + 8], radius=5, outline=color, width=w)
            self.d.ellipse([cx - 7, cy - 5, cx + 7, cy + 9], outline=color, width=w)
            self.d.rectangle([cx - 5, cy - 12, cx + 2, cy - 7], fill=color)
        elif name == "send":
            self.d.polygon([(cx - r, cy - r), (cx + r, cy), (cx - r, cy + r)],
                           outline=color, width=w)
        elif name == "check":
            self.d.line([cx - 8, cy, cx - 2, cy + 7], fill=color, width=w)
            self.d.line([cx - 2, cy + 7, cx + 9, cy - 8], fill=color, width=w)
        elif name == "chev_l":      # chevron pointing left
            self.d.line([cx + 7, cy - 11, cx - 7, cy, cx + 7, cy + 11], fill=color, width=w, joint="curve")
        elif name == "chev_r":      # chevron pointing right (RTL back)
            self.d.line([cx - 7, cy - 11, cx + 7, cy, cx - 7, cy + 11], fill=color, width=w, joint="curve")
        elif name == "pin":
            self.d.pieslice([cx - r, cy - r, cx + r, cy + r], 0, 360, outline=color, width=w)
            self.d.polygon([(cx - 7, cy + 5), (cx + 7, cy + 5), (cx, cy + r + 6)], fill=color)
            self.d.ellipse([cx - 4, cy - 6, cx + 4, cy + 2], fill=color)
        elif name == "phone":
            self.d.rounded_rectangle([cx - 9, cy - r, cx + 9, cy + r], radius=6, outline=color, width=w)
            self.d.line([cx - 3, cy + r - 6, cx + 3, cy + r - 6], fill=color, width=w)
        elif name == "chat":
            self.d.rounded_rectangle([cx - r, cy - r, cx + r, cy + 4], radius=8, outline=color, width=w)
            self.d.polygon([(cx - 5, cy + 4), (cx + 4, cy + 4), (cx - 6, cy + 13)], fill=color)
        elif name == "wallet":
            self.d.rounded_rectangle([cx - r, cy - 9, cx + r, cy + 10], radius=5, outline=color, width=w)
            self.d.ellipse([cx - 2, cy - 3, cx + 8, cy + 5], fill=color)
        elif name == "box":
            self.d.rounded_rectangle([cx - r, cy - r, cx + r, cy + r], radius=5, outline=color, width=w)
            self.d.line([cx - r, cy - 2, cx + r, cy - 2], fill=color, width=w - 1)
        elif name == "cal":
            self.d.rounded_rectangle([cx - r, cy - r, cx + r, cy + r], radius=5, outline=color, width=w)
            self.d.line([cx - r, cy - 4, cx + r, cy - 4], fill=color, width=w - 1)
            self.d.line([cx - 6, cy - r - 3, cx - 6, cy - r + 4], fill=color, width=w)
            self.d.line([cx + 6, cy - r - 3, cx + 6, cy - r + 4], fill=color, width=w)
        elif name == "gear":
            self.d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=w)
            self.d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], outline=color, width=w)
        elif name == "chart":
            for i, hgt in enumerate((8, 16, 24)):
                self.d.rectangle([cx - 12 + i * 10, cy + 12 - hgt, cx - 5 + i * 10, cy + 12], fill=color)
        elif name == "share":
            pts = [(cx - r, cy - 8), (cx + r, cy - 14), (cx - r, cy + 12)]
            for a, b in ((0, 1), (1, 2), (0, 2)):
                self.d.line([pts[a], pts[b]], fill=color, width=w - 1)
            for px, py in pts:
                self.d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=color)
        elif name == "cart":
            self.d.line([cx - r, cy - r + 2, cx - r + 5, cy - r + 2], fill=color, width=w)
            self.d.pieslice([cx - r + 2, cy - r + 2, cx + r + 4, cy + r], 0, 180,
                            outline=color, width=w)
            self.d.ellipse([cx - 8, cy + r - 2, cx - 1, cy + r + 5], fill=color)
            self.d.ellipse([cx + 5, cy + r - 2, cx + 12, cy + r + 5], fill=color)
        elif name == "note":
            self.d.rounded_rectangle([cx - r, cy - r, cx + r, cy + r], radius=5,
                                     outline=color, width=w)
            for yy in (-6, 0, 6):
                self.d.line([cx - 7, cy + yy, cx + 7, cy + yy], fill=color, width=w - 2)
        elif name == "home":
            self.d.polygon([(cx - r, cy), (cx, cy - r), (cx + r, cy)],
                           outline=color, width=w)
            self.d.line([cx - r + 4, cy, cx - r + 4, cy + r], fill=color, width=w)
            self.d.line([cx + r - 4, cy, cx + r - 4, cy + r], fill=color, width=w)
            self.d.line([cx - r + 4, cy + r, cx + r - 4, cy + r], fill=color, width=w)
            self.d.rectangle([cx - 6, cy + 4, cx + 6, cy + r], outline=color, width=w)

    # ---------- chrome ----------
    def _statusbar(self):
        self.d.text((IR, 10), fa("۹:۴۱"), font=font(21, "Medium"), fill=INK, anchor="ra")
        x = IL
        for h in (7, 11, 15, 19):
            self.d.rectangle([x, 32 - h, x + 5, 32], fill=INK)
            x += 8
        self.d.rounded_rectangle([x + 12, 14, x + 46, 32], radius=5, outline=INK, width=3)
        self.d.rectangle([x + 16, 18, x + 38, 28], fill=INK)
        self.d.rectangle([x + 47, 20, x + 51, 26], fill=INK)
        self.y = 46

    def navbar(self, title, back=True, right_text=None, left_icon=None, h=86):
        y0 = self.y
        cy = y0 + h // 2
        if back:
            self.icon("chev_r", IR - 14, cy, color=INK, w=5)
        if right_text:
            self.txt_fit(IR - (44 if back else 0), cy, right_text, 140, 22, "Bold",
                        BRAND, anchor="rm")
        if left_icon:
            self.icon(left_icon, IL + 16, cy, color=INK)
        t, f = self.fit(title, SW - 190, 30, "Bold")
        self.d.text((SW // 2, cy), t, font=f, fill=INK, anchor="mm")
        self.d.line([0, y0 + h, SW, y0 + h], fill=LINE, width=2)
        self.y = y0 + h

    # ---------- blocks ----------
    def h1(self, s, size=34):
        self.txt(IR, self.y, s, size, "Bold", INK, "ra")
        self.y += size + 18

    def section(self, title, action=None):
        cy = self.y + 20
        self.txt_fit(IR, cy, title, 340, 27, "Bold", INK, "rm")
        if action:
            self.txt_fit(IL, cy, action, 200, 21, "Bold", BRAND, "lm")
        self.y += 52

    def searchbox(self, text="جستجو ...", h=82, on=False):
        y0, y1 = self.y, self.y + h
        self.d.rounded_rectangle([IL, y0, IR, y1], radius=h // 2,
                                 fill=WHITE if on else BOX,
                                 outline=BRAND if on else LINE, width=3 if not on else 4)
        cy = (y0 + y1) // 2
        self.icon("search", IR - 42, cy, r=12, color=SUB, w=4)
        self.txt_fit(IR - 74, cy, text, IR - IL - 150, 25, "Regular", SUB if not on else INK, "rm")
        self.y = y1

    def banner(self, h=168, l1="", l2="", cta=None, color=BRAND):
        y0, y1 = self.y, self.y + h
        self.d.rounded_rectangle([IL, y0, IR, y1], radius=24, fill=color)
        cy = (y0 + y1) // 2
        if l1:
            self.txt_fit(IR - 34, cy - 34, l1, IR - IL - 68, 34, "Bold", WHITE, "ra")
        if l2:
            self.txt_fit(IR - 34, cy + 14, l2, IR - IL - 68, 23, "Regular", "#DDF1EC", "ra")
        if cta:
            cw = self.tw(cta, font(20, "Bold")) + 44
            self.d.rounded_rectangle([IL + 26, cy + 46, IL + 26 + cw, cy + 84], radius=19, fill=WHITE)
            self.d.text((IL + 26 + cw / 2, cy + 65), fa(cta), font=font(20, "Bold"), fill=color, anchor="mm")
        # decorative circles
        self.d.ellipse([IL + 8, y0 + 20, IL + 68, y0 + 80], outline="#2E9B86", width=6)
        self.d.ellipse([IL + 34, y0 + 66, IL + 74, y0 + 106], outline="#2E9B86", width=6)
        self.y = y1

    def icon_row(self, items, per_row=6, r=44, label_h=34):
        cw = (IR - IL) / per_row
        for j, item in enumerate(items[:per_row]):
            if isinstance(item, (tuple, list)):
                label, sym = item[0], item[1]
            else:
                label, sym = item, item[0]
            cx = IR - cw * (j + 0.5)
            cy = self.y + r
            self.d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BRAND_SOFT, outline=BRAND, width=3)
            t, f = self.fit(sym, r * 1.5, 30, "Bold")
            self.d.text((cx, cy), t, font=f, fill=BRAND, anchor="mm")
            t2, f2 = self.fit(label, cw - 4, 19, "Medium")
            self.d.text((cx, self.y + 2 * r + 8), t2, font=f2, fill=INK, anchor="ma")
        self.y += 2 * r + 8 + label_h

    def pills(self, items, per_row=4, h=60, gap=12, active=0, soft=True):
        w = (IR - IL - gap * (per_row - 1)) // per_row
        i = 0
        while i < len(items):
            row = items[i:i + per_row]
            for j, label in enumerate(row):
                x1 = IR - j * (w + gap)
                x0 = x1 - w
                idx = i + j
                sel = (idx == active)
                self.d.rounded_rectangle([x0, self.y, x1, self.y + h], radius=h // 2,
                                         fill=BRAND if sel else (BRAND_SOFT if soft else WHITE),
                                         outline=BRAND if sel else LINE, width=3)
                cy = self.y + h // 2
                t, f = self.fit(label, w - 18, 20, "Bold" if sel else "Medium")
                self.d.text(((x0 + x1) / 2, cy), t, font=f,
                            fill=WHITE if sel else INK, anchor="mm")
            self.y += h + gap
            i += per_row

    def imgph(self, box, radius=14):
        x0, y0, x1, y1 = [int(v) for v in box]
        if x1 - x0 < 6 or y1 - y0 < 6:
            return
        self.d.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill="#E9EDF3")
        w, h = x1 - x0, y1 - y0
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        s = min(w, h) / 5.0
        self.d.ellipse([cx + s * 0.3, cy - s * 1.0, cx + s * 0.3 + s * 0.75,
                        cy - s * 1.0 + s * 0.75], fill="#CBD4E0")
        self.d.polygon([(cx - s * 1.5, cy + s * 0.95), (cx - s * 0.35, cy - s * 0.25),
                        (cx + s * 0.8, cy + s * 0.95)], fill="#CBD4E0")
        self.d.polygon([(cx - s * 0.2, cy + s * 0.95), (cx + s * 0.75, cy - s * 0.35),
                        (cx + s * 1.7, cy + s * 0.95)], fill="#DCE3EC")

    def avatar(self, cx, cy, r, label="", fill=BRAND_SOFT, color=BRAND, ring=None):
        if ring:
            self.d.ellipse([cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4], fill=ring)
        self.d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=LINE, width=2)
        if label:
            t, f = self.fit(label, r * 1.6, int(r * 0.8), "Bold")
            self.d.text((cx, cy), t, font=f, fill=color, anchor="mm")

    def chip(self, text, right=IR, left=None, y=None, bg=BRAND_SOFT, fg=BRAND, h=42,
             size=20, bold=True):
        y = self.y if y is None else y
        f = font(size, "Bold" if bold else "Medium")
        w = self.d.textlength(fa(text), font=f) + 34
        if left is not None:
            x0, x1 = left, left + w
        else:
            x1 = right
            x0 = x1 - w
        self.d.rounded_rectangle([x0, y, x1, y + h], radius=h // 2, fill=bg)
        self.d.text(((x0 + x1) / 2, y + h / 2), fa(text), font=f, fill=fg, anchor="mm")
        return w

    def badge(self, text, right, y, bg=RED, fg=WHITE, size=17, minw=34):
        f = font(size, "Bold")
        w = max(minw, self.d.textlength(fa(text), font=f) + 18)
        h = w if len(str(text)) <= 2 else 40
        self.d.rounded_rectangle([right - w, y, right, y + h], radius=h // 2, fill=bg)
        self.d.text((right - w / 2, y + h / 2), fa(text), font=f, fill=fg, anchor="mm")
        return w

    def button(self, text, h=86, color=BRAND, fg=WHITE, outline=None, disabled=False):
        y0, y1 = self.y, self.y + h
        fill = "#DCE1E8" if disabled else color
        if outline:
            self.d.rounded_rectangle([IL, y0, IR, y1], radius=h // 2, fill=fill,
                                     outline=outline, width=3)
        else:
            self.d.rounded_rectangle([IL, y0, IR, y1], radius=h // 2, fill=fill)
        t, f = self.fit(text, IR - IL - 60, 27, "Bold")
        self.d.text(((IL + IR) / 2, (y0 + y1) / 2), t, font=f,
                    fill="#9AA3B0" if disabled else fg, anchor="mm")
        self.y = y1

    def bottom_nav(self, items, active=0):
        y0 = SH - 134
        self.d.rectangle([0, y0, SW, SH], fill=WHITE)
        self.d.line([0, y0, SW, y0], fill=LINE, width=2)
        n = len(items)
        w = SW / n
        shapes = ["home", "cart", "cal", "user"]
        for i, label in enumerate(items):
            cx = SW - (i + 0.5) * w
            color = BRAND if i == active else SUB
            if i == active:
                self.d.rounded_rectangle([cx - 34, y0 + 18, cx + 34, y0 + 66],
                                         radius=16, fill=BRAND_SOFT)
            self.icon(shapes[i % len(shapes)], cx, y0 + 42, r=13, color=color, w=4)
            t, f = self.fit(label, w - 8, 18, "Bold" if i == active else "Medium")
            self.d.text((cx, y0 + 78), t, font=f, fill=color, anchor="ma")
        self.y = SH

    def tabs(self, items, active=0, h=64):
        w = (IR - IL) // len(items)
        for i, label in enumerate(items):
            x1 = IR - i * w
            x0 = x1 - w
            cy = self.y + h // 2
            sel = i == active
            t, f = self.fit(label, w - 14, 22, "Bold" if sel else "Medium")
            self.d.text(((x0 + x1) / 2, cy), t, font=f, fill=BRAND if sel else SUB, anchor="mm")
            if sel:
                self.d.rounded_rectangle([x0 + 18, self.y + h - 7, x1 - 18, self.y + h],
                                         radius=4, fill=BRAND)
            else:
                self.d.line([x0 + 18, self.y + h - 3, x1 - 18, self.y + h - 3], fill=LINE, width=2)
        self.y += h + 12

    def row(self, title, sub=None, note=None, h=98, box=74, chevron=True,
            img=True, badge_text=None, badge_color=RED):
        y0, y1 = self.y, self.y + h
        tx = IR
        if img:
            bs = box
            by = y0 + (h - bs) // 2
            self.imgph([IR - bs, by, IR, by + bs], radius=12)
            tx = IR - bs - 16
        bw = 0
        if badge_text:
            bf = font(17, "Bold")
            bw = max(34, self.d.textlength(fa(badge_text), font=bf) + 18) + 14
        right_room = tx - IL - 20 - (bw if badge_text else 0)
        cy = y0 + h // 2
        ts = 24 if sub else 25
        self.txt_fit(tx, cy - (13 if sub else 0), title, right_room, ts, "Medium", INK, "rm")
        if sub:
            self.txt_fit(tx, cy + 8, sub, right_room, 20, "Regular", SUB, "rm")
        if note:
            self.txt_fit(IL + (bw if badge_text else 6), cy, note, 220, 22, "Bold", BRAND, "lm")
        if badge_text:
            self.badge(badge_text, IL + 12, cy - 17, bg=badge_color)
        elif chevron:
            self.icon("chev_l", IL + 12, cy, r=10, color="#AAB2BF", w=4)
        self.d.line([IL, y1, IR, y1], fill="#EEF1F5", width=2)
        self.y = y1

    def kv(self, k, v, h=58, kcolor=SUB, vcolor=INK, bold=False, size=23, rule=True):
        cy = self.y + h // 2
        self.txt_fit(IR, cy, k, 300, size, "Regular", kcolor, "rm")
        self.txt_fit(IL, cy, v, 300, size, "Bold" if bold else "Medium", vcolor, "lm")
        if rule:
            self.d.line([IL, self.y + h, IR, self.y + h], fill="#EEF1F5", width=2)
        self.y += h

    def card(self, radius=20, fill=WHITE, outline=LINE, pad=20, h=None, top=None):
        y0 = self.y if top is None else top
        h = h or 0
        self.d.rounded_rectangle([IL, y0, IR, y0 + h], radius=radius, fill=fill,
                                 outline=outline, width=3)
        return y0

    def radio(self, title, sub=None, selected=False, h=82, note=None):
        y0, y1 = self.y, self.y + h
        self.d.rounded_rectangle([IL, y0, IR, y1], radius=16,
                                 fill=BRAND_SOFT if selected else WHITE,
                                 outline=BRAND if selected else LINE,
                                 width=4 if selected else 3)
        cx = IR - 34
        cy = (y0 + y1) // 2
        self.d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14],
                       outline=BRAND if selected else "#AAB2BF", width=4)
        if selected:
            self.d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=BRAND)
        tx = cx - 30
        self.txt_fit(tx, cy - (12 if sub else 0), title, tx - IL - 24, 24,
                     "Bold" if selected else "Medium", INK, "rm")
        if sub:
            self.txt_fit(tx, cy + 8, sub, tx - IL - 24, 19, "Regular", SUB, "rm")
        if note:
            self.txt_fit(IL + 18, cy, note, 160, 20, "Bold", BRAND, "lm")
        self.y = y1 + 12

    def field(self, label, value="", placeholder=True, h=76, icon=None, trailing=None):
        if label:
            self.txt(IR, self.y, label, 22, "Medium", INK, "ra")
            self.y += 34
        y0, y1 = self.y, self.y + h
        self.d.rounded_rectangle([IL, y0, IR, y1], radius=14, fill=WHITE, outline=LINE, width=3)
        cy = (y0 + y1) // 2
        tx = IR - 22
        if icon:
            self.icon(icon, IR - 34, cy, r=12, color=SUB, w=4)
            tx = IR - 64
        if value:
            self.txt_fit(tx, cy, value, tx - IL - 24, 24,
                         "Regular" if placeholder else "Medium",
                         SUB if placeholder else INK, "rm")
        if trailing:
            self.txt_fit(IL + 22, cy, trailing, 150, 21, "Bold", BRAND, "lm")
        self.y = y1 + 16

    def code_boxes(self, n=6, filled=0, h=88, gap=14):
        w = (IR - IL - gap * (n - 1)) // n
        for i in range(n):
            x1 = IR - i * (w + gap)
            x0 = x1 - w
            on = i < filled
            self.d.rounded_rectangle([x0, self.y, x1, self.y + h], radius=14,
                                     fill=BRAND_SOFT if on else WHITE,
                                     outline=BRAND if on else LINE,
                                     width=4 if on else 3)
            if on:
                self.d.text(((x0 + x1) / 2, self.y + h / 2), fa(str((i + 3) % 10)),
                            font=font(38, "Bold"), fill=INK, anchor="mm")
        self.y += h + 16

    def timeline(self, steps, current, gap_h=74):
        dotx = IR - 18
        for i, item in enumerate(steps):
            title = item[0]
            sub = item[1] if len(item) > 1 else None
            cy = self.y + 26
            done = i < current
            active = i == current
            color = BRAND if done or active else "#C6CCD6"
            r = 13 if active else 10
            if i < len(steps) - 1:
                nxt = self.y + gap_h + 26
                col = BRAND if i < current else "#DCE1E8"
                self.d.line([dotx, cy + r + 4, dotx, nxt - r - 4], fill=col, width=5)
            if done:
                self.d.ellipse([dotx - r, cy - r, dotx + r, cy + r], fill=color)
                self.icon("check", dotx, cy, r=6, color=WHITE, w=4)
            elif active:
                self.d.ellipse([dotx - r - 5, cy - r - 5, dotx + r + 5, cy + r + 5], fill=BRAND_SOFT)
                self.d.ellipse([dotx - r, cy - r, dotx + r, cy + r], fill=color)
            else:
                self.d.ellipse([dotx - r, cy - r, dotx + r, cy + r], fill=WHITE,
                               outline=color, width=4)
            tx = dotx - r - 20
            self.txt_fit(tx, cy - (13 if sub else 12), title, tx - IL, 24,
                         "Bold" if active or done else "Medium",
                         INK if done or active else SUB, "rm")
            if sub:
                self.txt_fit(tx, cy + 8, sub, tx - IL, 19, "Regular", SUB, "rm")
            self.y += gap_h

    def metric(self, x0, x1, y0, y1, value, label, color=BRAND):
        self.d.rounded_rectangle([x0, y0, x1, y1], radius=18, fill=WHITE,
                                 outline=LINE, width=3)
        cy = (y0 + y1) / 2
        self.txt_fit(x1 - 18, cy - 12, label, x1 - x0 - 36, 21, "Medium", SUB, "rm")
        self.txt_fit(x1 - 18, cy + 12, value, x1 - x0 - 36, 30, "Bold", color, "rm")

    def progress(self, pct, h=16, color=BRAND, track="#E6EAF0"):
        y0 = self.y
        self.d.rounded_rectangle([IL, y0, IR, y0 + h], radius=h // 2, fill=track)
        w = (IR - IL) * pct / 100.0
        if w > h:
            self.d.rounded_rectangle([IR - w, y0, IR, y0 + h], radius=h // 2, fill=color)
        self.y += h

    def notice(self, title, sub=None, bg=GOLD_SOFT, fg="#7A6134", h=None, icon="!"):
        pad = 18
        t_h = 34 if not sub else 62
        h = h or (t_h + 2 * pad)
        y0, y1 = self.y, self.y + h
        self.d.rounded_rectangle([IL, y0, IR, y1], radius=16, fill=bg)
        cx = IR - 34
        cy = (y0 + y1) // 2
        self.d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], outline=fg, width=4)
        self.d.text((cx, cy), fa(icon), font=font(24, "Bold"), fill=fg, anchor="mm")
        tx = cx - 28
        self.txt_fit(tx, cy - (13 if sub else 12), title, tx - IL - 20, 23, "Bold", fg, "rm")
        if sub:
            self.txt_fit(tx, cy + 9, sub, tx - IL - 20, 19, "Regular", fg, "rm")
        self.y = y1 + 14

    def bubble(self, text, me=True, time="", status=None, wmax=430, size=23):
        f = font(size, "Regular")
        # naive wrap
        words = fa(text).split(" ")
        lines, cur = [], ""
        for w in words:
            trial = (cur + " " + w).strip()
            if self.d.textlength(trial, font=f) <= wmax - 44:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        lw = max([self.d.textlength(l, font=f) for l in lines] or [0])
        w = min(wmax, lw + 44)
        h = 30 + len(lines) * 34
        y0 = self.y
        if me:
            x1, x0 = IR, IR - w
            fill, fg = BRAND, WHITE
        else:
            x0, x1 = IL, IL + w
            fill, fg = "#EDF1F6", INK
        self.d.rounded_rectangle([x0, y0, x1, y0 + h], radius=18, fill=fill)
        for k, line in enumerate(lines):
            if me:
                self.d.text((x1 - 22, y0 + 16 + k * 34), line, font=f, fill=fg, anchor="ra")
            else:
                self.d.text((x0 + 22, y0 + 16 + k * 34), line, font=f, fill=fg, anchor="ra")
        info = time
        if status:
            info = (info + "  " + status) if info else status
        if info:
            if me:
                self.d.text((x0 - 8, y0 + h - 22), fa(info), font=font(17), fill=SUB, anchor="ra")
            else:
                self.d.text((x1 + 8, y0 + h - 22), fa(info), font=font(17), fill=SUB, anchor="la")
        self.y = y0 + h + 16

    def sysmsg(self, text):
        f = font(20, "Medium")
        t = fa(text)
        w = self.d.textlength(t, font=f) + 40
        x0 = (SW - w) / 2
        y0 = self.y
        self.d.rounded_rectangle([x0, y0, x0 + w, y0 + 44], radius=22, fill=BLUE_SOFT)
        self.d.text((SW / 2, y0 + 22), t, font=f, fill="#31538F", anchor="mm")
        self.y = y0 + 60

    def inputbar(self, placeholder="پیام خود را بنویسید ..."):
        y0 = SH - 118
        self.d.rectangle([0, y0, SW, SH], fill=WHITE)
        self.d.line([0, y0, SW, y0], fill=LINE, width=2)
        cy = y0 + 56
        self.icon("plus", IL + 26, cy, r=13, color=SUB, w=5)
        x0, x1 = IL + 60, IR - 76
        self.d.rounded_rectangle([x0, y0 + 22, x1, y0 + 92], radius=35, fill=BOX)
        self.d.text((x1 - 24, cy), fa(placeholder), font=font(22), fill=SUB, anchor="rm")
        self.d.ellipse([IR - 62, y0 + 24, IR, y0 + 90], fill=BRAND)
        self.icon("send", IR - 31, cy, r=12, color=WHITE, w=4)
        self.y = SH

    def stepper(self, x_right, y_mid, value="۲"):
        w, h = 132, 52
        x0 = x_right - w
        self.d.rounded_rectangle([x0, y_mid - h // 2, x_right, y_mid + h // 2],
                                 radius=12, fill=WHITE, outline=LINE, width=3)
        self.icon("minus", x0 + 26, y_mid, r=11, color=INK, w=4)
        self.icon("plus", x_right - 26, y_mid, r=11, color=INK, w=4)
        self.d.text((x_right - w / 2, y_mid), fa(value), font=font(24, "Bold"),
                    fill=INK, anchor="mm")

    def toggle(self, x_right, y_mid, on=True):
        w, h = 74, 40
        x0 = x_right - w
        self.d.rounded_rectangle([x0, y_mid - h // 2, x_right, y_mid + h // 2],
                                 radius=h // 2, fill=BRAND if on else "#D7DCE4")
        cx = x0 + h / 2 if on else x_right - h / 2
        self.d.ellipse([cx - h / 2 + 4, y_mid - h / 2 + 4, cx + h / 2 - 4, y_mid + h / 2 - 4],
                       fill=WHITE)

    # ---------- save ----------
    def save(self, name):
        mask = Image.new("L", (SW, SH), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, SW - 1, SH - 1], radius=46, fill=255)
        white = Image.new("RGB", (SW, SH), WHITE)
        scr = Image.composite(self.scr, white, mask)

        canvas = Image.new("RGB", (CW, CH), "#FFFFFF")
        dd = ImageDraw.Draw(canvas)
        dd.rounded_rectangle([M + 6, M + 10, M + SW + 6, M + SH + 10],
                             radius=48, fill="#E4E8EE")
        canvas.paste(scr, (M, M))
        dd.rounded_rectangle([M, M, M + SW, M + SH], radius=46,
                             outline="#16213E", width=7)
        path = os.path.join(OUT, name + ".png")
        canvas.save(path, quality=95)
        return path


# ======================================================================
#  Scenes
# ======================================================================
def sc_login():
    p = Phone(title=None)
    p.y = 150
    p.avatar(SW // 2, p.y + 70, 70, "A", fill=BRAND, color=WHITE)
    p.y += 168
    p.txt(SW // 2, p.y, "ورود | ثبت‌نام", 34, "Bold", INK, "ma"); p.y += 56
    p.txt(SW // 2, p.y, "شماره موبایل خود را وارد کنید", 23, "Regular", SUB, "ma"); p.y += 64
    p.field(None, "۰۹۱۲ ۳۴۵ ۶۷۸۹", placeholder=True, h=86, trailing="+۹۸")
    p.gap(6)
    p.button("ارسال کد تأیید")
    p.gap(30)
    p.icon("check", IL + 18, p.y + 14, r=10, color=BRAND, w=4)
    p.txt(IR - 4, p.y + 14, "کد تأیید ۵ رقمی / اعتبار ۱۲۰ ثانیه", 21, "Regular", SUB, "rm")
    p.y += 44
    p.icon("check", IL + 18, p.y + 14, r=10, color=BRAND, w=4)
    p.txt(IR - 4, p.y + 14, "حداکثر ۳ تلاش - ۳ پیامک در ۱۰ دقیقه", 21, "Regular", SUB, "rm")
    p.y += 70
    p.divider(30)
    p.button("ورود با اثر انگشت / تشخیص چهره", h=80, color=WHITE, fg=INK, outline=LINE)
    p.gap(24)
    p.txt(SW // 2, p.y, "با ورود، قوانین و حریم خصوصی AMPET را می‌پذیرم", 19, "Regular", SUB, "ma")
    return p.save("login")


def sc_home():
    p = Phone(title=None)
    # custom header
    cy = p.y + 44
    p.avatar(IR - 34, cy, 34, "م", ring=WHITE)
    p.txt(IR - 84, cy - 14, "سلام محمد 👋", 27, "Bold", INK, "rm")
    p.txt(IR - 84, cy + 16, "چه کمکی می‌تونم بکنم؟", 20, "Regular", SUB, "rm")
    p.icon("bell", IL + 22, cy, r=15)
    p.badge("۳", IL + 10, cy - 44)
    p.y += 96
    p.searchbox("جستجوی کالا، خدمات، دامپزشک ...")
    p.gap(20)
    p.banner(l1="تا ۳۰٪ تخفیف غذاهای خشک", l2="ویژه حیوانات خانگی شما", cta="مشاهده")
    p.gap(26)
    p.section("دسته‌بندی حیوانات", "همه")
    p.icon_row([("سگ", "سگ"), ("گربه", "گر"), ("پرنده", "پرن"),
                ("اگزوتیک", "اگز"), ("دام بزرگ", "دام"), ("اسب", "اسب")])
    p.gap(14)
    p.section("فروشندگان برتر", "مشاهده همه")
    shops = [dict(title="پت‌شاپ لایف‌لند", sub="⭐ ۴.۸ | ۳۲۰ محصول", price="تهران"),
             dict(title="کلینیک دامپزشکی مهر", sub="⭐ ۴.۹ | ۱۲۰ محصول", price="اصفهان"),
             dict(title="گرومر حیوانات شاد", sub="⭐ ۴.۷ | ۸۵ خدمت", price="شیراز")]
    x = IR
    for it in shops:
        w = 292
        x0 = x - w
        if x0 < IL:
            break
        y0 = p.y
        p.d.rounded_rectangle([x0, y0, x - 6, y0 + 236], radius=18, fill=WHITE,
                              outline=LINE, width=3)
        p.imgph([x0 + 10, y0 + 10, x - 16, y0 + 118], radius=12)
        p.txt_fit(x - 16, y0 + 136, it["title"], w - 32, 23, "Bold", INK, "ra")
        p.txt_fit(x - 16, y0 + 168, it["sub"], w - 32, 19, "Regular", SUB, "ra")
        p.chip(it["price"], right=x - 16, y=y0 + 194, bg=BOX, fg=SUB, h=32, size=17)
        x = x0 - 12
    p.y += 252
    p.section("پرفروش‌ترین‌ها", "مشاهده همه")
    prods = [dict(title="غذای خشک سگ بالغ", price="۲۴۹,۰۰۰ تومان"),
             dict(title="اسباب‌بازی موش پارچه‌ای", price="۸۹,۰۰۰ تومان"),
             dict(title="قلاده چرمی ضدپارگی", price="۱۷۵,۰۰۰ تومان")]
    x = IR
    for it in prods:
        w = 236
        x0 = x - w
        if x0 < IL:
            break
        y0 = p.y
        p.d.rounded_rectangle([x0, y0, x - 6, y0 + 268], radius=18, fill=WHITE,
                              outline=LINE, width=3)
        p.imgph([x0 + 10, y0 + 10, x - 16, y0 + 138], radius=12)
        p.txt_fit(x - 16, y0 + 154, it["title"], w - 32, 21, "Medium", INK, "ra")
        p.txt_fit(x - 16, y0 + 196, "فروشنده: پت‌لند", w - 32, 17, "Regular", SUB, "ra")
        p.txt_fit(x - 16, y0 + 232, it["price"], w - 32, 24, "Bold", BRAND, "ra")
        x = x0 - 12
    p.y += 284
    p.section("خدمات", "مشاهده همه")
    p.icon_row([("ویزیت آنلاین", "وی"), ("گرومینگ", "گر"), ("تاکسی حیوان", "تا"),
                ("کافه پت", "کا"), ("واکسن", "وا"), ("ویزیت در محل", "مح")])
    p.bottom_nav(["خانه", "سبد خرید", "نوبت‌ها", "پروفایل"], 0)
    return p.save("home")


def sc_search():
    p = Phone(title="جستجو", left_icon="filter")
    p.searchbox("غذا خشک سگ", h=80, on=True)
    p.gap(16)
    p.pills(["همه", "سگ", "گربه", "پرنده", "اگزوتیک", "دام بزرگ", "اسب", "بدون فیلتر"],
            per_row=4, active=1)
    p.y += 4
    # result count + sort
    p.txt(IR, p.y + 14, "۲۴۸ نتیجه", 21, "Medium", SUB, "rm")
    p.txt(IL, p.y + 14, "مرتب‌سازی: پیشنهاد ما ⌄", 21, "Bold", BRAND, "lm")
    p.y += 44
    p.divider(14)
    items = [("غذای خشک سگ بالغ ۱۰ کیلویی", "۲۴۹,۰۰۰ تومان", "۲۰٪"),
             ("غذای خشک توله سگ", "۱۹۵,۰۰۰ تومان", ""),
             ("غذای خشک بدون گلوتن", "۳۱۰,۰۰۰ تومان", "۱۰٪"),
             ("غذای خشک نژاد کوچک", "۱۷۵,۰۰۰ تومان", "")]
    cols = 2
    w = (IR - IL - 18) // cols
    for i, (t, price, off) in enumerate(items):
        col = i % cols
        x1 = IR - col * (w + 18)
        x0 = x1 - w
        y0 = p.y
        p.d.rounded_rectangle([x0, y0, x1, y0 + 300], radius=18, fill=WHITE,
                              outline=LINE, width=3)
        p.imgph([x0 + 10, y0 + 10, x1 - 10, y0 + 152], radius=12)
        if off:
            p.chip(off, right=x1 - 12, y=y0 + 18, bg=RED, fg=WHITE, h=34, size=18)
        p.txt_fit(x1 - 14, y0 + 170, t, w - 28, 21, "Medium", INK, "ra")
        p.txt_fit(x1 - 14, y0 + 212, "⭐ ۴.۶ | ۱۲۷ خرید", w - 28, 17, "Regular", SUB, "ra")
        p.txt_fit(x1 - 14, y0 + 252, price, w - 28, 24, "Bold", BRAND, "ra")
        p.icon("heart", x0 + 26, y0 + 268, r=12, color="#AAB2BF", w=4)
        if col == cols - 1:
            p.y += 316
    return p.save("search")


def sc_product():
    p = Phone(title="جزئیات محصول", right_text="اشتراک", left_icon="heart")
    p.imgph([IL, p.y, IR, p.y + 340], radius=20)
    p.y += 352
    # dots
    for i in range(4):
        cx = SW / 2 + (1.5 - i) * 22
        p.d.ellipse([cx - 6, p.y, cx + 6, p.y + 12], fill=BRAND if i == 0 else "#C6CCD6")
    p.y += 34
    p.txt(IR, p.y, "۲۴۹,۰۰۰ تومان", 36, "Bold", BRAND, "ra")
    p.txt_fit(IR - 0, p.y + 46, "۳۱۲,۰۰۰", 140, 22, "Regular", "#AAB2BF", "ra")
    # strikethrough
    w0 = p.tw("۳۱۲,۰۰۰", font(22))
    p.d.line([IR - w0, p.y + 58, IR, p.y + 58], fill="#AAB2BF", width=3)
    p.chip("۲۰٪ تخفیف", right=IR - w0 - 14, y=p.y + 44, bg=RED_SOFT, fg=RED, h=36, size=19)
    p.txt(IL, p.y + 16, "۱۲۷ خرید از این محصول", 21, "Medium", SUB, "lm")
    p.y += 96
    p.divider(16)
    # seller
    p.avatar(IR - 36, p.y + 40, 36, "پ")
    p.txt(IR - 86, p.y + 24, "پت‌شاپ لایف‌لند", 25, "Bold", INK, "rm")
    p.txt(IR - 86, p.y + 56, "⭐ ۴.۸ | ۳۲۰ محصول | تهران", 20, "Regular", SUB, "rm")
    p.chip("فروشگاه", left=IL + 4, y=p.y + 26, bg=BOX, fg=SUB, h=38, size=18)
    p.y += 96
    p.tabs(["توضیحات", "مشخصات", "نظرات (۸۴)"], 0)
    for _ in range(4):
        p.d.rounded_rectangle([IL, p.y, IR, p.y + 18], radius=9, fill="#EBEFF4")
        p.y += 32
    p.gap(6)
    p.section("مشخصات فنی")
    p.kv("وزن", "۱۰ کیلوگرم", rule=True)
    p.kv("برند", "Royal Canin", rule=True)
    p.kv("مناسب", "سگ بالغ - همه نژادها", rule=True)
    p.gap(14)
    p.section("نظرات کاربران", "همه نظرات")
    p.avatar(IR - 30, p.y + 30, 30, "ن")
    p.txt(IR - 74, p.y + 14, "نگار - ⭐⭐⭐⭐⭐", 22, "Bold", INK, "rm")
    p.txt_fit(IR - 74, p.y + 46, "کیفیت عالی، سگم خیلی دوست داشت", 400, 20, "Regular", SUB, "rm")
    p.y += 96
    # sticky bar
    y0 = SH - 140
    p.d.rectangle([0, y0, SW, SH], fill=WHITE)
    p.d.line([0, y0, SW, y0], fill=LINE, width=2)
    p.txt(IR - 8, y0 + 40, "۲۴۹,۰۰۰", 26, "Bold", BRAND, "rm")
    p.txt(IR - 8, y0 + 76, "تومان", 19, "Regular", SUB, "rm")
    bw = 400
    p.d.rounded_rectangle([IL, y0 + 24, IL + bw, y0 + 108], radius=42, fill=BRAND)
    p.d.text((IL + bw / 2, y0 + 66), fa("افزودن به سبد خرید"), font=font(25, "Bold"),
             fill=WHITE, anchor="mm")
    p.y = SH
    return p.save("product")


def sc_cart():
    p = Phone(title="سبد خرید", back=True, right_text="پاک‌سازی")
    # group 1
    p.txt(IR, p.y + 18, "پت‌شاپ لایف‌لند", 25, "Bold", INK, "rm")
    p.txt(IL, p.y + 20, "۲ قلم", 20, "Regular", SUB, "lm")
    p.y += 52
    p.d.line([IL, p.y, IR, p.y], fill=LINE, width=2)
    p.y += 12
    for title, price in [("غذای خشک سگ بالغ ۱۰ کیلو", "۲۴۹,۰۰۰"),
                         ("قلاده چرمی ضدپارگی", "۱۷۵,۰۰۰")]:
        p.imgph([IR - 84, p.y + 6, IR, p.y + 90], radius=12)
        p.txt_fit(IR - 100, p.y + 14, title, 330, 22, "Medium", INK, "ra")
        p.txt(IR - 100, p.y + 50, price + " تومان", 24, "Bold", BRAND, "ra")
        p.stepper(IR - 100, p.y + 116, "۱")
        p.icon("dots", IL + 20, p.y + 30, r=10, color="#AAB2BF")
        p.y += 154
    p.kv("هزینه ارسال این فروشگاه", "۳۵,۰۰۰ تومان", kcolor=SUB, rule=False)
    p.gap(12)
    p.d.line([IL, p.y, IR, p.y], fill=LINE, width=3)
    p.gap(18)
    # group 2
    p.txt(IR, p.y + 18, "داروخانه دامپزشکی مهر", 25, "Bold", INK, "rm")
    p.txt(IL, p.y + 20, "۱ قلم", 20, "Regular", SUB, "lm")
    p.y += 52
    p.d.line([IL, p.y, IR, p.y], fill=LINE, width=2)
    p.y += 12
    p.imgph([IR - 84, p.y + 6, IR, p.y + 90], radius=12)
    p.txt_fit(IR - 100, p.y + 14, "قطره ضدکک و کنه سگ", 330, 22, "Medium", INK, "ra")
    p.txt(IR - 100, p.y + 50, "۱۲۰,۰۰۰ تومان", 24, "Bold", BRAND, "ra")
    p.stepper(IR - 100, p.y + 116, "۲")
    p.y += 154
    p.kv("هزینه ارسال این فروشگاه", "۲۸,۰۰۰ تومان", kcolor=SUB, rule=False)
    p.gap(14)
    p.notice("سبد شما به ۲ سفارش جداگانه تفکیک می‌شود",
             "هر فروشگاه جداگانه ارسال و جداگانه تسویه می‌شود")
    p.gap(6)
    p.field(None, "کد تخفیف را وارد کنید", placeholder=True, h=76, trailing="اعمال")
    p.kv("جمع اقلام", "۵۴۴,۰۰۰ تومان", kcolor=SUB, rule=False, h=52)
    p.kv("تخفیف", "- ۵۰,۰۰۰ تومان", kcolor=SUB, vcolor=RED, rule=False, h=52)
    p.kv("هزینه ارسال (۲ فروشگاه)", "۶۳,۰۰۰ تومان", kcolor=SUB, rule=False, h=52)
    y0 = SH - 140
    p.d.rectangle([0, y0, SW, SH], fill=WHITE)
    p.d.line([0, y0, SW, y0], fill=LINE, width=2)
    p.txt(IR - 8, y0 + 40, "۵۵۷,۰۰۰ تومان", 28, "Bold", BRAND, "rm")
    p.txt(IR - 8, y0 + 78, "مبلغ قابل پرداخت", 19, "Regular", SUB, "rm")
    bw = 340
    p.d.rounded_rectangle([IL, y0 + 24, IL + bw, y0 + 108], radius=42, fill=BRAND)
    p.d.text((IL + bw / 2, y0 + 66), fa("تسویه"), font=font(26, "Bold"), fill=WHITE, anchor="mm")
    p.y = SH
    return p.save("cart")


def sc_checkout():
    p = Phone(title="تسویه و پرداخت")
    p.section("آدرس تحویل", "تغییر")
    p.d.rounded_rectangle([IL, p.y, IR, p.y + 118], radius=18, fill=WHITE,
                          outline=BRAND, width=4)
    p.icon("pin", IR - 34, p.y + 44, r=15, color=BRAND, w=4)
    p.txt_fit(IR - 66, p.y + 30, "خانه - تهران، سعادت‌آباد", 380, 24, "Bold", INK, "rm")
    p.txt_fit(IR - 66, p.y + 66, "خیابان علامه شمالی، پلاک ۱۲، واحد ۴", 420, 20,
              "Regular", SUB, "rm")
    p.txt_fit(IR - 66, p.y + 94, "گیرنده: محمد رضایی - ۰۹۱۲۳۴۵۶۷۸۹", 420, 20, "Regular", SUB, "rm")
    p.chip("پیش‌فرض", left=IL + 14, y=p.y + 14, bg=BOX, fg=SUB, h=34, size=17)
    p.y += 140
    p.section("روش ارسال")
    p.radio("پیک فروشگاه", "۱ تا ۲ روز کاری", selected=True, note="۳۵,۰۰۰")
    p.radio("پست پیشتاز", "۳ تا ۵ روز کاری", note="۲۸,۰۰۰")
    p.radio("تحویل حضوری", "فروشگاه سعادت‌آباد", note="رایگان")
    p.gap(6)
    p.section("روش پرداخت")
    p.radio("درگاه بانکی", "سامان / ملت / پارسیان", selected=True)
    p.radio("کیف پول AMPET", "موجودی: ۴۲۰,۰۰۰ تومان")
    p.radio("اعتبار خرید (BNPL)", "۳۰ میلیون ریال باقی‌مانده")
    p.radio("زرین‌پال", "پرداخت امن")
    p.gap(8)
    p.kv("جمع اقلام", "۵۴۴,۰۰۰", kcolor=SUB, h=50, rule=False)
    p.kv("تخفیف کد", "- ۵۰,۰۰۰", kcolor=SUB, vcolor=RED, h=50, rule=False)
    p.kv("هزینه ارسال", "۶۳,۰۰۰", kcolor=SUB, h=50, rule=False)
    p.kv("امتیاز وفاداری", "- ۵,۰۰۰", kcolor=SUB, vcolor=RED, h=50, rule=False)
    y0 = SH - 140
    p.d.rectangle([0, y0, SW, SH], fill=WHITE)
    p.d.line([0, y0, SW, y0], fill=LINE, width=2)
    p.txt(IR - 8, y0 + 40, "۵۵۲,۰۰۰ تومان", 28, "Bold", BRAND, "rm")
    p.txt(IR - 8, y0 + 78, "مبلغ نهایی", 19, "Regular", SUB, "rm")
    bw = 340
    p.d.rounded_rectangle([IL, y0 + 24, IL + bw, y0 + 108], radius=42, fill=BRAND)
    p.d.text((IL + bw / 2, y0 + 66), fa("پرداخت"), font=font(26, "Bold"), fill=WHITE, anchor="mm")
    p.y = SH
    return p.save("checkout")


def sc_pet():
    """پرونده حیوان خانگی - Pet Profile"""
    p = Phone(title="پرونده حیوان", right_text="ویرایش", left_icon="share")
    # identity card
    p.d.rounded_rectangle([IL, p.y, IR, p.y + 232], radius=22, fill=BRAND_SOFT,
                          outline=BRAND, width=3)
    p.avatar(IR - 84, p.y + 74, 54, "ش", fill=WHITE, color=BRAND, ring=WHITE)
    p.txt(IR - 160, p.y + 46, "شکاری", 32, "Bold", INK, "rm")
    p.txt(IR - 160, p.y + 92, "گربه ایرانی - نر - اخته", 22, "Regular", SUB, "rm")
    p.chip("کارت سلامت", left=IL + 20, y=p.y + 22, bg=WHITE, fg=BRAND, h=38, size=18)
    p.d.line([IL + 20, p.y + 146, IR - 20, p.y + 146], fill="#CBE6E0", width=2)
    stats = [("سن", "۳ سال"), ("وزن", "۴.۵ کگ"), ("میکروچیپ", "۹۸۱۰۲۰۰۰۰"), ("تولد", "۱۴۰۲/۰۵/۱۱")]
    cw = (IR - IL - 40) / 4
    for i, (k, v) in enumerate(stats):
        cx = IR - 20 - cw * (i + 0.5)
        p.txt_fit(cx, p.y + 166, v, cw - 8, 23, "Bold", BRAND, "ma")
        p.txt_fit(cx, p.y + 198, k, cw - 8, 18, "Regular", SUB, "ma")
    p.y += 254
    p.notice("آلرژی ثبت شده: مرغ و گندم", "در همه تجویزها و نسخه‌ها لحاظ می‌شود",
             bg=RED_SOFT, fg=RED)
    p.tabs(["پرونده پزشکی", "واکسن‌ها", "نوبت‌ها", "نسخه‌ها"], 0)
    p.section("آخرین سوابق پزشکی", "افزودن سابقه +")
    for t, s in [("ویزیت عمومی - دکتر شریفی", "۱۴۰۵/۰۶/۲۸ | کلینیک مهر | عادی"),
                 ("آزمایش خون کامل", "۱۴۰۵/۰۶/۲۸ | نرمال"),
                 ("جراحی ختنه", "۱۴۰۴/۱۱/۰۳ | بیمارستان پت‌کر | موفق"),
                 ("درمان عفونت ادراری", "۱۴۰۴/۰۹/۱۲ | پایان یافته")]:
        y0 = p.y
        p.d.rounded_rectangle([IL, y0, IR, y0 + 92], radius=16, fill=WHITE,
                              outline=LINE, width=3)
        p.icon("chat" if False else "box", IR - 40, y0 + 46, r=15, color=BRAND, w=4)
        p.txt_fit(IR - 74, y0 + 22, t, 380, 23, "Bold", INK, "rm")
        p.txt_fit(IR - 74, y0 + 56, s, 380, 19, "Regular", SUB, "rm")
        p.icon("chev_l", IL + 20, y0 + 46, r=11, color="#AAB2BF", w=4)
        p.y += 104
    p.gap(8)
    p.section("واکسیناسیون")
    p.timeline([("نوبت بعدی واکسن ثلاث", "۱۴۰۵/۱۰/۲۰ - باقی‌مانده: ۲ ماه"),
                ("واکسن سه‌گانه", "۱۴۰۵/۰۴/۱۵ - تزریق شده"),
                ("مایه‌کوبی هاری", "۱۴۰۴/۱۰/۱۵ - تزریق شده")], current=0, gap_h=76)
    y0 = SH - 138
    p.d.rectangle([0, y0, SW, SH], fill=WHITE)
    p.d.line([0, y0, SW, y0], fill=LINE, width=2)
    p.d.rounded_rectangle([IR - 200, y0 + 24, IR, y0 + 108], radius=42, fill=WHITE,
                          outline=BRAND, width=4)
    p.d.text((IR - 100, y0 + 66), fa("رزرو نوبت"), font=font(25, "Bold"), fill=BRAND, anchor="mm")
    p.d.rounded_rectangle([IL, y0 + 24, IL + 460, y0 + 108], radius=42, fill=BRAND)
    p.d.text((IL + 230, y0 + 66), fa("ویزیت آنلاین"), font=font(25, "Bold"),
             fill=WHITE, anchor="mm")
    p.y = SH
    return p.save("pet-profile")


def sc_tracking():
    p = Phone(title="پیگیری سفارش", right_text="تماس")
    p.txt(IR, p.y + 16, "سفارش #۱۲۳۴", 30, "Bold", INK, "rm")
    p.chip("در حال ارسال", left=IL, y=p.y + 12, bg=GOLD_SOFT, fg="#8A6A2B", h=44, size=20)
    p.y += 62
    p.kv("فروشگاه", "پت‌شاپ لایف‌لند", kcolor=SUB, h=52, rule=False, bold=True)
    p.kv("هزینه ارسال / کد رهگیری", "۳۵,۰۰۰ تومان - LK88213", kcolor=SUB, h=52, rule=False)
    p.gap(10)
    p.timeline([
        ("ثبت سفارش", "۱۴۰۵/۰۷/۱۰ ساعت ۱۰:۱۲"),
        ("تأیید فروشنده", "۱۴۰۵/۰۷/۱۰ ساعت ۱۰:۴۰"),
        ("آماده‌سازی", "۱۴۰۵/۰۷/۱۰ ساعت ۱۳:۰۵"),
        ("تحویل به پیک", "۱۴۰۵/۰۷/۱۱ ساعت ۰۹:۲۰"),
        ("در حال ارسال", "۱۴۰۵/۰۷/۱۱ ساعت ۱۰:۰۵"),
        ("تحویل شده", "در انتظار"),
    ], current=4, gap_h=76)
    # delivery code box
    p.d.rounded_rectangle([IL, p.y, IR, p.y + 156], radius=20, fill=BRAND_SOFT,
                          outline=BRAND, width=4)
    p.txt(SW // 2, p.y + 24, "کد تحویل شما", 22, "Medium", SUB, "ma")
    p.txt(SW // 2, p.y + 58, "۴ • ۸ • ۲ • ۱ • ۹ • ۶", 44, "Bold", BRAND, "ma")
    p.txt(SW // 2, p.y + 116, "فقط در وضعیت «در حال ارسال» - تا ۲۴ ساعت معتبر",
          18, "Regular", SUB, "ma")
    p.y += 176
    p.notice("این کد را به پیک بگویید", "با پوش و پیامک هم برای شما ارسال شد")
    p.gap(4)
    p.section("پیک سفارش")
    p.avatar(IR - 36, p.y + 44, 36, "ع")
    p.txt(IR - 86, p.y + 26, "علی محمدی", 25, "Bold", INK, "rm")
    p.txt(IR - 86, p.y + 60, "پیک فروشگاه - پراید سفید ۲۲ ب۴۵۷", 20, "Regular", SUB, "rm")
    p.chip("تماس", left=IL + 4, y=p.y + 30, bg=BRAND, fg=WHITE, h=44, size=20)
    p.y += 106
    p.gap(6)
    p.section("پس از تحویل ثبت می‌شود")
    p.kv("نام گیرنده / نسبت", "زهرا رضایی - همسر", kcolor=SUB, h=52)
    p.kv("ساعت تحویل", "۱۴۰۵/۰۷/۱۱ - ۱۱:۳۵", kcolor=SUB, h=52)
    p.kv("عکس بسته", "⬇ ثبت شده", kcolor=SUB, h=52, vcolor=BRAND)
    y0 = SH - 140
    p.d.rectangle([0, y0, SW, SH], fill=WHITE)
    p.d.line([0, y0, SW, y0], fill=LINE, width=2)
    p.d.rounded_rectangle([IL, y0 + 24, IL + 320, y0 + 108], radius=42, fill=WHITE,
                          outline=RED, width=4)
    p.d.text((IL + 160, y0 + 66), fa("ثبت مشکل"), font=font(25, "Bold"), fill=RED, anchor="mm")
    p.d.rounded_rectangle([IR - 340, y0 + 24, IR, y0 + 108], radius=42, fill=BRAND)
    p.d.text((IR - 170, y0 + 66), fa("تأیید دریافت"), font=font(25, "Bold"),
             fill=WHITE, anchor="mm")
    p.y = SH
    return p.save("order-tracking")


def sc_courier():
    p = Phone(title="تأیید تحویل سفارش")
    p.notice("لینک اختصاصی این سفارش - بدون نیاز به نصب اپ",
             "اعتبار: ۲۴ ساعت پس از ارسال", bg=BLUE_SOFT, fg="#31538F")
    p.section("اطلاعات سفارش")
    p.kv("شماره سفارش", "#۱۲۳۴", kcolor=SUB, h=52, bold=True)
    p.kv("آدرس مشتری", "تهران، سعادت‌آباد، علامه شمالی", kcolor=SUB, h=52)
    p.kv("تعداد اقلام", "۳ قلم - ۲ فروشگاه", kcolor=SUB, h=52)
    p.gap(10)
    p.section("کد تحویل ۶ رقمی (از مشتری بگیرید)")
    p.code_boxes(6, filled=4)
    p.notice("۲ تلاش باقی‌مانده", "۳ تلاش اشتباه = قفل ۱۵ دقیقه + پیامک به مشتری",
             bg=RED_SOFT, fg=RED)
    p.field("نام گیرنده", "زهرا رضایی", placeholder=False, h=76)
    p.txt(IR, p.y, "نسبت با خریدار", 22, "Medium", INK, "ra")
    p.y += 36
    p.pills(["خود خریدار", "همسر", "خانواده", "همسایه"], per_row=4, active=1)
    p.txt(IR, p.y + 4, "عکس بسته (اجباری)", 22, "Medium", INK, "ra")
    p.y += 40
    p.d.rounded_rectangle([IL, p.y, IR, p.y + 170], radius=18, fill=BOX,
                          outline=RED, width=4, )
    p.icon("camera", SW // 2, p.y + 70, r=26, color=RED, w=6)
    p.txt(SW // 2, p.y + 116, "عکس بسته را بگیرید", 22, "Bold", RED, "ma")
    p.y += 188
    p.d.line([IL, p.y, IR, p.y], fill=LINE, width=2)
    p.y += 18
    p.txt(IR, p.y + 20, "موقعیت مکانی هنگام تحویل", 23, "Medium", INK, "rm")
    p.txt(IR, p.y + 54, "اختیاری - توصیه می‌شود", 19, "Regular", SUB, "rm")
    p.toggle(IR, p.y + 34, on=True)
    p.y += 92
    p.button("ثبت تحویل", disabled=False)
    p.gap(16)
    p.notice("مشتری در دسترس نیست؟", "گزینه‌های جایگزین: آدرس اشتباه / کسی نیست / محل کسب‌باز",
             bg=BOX, fg=SUB)
    return p.save("courier-delivery")


def sc_visit():
    p = Phone(title="ویزیت آنلاین", right_text="گزارش")
    p.chip("در حال ویزیت - ۰۸:۳۲", right=IR, y=p.y + 10, bg=BRAND_SOFT, fg=BRAND, h=44, size=20)
    p.txt(IL, p.y + 32, "۱۵:۰۰ از ۲۰ دقیقه", 20, "Medium", SUB, "lm")
    p.y += 70
    p.d.rounded_rectangle([IL, p.y, IR, p.y + 380], radius=22, fill="#1E2A3A")
    p.avatar(SW // 2, p.y + 150, 76, "د", fill="#33455C", color="#9FB3CC", ring=None)
    p.txt(SW // 2, p.y + 246, "دکتر مریم شریفی", 26, "Bold", WHITE, "ma")
    p.txt(SW // 2, p.y + 284, "دامپزشک - کلینیک مهر", 20, "Regular", "#9FB3CC", "ma")
    p.d.rounded_rectangle([IL + 24, p.y + 300, IL + 184, p.y + 460], radius=16,
                          fill="#3B5068", outline="#6C829B", width=3)
    p.avatar(IL + 104, p.y + 380, 46, "م", fill="#4A617B", color="#C9D6E5")
    p.y += 402
    # controls
    ctrls = [("chat", False), ("phone", False), ("camera", False), ("gear", False)]
    n = len(ctrls) + 1
    w = (IR - IL) / n
    for i, (ic, _) in enumerate(ctrls):
        cx = IR - w * (i + 0.5)
        p.d.ellipse([cx - 42, p.y, cx + 42, p.y + 84], fill=BOX)
        p.icon(ic, cx, p.y + 42, r=17, color=INK, w=5)
    cx = IR - w * (len(ctrls) + 0.5)
    p.d.ellipse([cx - 42, p.y, cx + 42, p.y + 84], fill=RED)
    p.icon("phone", cx, p.y + 42, r=17, color=WHITE, w=5)
    p.txt(cx, p.y + 94, "پایان تماس", 18, "Medium", RED, "ma")
    p.y += 126
    p.section("پرونده حیوان (اشتراک‌گذاری شده)")
    p.d.rounded_rectangle([IL, p.y, IR, p.y + 160], radius=18, fill=BRAND_SOFT,
                          outline=BRAND, width=3)
    p.avatar(IR - 60, p.y + 60, 38, "ش", fill=WHITE, color=BRAND, ring=WHITE)
    p.txt(IR - 112, p.y + 32, "شکاری - گربه ایرانی", 25, "Bold", INK, "rm")
    p.txt(IR - 112, p.y + 70, "۳ سال | ۴.۵ کگ | نر اخته", 20, "Regular", SUB, "rm")
    p.txt(IL + 16, p.y + 34, "آلرژی: مرغ، گندم", 18, "Bold", RED, "lm")
    p.txt_fit(IR - 20, p.y + 116, "آخرین سابقه: ویزیت ۱۴۰۵/۰۶/۲۸", 560, 20, "Regular", SUB, "rm")
    p.y += 182
    p.section("نسخه و توصیه (پس از پایان)")
    p.d.rounded_rectangle([IL, p.y, IR, p.y + 148], radius=18, fill=WHITE,
                          outline=LINE, width=3)
    p.txt_fit(IR - 20, p.y + 26, "پماد چشمی ۲ بار در روز - ۵ روز", 600, 23, "Medium", INK, "rm")
    p.txt_fit(IR - 20, p.y + 66, "آزمایش خون توصیه می‌شود", 600, 21, "Regular", SUB, "rm")
    p.chip("دانلود نسخه", right=IR - 20, y=p.y + 100, bg=BRAND, fg=WHITE, h=40, size=18)
    p.chip("اشتراک با کلینیک", right=IR - 170, y=p.y + 100, bg=BOX, fg=INK, h=40, size=18)
    return p.save("online-visit")


def sc_chat():
    p = Phone(title="پت‌شاپ لایف‌لند", back=True)
    p.avatar(IL + 30, p.y - 43, 26, "پ")
    p.txt(IL + 66, p.y - 56, "آنلاین", 18, "Medium", BRAND, "lm")
    p.sysmsg("سفارش #۱۲۳۴ ثبت شد")
    p.gap(6)
    p.sysmsg("پرداخت انجام شد - ۵۵۷,۰۰۰ تومان")
    p.gap(10)
    p.bubble("سلام، آیا این غذا برای گربه مناسبه؟", me=True, time="۱۰:۲۲", status="✓✓ خوانده شده")
    p.bubble("سلام، بله. برای گربه بالغ ایرانی عالیه", me=False, time="۱۰:۲۴")
    p.bubble("لینک محصول: غذای خشک گربه بالغ", me=False, time="۱۰:۲۴")
    p.bubble("ممنون. ارسال چند روزه به تهران؟", me=True, time="۱۰:۲۵", status="✓✓")
    p.bubble("۱ تا ۲ روز کاری با پیک فروشگاه", me=False, time="۱۰:۲۶")
    p.sysmsg("سفارش در حال ارسال است - کد تحویل ۴۸۲۱۹۶")
    p.gap(8)
    p.bubble("بسته ارسال شد، کد تحویل رو پیامک کردم", me=False, time="۱۰:۵۸")
    p.bubble("ممنون", me=True, time="۱۱:۰۲", status="✓ ارسال شده")
    p.gap(4)
    # typing
    p.d.rounded_rectangle([IL, p.y, IL + 120, p.y + 52], radius=18, fill="#EDF1F6")
    for i in range(3):
        cx = IL + 30 + i * 28
        p.d.ellipse([cx - 7, p.y + 19, cx + 7, p.y + 33], fill="#98A2B3")
    p.y += 70
    p.inputbar()
    return p.save("chat")


def sc_seller_dash():
    p = Phone(title="داشبورد فروشنده", left_icon="gear", back=False, right_text=None)
    p.avatar(IR - 40, p.y + 40, 40, "پ")
    p.txt(IR - 96, p.y + 20, "پت‌شاپ لایف‌لند", 27, "Bold", INK, "rm")
    p.txt(IR - 96, p.y + 56, "فروشنده تأیید شده - ⭐ ۴.۸", 20, "Regular", SUB, "rm")
    p.y += 100
    g = 16
    w = (IR - IL - g) // 2
    h = 120
    metrics = [("۲۴", "سفارش امروز", BRAND), ("۸", "در انتظار تأیید", "#B7791F"),
               ("۳٫۲ میلیون", "فروش امروز", BRAND), ("۱۲", "کالای ناموجود", RED)]
    for i, (v, l, c) in enumerate(metrics):
        col, row = i % 2, i // 2
        x1 = IR - col * (w + g)
        x0 = x1 - w
        y0 = p.y + row * (h + g)
        p.metric(x0, x1, y0, y0 + h, v, l, c)
    p.y += 2 * h + g + 24
    p.section("کارهای امروز", "مشاهده همه")
    for t, s, n in [("تأیید سفارش جدید", "سفارش #۱۲۳۵ - ۲ قلم", "۵"),
                    ("پاسخ به چت مشتریان", "۳ پیام خوانده نشده", "۳"),
                    ("کالای ناموجود", "۱۲ کالا نیاز به شارژ موجودی", "۱۲"),
                    ("نظرات جدید", "۲ نظر بدون پاسخ", "۲")]:
        p.row(t, s, badge_text=n)
    p.gap(14)
    p.section("دسترسی سریع")
    g2 = 14
    w2 = (IR - IL - g2 * 2) // 3
    quick = ["افزودن کالا", "مدیریت موجودی", "کد تخفیف", "گزارش فروش", "مدیریت نوبت", "کیف پول"]
    for i, q in enumerate(quick):
        col, row = i % 3, i // 3
        x1 = IR - col * (w2 + g2)
        x0 = x1 - w2
        y0 = p.y + row * (110 + g2)
        p.d.rounded_rectangle([x0, y0, x1, y0 + 110], radius=16, fill=BRAND_SOFT,
                              outline=BRAND, width=3)
        p.icon(["box", "chart", "plus", "wallet", "cal", "gear"][i],
               (x0 + x1) / 2, y0 + 40, r=15, color=BRAND, w=4)
        p.txt_fit((x0 + x1) / 2, y0 + 74, q, w2 - 12, 18, "Bold", INK, "ma")
    p.y += 2 * 110 + g2 + 20
    p.section("گزارش فروش ۷ روز اخیر")
    p.d.rounded_rectangle([IL, p.y, IR, p.y + 200], radius=18, fill=WHITE,
                          outline=LINE, width=3)
    base = p.y + 170
    vals = [60, 90, 55, 120, 100, 150, 130]
    bw = 46
    for i, v in enumerate(vals):
        x1 = IR - 34 - i * (bw + 16)
        bh = v
        p.d.rounded_rectangle([x1 - bw, base - bh, x1, base], radius=8,
                              fill=BRAND if i == 6 else "#9ED6C9")
        p.d.text((x1 - bw / 2, base + 8), fa(["ش", "ی", "د", "س", "چ", "پ", "ج"][i]),
                 font=font(18), fill=SUB, anchor="ma")
    p.y += 216
    return p.save("seller-dashboard")


def sc_seller_bookings():
    p = Phone(title="مدیریت نوبت‌ها", left_icon="cal")
    p.pills(["امروز", "فردا", "هفته", "لغو شده", "تمام شده"], per_row=5, active=0)
    p.gap(8)
    p.kv("تعداد نوبت امروز", "۸ نوبت - ۲ در انتظار تأیید", kcolor=SUB, h=52,
         bold=True, rule=False)
    p.gap(6)
    slots = [("۰۹:۰۰", "نگار - گربه", "گرومینگ", "تأیید شده", BRAND),
             ("۱۰:۳۰", "امیر - سگ", "ویزیت حضوری", "در انتظار", "#B7791F"),
             ("۱۲:۰۰", "سارا - پرنده", "ویزیت آنلاین", "تأیید شده", BRAND),
             ("۱۴:۰۰", "رضا - اسب", "ویزیت در محل", "در انتظار", "#B7791F"),
             ("۱۶:۰۰", "مینا - گربه", "واکسن", "لغو شده", RED),
             ("۱۸:۰۰", "بهرام - دام", "ویزیت دام بزرگ", "تأیید شده", BRAND)]
    for time, who, svc, st, col in slots:
        y0 = p.y
        p.d.rounded_rectangle([IL, y0, IR, y0 + 122], radius=16, fill=WHITE,
                              outline=LINE, width=3)
        p.d.rounded_rectangle([IR - 96, y0 + 1, IR - 1, y0 + 121], radius=15,
                              fill=BRAND_SOFT)
        p.txt(IR - 48, y0 + 46, time, 25, "Bold", BRAND, "ma")
        p.txt(IR - 48, y0 + 82, svc[:9], 15, "Regular", SUB, "ma")
        p.txt_fit(IR - 114, y0 + 26, who, 300, 24, "Bold", INK, "rm")
        p.txt_fit(IR - 114, y0 + 62, svc, 300, 20, "Regular", SUB, "rm")
        p.chip(st, left=IL + 14, y=y0 + 16, bg=BOX if col == RED else (
            BRAND_SOFT if col == BRAND else "#FDF3E3"),
               fg=col if col != RED else RED, h=36, size=17)
        if st == "در انتظار":
            p.d.rounded_rectangle([IL + 14, y0 + 66, IL + 116, y0 + 106], radius=20,
                                  fill=BRAND)
            p.txt(IL + 65, y0 + 86, "تأیید", 18, "Bold", WHITE, "mm")
            p.d.rounded_rectangle([IL + 128, y0 + 66, IL + 230, y0 + 106], radius=20,
                                  fill=WHITE, outline=RED, width=3)
            p.txt(IL + 179, y0 + 86, "لغو", 18, "Bold", RED, "mm")
        else:
            p.txt_fit(IL + 14, y0 + 80, "جزئیات >", 200, 19, "Medium", SUB, "lm")
        p.y += 134
    p.gap(6)
    p.notice("ساعت‌های خالی امروز: ۳ اسلات", "برای فعال‌سازی از تقویم استفاده کنید")
    return p.save("seller-bookings")


def sc_seller_shipping():
    p = Phone(title="مدیریت ارسال و پیک‌ها", left_icon="box")
    p.tabs(["سفارش‌ها", "پیک‌ها", "مناطق ارسال"], 0)
    p.pills(["در انتظار", "آماده‌سازی", "تحویل پیک", "ارسال شده"], per_row=4, active=1)
    p.gap(6)
    p.notice("۳ سفارش در انتظار ارسال", "۲۴ ساعت فرصت آماده‌سازی دارید",
             bg=GOLD_SOFT, fg="#8A6A2B")
    orders = [("#۱۲۳۵", "محمد رضایی - ۲ قلم", "۳۵,۰۰۰", "تحویل پیک"),
              ("#۱۲۳۶", "نگار احمدی - ۱ قلم", "۲۸,۰۰۰", "آماده‌سازی"),
              ("#۱۲۳۷", "رضا کریمی - ۴ قلم", "رایگان", "در انتظار"),
              ("#۹۸۷۶", "سارا مرادی - ۲ قلم", "۳۵,۰۰۰", "ارسال شده"),
              ("#۹۸۷۵", "امیر قاسمی - ۱ قلم", "۲۸,۰۰۰", "ارسال شده")]
    for oid, who, cost, st in orders:
        y0 = p.y
        p.d.rounded_rectangle([IL, y0, IR, y0 + 138], radius=16, fill=WHITE,
                              outline=LINE, width=3)
        p.txt_fit(IR - 20, y0 + 26, "سفارش " + oid, 300, 24, "Bold", INK, "rm")
        p.txt_fit(IR - 20, y0 + 62, who, 340, 20, "Regular", SUB, "rm")
        p.txt_fit(IR - 20, y0 + 98, "ارسال: " + cost, 300, 21, "Bold", BRAND, "rm")
        p.chip(st, left=IL + 16, y=y0 + 16,
               bg=BRAND_SOFT if st == "ارسال شده" else (
                   "#FDF3E3" if st != "در انتظار" else BOX),
               fg=BRAND if st == "ارسال شده" else ("#B7791F" if st != "در انتظار" else SUB),
               h=36, size=17)
        if st != "ارسال شده":
            p.d.rounded_rectangle([IL + 16, y0 + 68, IL + 216, y0 + 116], radius=24,
                                  fill=BRAND)
            p.txt(IL + 116, y0 + 92, "تولید لینک تحویل", 19, "Bold", WHITE, "mm")
        else:
            p.txt_fit(IL + 16, y0 + 92, "کد رهگیری: LK8821", 300, 19, "Medium", SUB, "lm")
        p.y += 150
    p.gap(4)
    p.section("پیک‌های فروشگاه")
    p.row("علی محمدی", "پراید سفید - ۲۲ ب۴۵۷ - ۱۲ ارسال", note="فعال")
    p.row("حسین نوری", "پژو ۲۰۶ - ۵۸ د۳۲۱ - ۴ ارسال", note="فعال")
    p.gap(10)
    p.notice("پیک خارج از تیم؟", "لینک تحویل اختصاصی بفرستید - نیازی به نصب اپ ندارد",
             bg=BLUE_SOFT, fg="#31538F")
    return p.save("seller-shipping")


def sc_seller_wallet():
    p = Phone(title="کیف پول و تسویه", left_icon="wallet")
    p.d.rounded_rectangle([IL, p.y, IR, p.y + 230], radius=24, fill=BRAND)
    p.txt(IR - 30, p.y + 44, "موجودی قابل برداشت", 23, "Regular", "#CFEDE6", "rm")
    p.txt(IR - 30, p.y + 84, "۸٬۴۵۰,۰۰۰ تومان", 44, "Bold", WHITE, "rm")
    p.d.line([IL + 26, p.y + 154, IR - 26, p.y + 154], fill="#2E9B86", width=2)
    cw = (IR - IL - 52) / 3
    for i, (v, l) in enumerate([("۲٬۱۰۰,۰۰۰", "کارمزد ماه"), ("۳۰ روز", "دوره تسویه"),
                                ("۱۴۰۵/۰۷/۱۵", "واریز بعدی")]):
        cx = IR - 26 - cw * (i + 0.5)
        p.txt(cx, p.y + 174, v, 21, "Bold", WHITE, "ma")
        p.txt(cx, p.y + 204, l, 17, "Regular", "#CFEDE6", "ma")
    p.y += 252
    g = 16
    w = (IR - IL - g) // 2
    for i, (v, l, c) in enumerate([("۱۲٬۳۰۰,۰۰۰", "فروش خالص ماه", BRAND),
                                   ("۲٬۱۰۰,۰۰۰", "کارمزد AMPET", RED)]):
        x1 = IR - i * (w + g)
        p.metric(x1 - w, x1, p.y, p.y + 120, v, l, c)
    p.y += 144
    p.section("درخواست تسویه", "تاریخچه")
    p.notice("تسویه خودکار هر ۱۴ روز", "ماه اول: ۳۰ روز پس از اولین فروش - فقط به شماره شبا")
    p.d.rounded_rectangle([IL, p.y, IR, p.y + 118], radius=16, fill=WHITE,
                          outline=LINE, width=3)
    p.txt_fit(IR - 20, p.y + 24, "شماره شبای ثبت‌شده", 340, 21, "Regular", SUB, "rm")
    p.txt_fit(IR - 20, p.y + 58, "IR۸۲ ۰۵۷۰ ۰۲۲۲ ۸۰۰۲ ۰۳۶۰ ۰۰۰۰ ۰۱", 480, 24,
              "Bold", INK, "rm")
    p.chip("تأیید شده", right=IR - 20, y=p.y + 82, bg=BRAND_SOFT, fg=BRAND, h=32, size=17)
    p.y += 140
    p.button("درخواست تسویه زودتر از موعد", h=80, color=WHITE, fg=BRAND, outline=BRAND)
    p.gap(22)
    p.section("آخرین تراکنش‌ها")
    for t, s, v, c in [("سفارش #۱۲۳۴", "۱۴۰۵/۰۷/۱۱ - پس از تحویل", "+ ۴۹۲,۰۰۰", BRAND),
                       ("کارمزد فروش", "۱۴۰۵/۰۷/۱۱ - ۵٪", "- ۲۶,۰۰۰", RED),
                       ("تسویه بانکی", "۱۴۰۵/۰۷/۰۱ - IR82...", "- ۳,۲۰۰,۰۰۰", INK),
                       ("مرجوعی سفارش #۱۲۱۰", "۱۴۰۵/۰۶/۲۸", "- ۲۴۹,۰۰۰", RED)]:
        y0 = p.y
        p.icon("wallet", IR - 26, y0 + 34, r=15, color=BRAND, w=4)
        p.txt_fit(IR - 60, y0 + 16, t, 300, 23, "Medium", INK, "rm")
        p.txt_fit(IR - 60, y0 + 50, s, 340, 19, "Regular", SUB, "rm")
        p.txt_fit(IL, y0 + 34, v, 240, 24, "Bold", c, "lm")
        p.d.line([IL, y0 + 74, IR, y0 + 74], fill="#EEF1F5", width=2)
        p.y += 86
    return p.save("seller-wallet")


def sc_add_product():
    p = Phone(title="افزودن کالای جدید", right_text="ذخیره پیش‌نویس")
    p.section("تصاویر محصول (حداکثر ۸ عدد)")
    p.imgph([IR - 150, p.y, IR, p.y + 150], radius=16)
    for i in range(2):
        x1 = IR - 166 - i * 158
        p.d.rounded_rectangle([x1 - 150, p.y, x1, p.y + 150], radius=16, fill=BOX,
                              outline=LINE, width=3)
        p.icon("plus", x1 - 75, p.y + 75, r=20, color="#AAB2BF", w=5)
    p.y += 172
    p.field("عنوان کالا *", "غذای خشک سگ بالغ ۱۰ کیلویی", placeholder=False)
    p.field("دسته‌بندی *", "سگ > غذا > خشک ⌄", placeholder=False)
    p.field("برند", "Royal Canin", placeholder=False)
    p.field("قیمت (تومان) *", "۲۴۹,۰۰۰", placeholder=False, trailing="ریال ⇄")
    p.field("قیمت قبل از تخفیف", "۳۱۲,۰۰۰", placeholder=False)
    p.field("موجودی *", "۴۵ عدد", placeholder=False, trailing="موجودی")
    p.field("وزن / حجم", "۱۰ کیلوگرم", placeholder=False)
    p.txt(IR, p.y, "مناسب برای حیوانات", 22, "Medium", INK, "ra")
    p.y += 36
    p.pills(["سگ", "گربه", "پرنده", "اگزوتیک", "دام", "اسب"], per_row=3, active=0)
    p.gap(6)
    p.field("توضیحات کامل", "غذای خشک متعادل برای سگ بالغ ...", placeholder=True, h=110)
    p.section("تنظیمات ارسال فروشگاه")
    p.kv("هزینه ارسال پیش‌فرض", "۳۵,۰۰۰ تومان", kcolor=SUB, h=54)
    p.kv("زمان آماده‌سازی", "۱ روز کاری", kcolor=SUB, h=54)
    p.kv("مناطق ارسال", "تهران، کرج، اصفهان", kcolor=SUB, h=54)
    p.gap(16)
    p.button("انتشار کالا")
    p.gap(14)
    return p.save("add-product")


def sc_add_service():
    p = Phone(title="افزودن خدمت جدید", right_text="ذخیره پیش‌نویس")
    p.field("عنوان خدمت *", "گرومینگ کامل سگ", placeholder=False)
    p.section("دسته‌بندی خدمت *")
    p.pills(["گرومینگ", "ویزیت حضوری", "ویزیت آنلاین", "واکسن",
             "پانسیون", "تاکسی", "آزمایش", "کافه پت"], per_row=4, active=0)
    p.gap(6)
    p.field("قیمت پایه (تومان) *", "۳۵۰,۰۰۰", placeholder=False)
    p.field("مدت تقریبی", "۹۰ دقیقه", placeholder=False)
    p.txt(IR, p.y, "مناسب برای حیوانات", 22, "Medium", INK, "ra")
    p.y += 36
    p.pills(["سگ", "گربه", "پرنده", "اگزوتیک"], per_row=4, active=0)
    p.gap(6)
    p.section("ساعت‌های کاری (تقویم رزرو)")
    days = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه"]
    w = (IR - IL - 8 * 6) / 7
    for i, d in enumerate(days):
        x1 = IR - i * (w + 8)
        x0 = x1 - w
        on = i < 6
        p.d.rounded_rectangle([x0, p.y, x1, p.y + 74], radius=12,
                              fill=BRAND_SOFT if on else BOX,
                              outline=BRAND if on else LINE, width=3)
        p.txt((x0 + x1) / 2, p.y + 22, d[:6], 15, "Bold" if on else "Medium",
              BRAND if on else SUB, "ma")
        p.txt((x0 + x1) / 2, p.y + 50, "۹-۱۸" if on else "تعطیل", 14,
              "Regular", SUB, "ma")
    p.y += 96
    p.section("ظرفیت همزمان")
    p.radio("۱ نوبت همزمان", selected=True, h=72)
    p.radio("۲ نوبت همزمان", h=72)
    p.radio("۳ نوبت همزمان", h=72)
    p.gap(6)
    p.section("قوانین کنسلی (الزامی)")
    p.kv("رایگان تا", "۲۴ ساعت قبل", kcolor=SUB, h=54, bold=True)
    p.kv("جریمه ۲۴ تا ۲ ساعت", "۳۰٪ مبلغ", kcolor=SUB, h=54, vcolor=RED, bold=True)
    p.kv("کمتر از ۲ ساعت / عدم حضور", "۱۰۰٪ مبلغ", kcolor=SUB, h=54, vcolor=RED, bold=True)
    p.gap(16)
    p.button("انتشار خدمت")
    p.gap(14)
    return p.save("add-service")


def sc_add_provider():
    p = Phone(title="افزودن سرویس‌دهنده", right_text="ذخیره پیش‌نویس")
    p.section("نوع سرویس‌دهنده *")
    p.pills(["پت‌شاپ", "گرومر", "کلینیک", "بیمارستان", "دامپزشک",
             "دام بزرگ", "پانسیون", "عمده‌فروش", "واردکننده", "بیمارستان+پانسیون"],
            per_row=3, active=2)
    p.gap(6)
    p.notice("انتخاب نوع، فیلدهای ثبت‌نام را تغییر می‌دهد",
             "کلینیک: مجوز، شماره نظام دامپزشکی، بیمه‌نامه")
    p.field("نام / عنوان *", "کلینیک دامپزشکی مهر", placeholder=False)
    p.field("شماره تماس *", "۰۲۱ ۸۸۷۷۶۶۵۵", placeholder=False)
    p.field("استان / شهر *", "تهران / تهران ⌄", placeholder=False)
    p.field("آدرس *", "خیابان ولیعصر، بالاتر از پارک‌وی", placeholder=False, h=90)
    p.field("شماره نظام دامپزشکی *", "۱۲۳۴۵", placeholder=False)
    p.field("شماره ثبت / مجوز کسب‌وکار", "۴۱۱۳۵۶۷۸۹۰", placeholder=False)
    p.field("کد ملی مسئول *", "۰۰۸۴۵۶۷۸۹۰", placeholder=False)
    p.field("شماره شبا (برای تسویه) *", "IR۸۲ ۰۵۷۰ ...", placeholder=False)
    p.txt(IR, p.y, "لوگو و تصاویر محل", 22, "Medium", INK, "ra")
    p.y += 36
    p.imgph([IR - 130, p.y, IR, p.y + 130], radius=16)
    p.d.rounded_rectangle([IL, p.y, IR - 146, p.y + 130], radius=16, fill=BOX,
                          outline=LINE, width=3)
    p.icon("plus", (IL + IR - 146) / 2, p.y + 65, r=20, color="#AAB2BF", w=5)
    p.y += 152
    p.notice("پس از ثبت، ادمین بررسی می‌کند", "وضعیت: در انتظار تأیید - تا ۷۲ ساعت",
             bg=GOLD_SOFT, fg="#8A6A2B")
    p.button("ثبت درخواست")
    p.gap(14)
    return p.save("add-provider")


def sc_manage_providers():
    p = Phone(title="مدیریت سرویس‌دهندگان", left_icon="filter")
    p.searchbox("جستجو بر اساس نام یا شماره ...", h=76)
    p.gap(14)
    p.pills(["همه (۲۴)", "تأیید شده (۱۸)", "در انتظار (۴)", "رد شده (۲)"],
            per_row=4, active=0)
    p.gap(6)
    provs = [("کلینیک دامپزشکی مهر", "کلینیک - تهران", "تأیید شده", BRAND),
             ("گرومر حیوانات شاد", "گرومر - شیراز", "تأیید شده", BRAND),
             ("بیمارستان پت‌کر", "بیمارستان+پانسیون - تهران", "در انتظار", "#B7791F"),
             ("دامپزشک مهندس رستمی", "دامپزشک - اصفهان", "در انتظار", "#B7791F"),
             ("مرکز دام بزرگ کرمان", "دام بزرگ - کرمان", "رد شده", RED),
             ("پت‌شاپ لایف‌لند", "پت‌شاپ - تهران", "تأیید شده", BRAND)]
    for name, sub, st, col in provs:
        y0 = p.y
        p.d.rounded_rectangle([IL, y0, IR, y0 + 130], radius=16, fill=WHITE,
                              outline=LINE, width=3)
        p.avatar(IR - 54, y0 + 65, 34, name[0])
        p.txt_fit(IR - 104, y0 + 32, name, 340, 23, "Bold", INK, "rm")
        p.txt_fit(IR - 104, y0 + 68, sub, 340, 19, "Regular", SUB, "rm")
        p.chip(st, left=IL + 16, y=y0 + 84, bg=BRAND_SOFT if col == BRAND else (
            "#FDF3E3" if col != RED else RED_SOFT),
               fg=col if col != RED else RED, h=36, size=17)
        p.txt_fit(IL + 16, y0 + 30, "⭐ ۴." + str(6 + (y0 // 100) % 3), 200, 20,
                  "Bold", GOLD, "lm")
        p.icon("chev_l", IR - 26, y0 + 65, r=11, color="#AAB2BF", w=4)
        p.y += 142
    p.gap(8)
    p.notice("۴ درخواست در انتظار بررسی", "میانگین زمان بررسی: ۷۲ ساعت")
    return p.save("manage-providers")


def sc_admin():
    p = Phone(title="پنل مدیریت AMPET", back=False, left_icon="gear")
    p.avatar(IR - 40, p.y + 40, 40, "ا")
    p.txt(IR - 96, p.y + 20, "مدیر سیستم", 27, "Bold", INK, "rm")
    p.txt(IR - 96, p.y + 56, "دسترسی کامل - ۸ نقش تعریف شده", 20, "Regular", SUB, "rm")
    p.chip("زنده", left=IL + 4, y=p.y + 34, bg=BRAND, fg=WHITE, h=38, size=18)
    p.y += 104
    g = 14
    w = (IR - IL - g) // 2
    for i, (v, l, c) in enumerate([("۱٬۲۴۰", "کاربر فعال", BRAND),
                                   ("۸۶", "فروشنده تأیید شده", BRAND),
                                   ("۳۲۰", "سفارش امروز", BRAND),
                                   ("۱۸٫۴ میلیون", "درآمد امروز", BRAND)]):
        col, row = i % 2, i // 2
        x1 = IR - col * (w + g)
        p.metric(x1 - w, x1, p.y + row * (116 + g), p.y + row * (116 + g) + 116, v, l, c)
    p.y += 2 * 116 + g + 24
    p.section("صفحات مدیریتی (۲۰ بخش)")
    items = [("تأیید فروشندگان", "۴ در انتظار", "۴"),
             ("مدیریت کاربران", "۱٬۲۴۰ فعال", ""),
             ("مدیریت سفارش‌ها", "۱۸ در انتظار", "۱۸"),
             ("مدیریت مرجوعی‌ها", "۳ درخواست", "۳"),
             ("کدهای تخفیف", "۱۲ کد فعال", ""),
             ("کمپین‌ها و بنرها", "۳ بنر فعال", ""),
             ("دسته‌بندی و ویژگی‌ها", "۶ حیوان - ۲۴ دسته", ""),
             ("محتوا و مقالات", "۴۵ مقاله", ""),
             ("تیکت‌های پشتیبانی", "۷ باز", "۷"),
             ("گزارش چت‌ها", "۲ گزارش جدید", "۲")]
    for t, s, n in items:
        p.row(t, s, badge_text=n)
    p.gap(14)
    p.section("نظارت و مالی")
    p.tabs(["کیف پول", "تسویه‌ها", "کارمزد", "گزارش"], 0)
    p.kv("کارمزد فعال", "۵٪ - قابل تغییر توسط ادمین", kcolor=SUB, h=54, bold=True)
    p.kv("تسویه‌های در انتظار", "۱۲ فروشنده - ۸۶ میلیون", kcolor=SUB, h=54)
    p.kv("مغایرت مالی", "۰ مورد", kcolor=SUB, h=54, vcolor=BRAND)
    p.gap(14)
    p.notice("RBAC: ۸ نقش × ۲۳ عملکرد", "ادمین، مالی، پشتیبانی، محتوا، ناظر، تأییدکننده، فروشنده، مشتری",
             bg=BLUE_SOFT, fg="#31538F")
    return p.save("admin-panel")


def sc_booking():
    """رزرو نوبت - انتخاب ارائه‌دهنده و زمان"""
    p = Phone(title="رزرو نوبت", right_text="خدمات")
    p.section("انتخاب ارائه‌دهنده", "همه")
    provs = [
        ("دکتر سارا شریفی", "دامپزشک - معاینه عمومی", "امتیاز ۴.۸  |  ۲.۱ کیلومتر", True),
        ("کلینیک حیوانات مهر", "بیمارستان - شبانه‌روزی", "امتیاز ۴.۶  |  ۴.۸ کیلومتر", False),
        ("گرومینگ آرامش", "گرومر - حمام و اصلاح مو", "امتیاز ۴.۹  |  ۱.۲ کیلومتر", False),
    ]
    for name, sub, meta, sel in provs:
        y0 = p.y
        p.d.rounded_rectangle([IL, y0, IR, y0 + 116], radius=18,
                              fill=BRAND_SOFT if sel else WHITE,
                              outline=BRAND if sel else LINE,
                              width=4 if sel else 3)
        p.avatar(IR - 62, y0 + 58, 40, name.replace("دکتر ", "")[0])
        p.txt_fit(IR - 114, y0 + 24, name, 320, 24, "Bold", INK, "rm")
        p.txt_fit(IR - 114, y0 + 56, sub, 320, 19, "Regular", SUB, "rm")
        p.txt_fit(IR - 114, y0 + 84, meta, 320, 18, "Medium", BRAND, "rm")
        if sel:
            p.icon("check", IL + 34, y0 + 58, r=15, color=BRAND, w=5)
        else:
            p.d.ellipse([IL + 20, y0 + 44, IL + 48, y0 + 72], outline="#AAB2BF", width=4)
        p.y += 128
    p.gap(6)
    p.section("تاریخ")
    p.pills(["۱۲ شنبه", "۱۳ یک‌شنبه", "۱۴ دوشنبه", "۱۵ سه‌شنبه"],
            per_row=4, h=64, active=1)
    p.section("ساعت شروع")
    slots = [("۰۹:۰۰", "free"), ("۱۰:۳۰", "busy"), ("۱۲:۰۰", "free"), ("۱۴:۰۰", "free"),
             ("۱۵:۳۰", "sel"), ("۱۷:۰۰", "free"), ("۱۸:۳۰", "busy"), ("۲۰:۰۰", "free")]
    cols, hh, g = 4, 66, 12
    w = (IR - IL - g * (cols - 1)) // cols
    for i, (t, st) in enumerate(slots):
        r_, c_ = i // cols, i % cols
        x1 = IR - c_ * (w + g)
        x0 = x1 - w
        yy = p.y + r_ * (hh + g)
        fill = {"free": WHITE, "busy": BOX, "sel": BRAND}[st]
        out = {"free": BRAND, "busy": LINE, "sel": BRAND}[st]
        fg = {"free": BRAND, "busy": "#AAB2BF", "sel": WHITE}[st]
        p.d.rounded_rectangle([x0, yy, x1, yy + hh], radius=14, fill=fill,
                              outline=out, width=3)
        p.d.text(((x0 + x1) / 2, yy + hh / 2), fa(t), font=font(21, "Bold"),
                 fill=fg, anchor="mm")
    p.y += 2 * hh + g + 22
    p.section("حیوان", "تغییر")
    p.row("شکاری", "گربه ایرانی - نر - ۳ سال", note="۴.۵ کگ", h=98, chevron=True)
    p.notice("پس از ثبت، ارائه‌دهنده تا ۲۴ ساعت فرصت تأیید دارد",
             "پرداخت فقط پس از تأیید او فعال می‌شود", bg=BLUE_SOFT, fg="#31538F")
    y0 = SH - 140
    p.d.rectangle([0, y0, SW, SH], fill=WHITE)
    p.d.line([0, y0, SW, y0], fill=LINE, width=2)
    p.txt(IR - 8, y0 + 40, "۳۵۰,۰۰۰ تومان", 28, "Bold", BRAND, "rm")
    p.txt(IR - 8, y0 + 78, "معاینه عمومی - ۳۰ دقیقه", 19, "Regular", SUB, "rm")
    bw = 340
    p.d.rounded_rectangle([IL, y0 + 24, IL + bw, y0 + 108], radius=42, fill=BRAND)
    p.d.text((IL + bw / 2, y0 + 66), fa("درخواست رزرو"), font=font(26, "Bold"),
             fill=WHITE, anchor="mm")
    p.y = SH
    return p.save("booking")


def sc_booking_detail():
    """جزئیات نوبت + لغو و جریمه"""
    p = Phone(title="جزئیات نوبت", right_text="تغییر زمان")
    y0 = p.y
    p.d.rounded_rectangle([IL, y0, IR, y0 + 146], radius=20, fill=GOLD_SOFT)
    p.txt_fit(IR - 26, y0 + 34, "در انتظار پرداخت مشتری", 420, 27, "Bold", "#8A6A2B", "rm")
    p.txt_fit(IR - 26, y0 + 76, "مهلت باقی‌مانده برای پرداخت", 420, 20, "Regular", "#8A6A2B", "rm")
    p.txt(IL + 26, y0 + 56, "۰۱:۴۷:۲۲", 34, "Bold", "#8A6A2B", "lm")
    p.chip("تأیید ارائه‌دهنده شد", right=IR - 26, y=y0 + 96, bg=WHITE, fg=BRAND,
           h=38, size=18)
    p.y += 166
    p.section("مشخصات نوبت")
    p.kv("ارائه‌دهنده", "دکتر سارا شریفی", h=56, rule=True, bold=True)
    p.kv("خدمت", "معاینه عمومی - ۳۰ دقیقه", h=56)
    p.kv("تاریخ و ساعت", "۱۴۰۵/۰۷/۱۳ - ۱۵:۳۰", h=56)
    p.kv("حیوان", "شکاری - گربه ایرانی", h=56)
    p.kv("مبلغ قابل پرداخت", "۳۵۰,۰۰۰ تومان", h=56, bold=True, vcolor=BRAND)
    p.gap(8)
    p.section("وضعیت نوبت")
    p.timeline([("ثبت درخواست", "۱۴۰۵/۰۷/۱۲ - ۲۰:۱۴"),
                ("تأیید ارائه‌دهنده", "۱۴۰۵/۰۷/۱۲ - ۲۰:۴۱"),
                ("پرداخت مشتری", "در انتظار"),
                ("یادآوری ۲ ساعت قبل", "آینده"),
                ("برگزاری نوبت", "۱۴۰۵/۰۷/۱۳ - ۱۵:۳۰")], current=2, gap_h=70)
    p.section("جریمه لغو مشتری")
    for a, b, c in [("بیش از ۲۴ ساعت قبل", "رایگان", "بازگشت کامل"),
                    ("۲۴ ساعت تا ۲ ساعت قبل", "۳۰٪", "۲۴۵,۰۰۰ بازمی‌گردد"),
                    ("کمتر از ۲ ساعت / عدم حضور", "۱۰۰٪", "بازگشتی ندارد")]:
        yy = p.y
        p.d.rounded_rectangle([IL, yy, IR, yy + 64], radius=14, fill=WHITE,
                              outline=LINE, width=3)
        p.txt_fit(IR - 16, yy + 32, a, 252, 19, "Medium", INK, "rm")
        cw_ = p.chip(b, left=IL + 14, y=yy + 12, bg=RED_SOFT if b == "۱۰۰٪" else BRAND_SOFT,
                     fg=RED if b == "۱۰۰٪" else BRAND, h=40, size=19)
        nx = IL + 14 + cw_ + 14
        p.txt_fit(nx, yy + 32, c, IR - nx - 276, 18, "Regular", SUB, "lm")
        p.y += 74
    p.notice("کمتر از ۲ ساعت مانده، لغو معادل ۱۰۰٪ جریمه است",
             "پیش از لغو، مبلغ دقیق جریمه نمایش داده می‌شود", bg=RED_SOFT, fg=RED)
    y0 = SH - 140
    p.d.rectangle([0, y0, SW, SH], fill=WHITE)
    p.d.line([0, y0, SW, y0], fill=LINE, width=2)
    p.d.rounded_rectangle([IL, y0 + 24, IL + 300, y0 + 108], radius=42, fill=WHITE,
                          outline=RED, width=4)
    p.d.text((IL + 150, y0 + 66), fa("لغو نوبت"), font=font(25, "Bold"), fill=RED,
             anchor="mm")
    p.d.rounded_rectangle([IR - 370, y0 + 24, IR, y0 + 108], radius=42, fill=BRAND)
    p.d.text((IR - 185, y0 + 66), fa("پرداخت ۳۵۰,۰۰۰"), font=font(25, "Bold"),
             fill=WHITE, anchor="mm")
    p.y = SH
    return p.save("booking-detail")


def sc_address():
    """دفترچه آدرس + گیرنده + بازه تحویل"""
    p = Phone(title="آدرس تحویل", right_text="افزودن +")
    p.section("آدرس‌های من")
    adds = [("خانه", "تهران، سعادت‌آباد، خیابان علامه شمالی، پلاک ۱۲، واحد ۴",
             "گیرنده: خودم - ۰۹۱۲۳۴۵۶۷۸۹", True),
            ("محل کار", "تهران، ولیعصر، برج نگین، طبقه ۹، واحد ۹۰۲",
             "گیرنده: زهرا رضایی (همسر) - ۰۹۱۲۹۸۷۶۵۴۳", False),
            ("پدر و مادر", "کرج، گوهردشت، خیابان ارشد، کوچه ۴، پلاک ۸",
             "گیرنده: علی رضایی (پدر) - ۰۹۳۵۱۱۲۲۳۳۴", False)]
    for title, addr, rec, sel in adds:
        y0 = p.y
        p.d.rounded_rectangle([IL, y0, IR, y0 + 168], radius=18,
                              fill=BRAND_SOFT if sel else WHITE,
                              outline=BRAND if sel else LINE,
                              width=4 if sel else 3)
        cx = IR - 34
        cy = y0 + 40
        p.d.ellipse([cx - 15, cy - 15, cx + 15, cy + 15],
                    outline=BRAND if sel else "#AAB2BF", width=4)
        if sel:
            p.d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=BRAND)
        p.txt_fit(cx - 30, cy, title, 200, 24, "Bold", INK, "rm")
        if sel:
            p.chip("پیش‌فرض", left=IL + 16, y=y0 + 18, bg=WHITE, fg=BRAND, h=34, size=17)
        p.txt_fit(IR - 26, y0 + 78, addr, 540, 20, "Regular", SUB, "rm")
        p.txt_fit(IR - 26, y0 + 110, rec, 540, 19, "Medium", INK, "rm")
        p.d.line([IL + 20, y0 + 134, IR - 20, y0 + 134], fill="#E3E7EE", width=2)
        p.txt_fit(IR - 26, y0 + 152, "ویرایش", 120, 19, "Medium", BRAND, "rm")
        p.txt_fit(IL + 26, y0 + 152, "حذف", 120, 19, "Medium", RED, "lm")
        p.y += 180
    p.section("بازه تحویل")
    p.pills(["۰۹ - ۱۲", "۱۲ - ۱۶", "۱۶ - ۲۰", "۲۰ - ۲۲"], per_row=4, h=64, active=1)
    p.notice("ساعت تحویل توسط شما انتخاب می‌شود",
             "ارسال بر عهده فروشگاه است و AMPET مسئولیتی ندارد",
             bg=BLUE_SOFT, fg="#31538F")
    p.section("نوع گیرنده")
    p.radio("خودم", "تحویل به شخص سفارش‌دهنده", selected=True)
    p.radio("شخص دیگر", "نام، نسبت و شماره تماس اجباری می‌شود")
    y0 = SH - 140
    p.d.rectangle([0, y0, SW, SH], fill=WHITE)
    p.d.line([0, y0, SW, y0], fill=LINE, width=2)
    p.d.rounded_rectangle([IL, y0 + 24, IR, y0 + 108], radius=42, fill=BRAND)
    p.d.text((SW / 2, y0 + 66), fa("تأیید آدرس و بازه تحویل"), font=font(26, "Bold"),
             fill=WHITE, anchor="mm")
    p.y = SH
    return p.save("address")


def sc_wallet():
    """کیف پول مشتری"""
    p = Phone(title="کیف پول", left_icon="note")
    y0 = p.y
    p.d.rounded_rectangle([IL, y0, IR, y0 + 206], radius=24, fill=BRAND)
    p.txt_fit(IR - 30, y0 + 40, "موجودی قابل برداشت", 400, 22, "Medium", "#CFEBE4", "rm")
    p.txt_fit(IR - 30, y0 + 96, "۱,۲۴۵,۰۰۰ تومان", 500, 44, "Bold", WHITE, "rm")
    p.d.line([IL + 26, y0 + 140, IR - 26, y0 + 140], fill="#3FA08D", width=2)
    p.txt_fit(IR - 30, y0 + 172, "در انتظار تسویه: ۳۸۰,۰۰۰", 340, 21, "Medium",
              "#CFEBE4", "rm")
    p.txt_fit(IL + 30, y0 + 172, "امتیاز: ۲,۴۵۰", 300, 21, "Medium", "#CFEBE4", "lm")
    p.y += 226
    gw = (IR - IL - 16) // 2
    p.d.rounded_rectangle([IR - gw, p.y, IR, p.y + 86], radius=20, fill=BRAND)
    p.d.text(((IR - gw + IR) / 2, p.y + 43), fa("شارژ کیف پول"), font=font(24, "Bold"),
             fill=WHITE, anchor="mm")
    p.d.rounded_rectangle([IL, p.y, IL + gw, p.y + 86], radius=20, fill=WHITE,
                          outline=BRAND, width=4)
    p.d.text((IL + gw / 2, p.y + 43), fa("برداشت به بانک"), font=font(24, "Bold"),
             fill=BRAND, anchor="mm")
    p.y += 106
    p.notice("برداشت طبق چرخه ۱۴ روزه پرداخت می‌شود",
             "چرخه ۱ (پیش از نخستین فروش تحویل‌شده) = ۳۰ روز")
    p.section("تاریخچه تراکنش‌ها", "همه")
    p.pills(["همه", "شارژ", "برداشت", "سفارش"], per_row=4, h=58, active=0)
    txs = [("شارژ کیف پول", "۱۴۰۵/۰۷/۱۱ - کارت ۶۰۳۷", "+ ۵۰۰,۰۰۰", BRAND),
           ("سفارش #۱۲۳۴ - پت‌شاپ لایف‌لند", "۱۴۰۵/۰۷/۱۰ - پرداخت درگاه", "- ۵۵۲,۰۰۰", RED),
           ("بازگشت وجه - مرجوعی #۸۷۱", "۱۴۰۵/۰۷/۰۸ - تأیید فروشنده", "+ ۲۱۰,۰۰۰", BRAND),
           ("برداشت به حساب بانکی", "۱۴۰۵/۰۶/۳۰ - شبا IR۱۲", "- ۱,۰۰۰,۰۰۰", RED),
           ("پاداش دعوت دوستان", "۱۴۰۵/۰۶/۲۸ - معرف: رضا", "+ ۵۰,۰۰۰", BRAND)]
    for t, s, v, c in txs:
        p.row(t, s, h=94, chevron=False, img=False)
        p.txt_fit(IL + 16, p.y - 47, v, 220, 24, "Bold", c, "lm")
    p.gap(6)
    p.notice("موجودی کیف پول فقط برای خرید قابل استفاده است",
             "برداشت بانکی نیازمند ثبت شبا و تأیید ۲ مرحله‌ای", bg=BOX, fg="#5B6474")
    y0 = SH - 134
    p.bottom_nav(["خانه", "سبد", "نوبت‌ها", "حساب"], active=3)
    return p.save("wallet")


def sc_payment_result():
    """نتیجه پرداخت"""
    p = Phone(title="نتیجه پرداخت")
    p.y += 26
    cx, cy = SW // 2, p.y + 78
    p.d.ellipse([cx - 78, cy - 78, cx + 78, cy + 78], fill=BRAND_SOFT)
    p.d.ellipse([cx - 60, cy - 60, cx + 60, cy + 60], fill=BRAND)
    p.icon("check", cx, cy, r=30, color=WHITE, w=9)
    p.y += 176
    p.txt(SW // 2, p.y, "پرداخت موفق", 36, "Bold", INK, "ma")
    p.y += 54
    p.txt(SW // 2, p.y, "۵۵۲,۰۰۰ تومان", 40, "Bold", BRAND, "ma")
    p.y += 74
    p.kv("شماره سفارش", "#۱۲۳۴ و #۱۲۳۵", h=56, bold=True)
    p.kv("شماره پیگیری", "۴۵۸۷۲۹۱۲۳۴۵۶۷۸۹", h=56)
    p.kv("روش پرداخت", "درگاه بانکی - سامان", h=56)
    p.kv("زمان پرداخت", "۱۴۰۵/۰۷/۱۲ - ۲۱:۳۷", h=56)
    p.gap(10)
    p.section("خلاصه سفارش (۲ فروشگاه)")
    for shop, items, amt, st in [("پت‌شاپ لایف‌لند", "۳ قلم - ارسال پیک فروشگاه",
                                  "۵۵۲,۰۰۰", "در انتظار تأیید فروشنده"),
                                 ("داروخانه دامپزشکی مهر", "۱ قلم - ارسال پست پیشتاز",
                                  "۲۱۰,۰۰۰", "در انتظار تأیید فروشنده")]:
        y0 = p.y
        p.d.rounded_rectangle([IL, y0, IR, y0 + 116], radius=18, fill=WHITE,
                              outline=LINE, width=3)
        p.txt_fit(IR - 20, y0 + 30, shop, 330, 24, "Bold", INK, "rm")
        p.txt_fit(IR - 20, y0 + 64, items, 330, 19, "Regular", SUB, "rm")
        p.txt_fit(IL + 20, y0 + 32, amt, 200, 25, "Bold", BRAND, "lm")
        p.chip(st, left=IL + 20, y=y0 + 66, bg=GOLD_SOFT, fg="#8A6A2B", h=36, size=17)
        p.y += 128
    p.notice("پول نزد AMPET نگه‌داری می‌شود (اسکرو)",
             "پس از تأیید فروشنده و تحویل با کد، به فروشنده واریز خواهد شد",
             bg=BLUE_SOFT, fg="#31538F")
    y0 = SH - 140
    p.d.rectangle([0, y0, SW, SH], fill=WHITE)
    p.d.line([0, y0, SW, y0], fill=LINE, width=2)
    p.d.rounded_rectangle([IL, y0 + 24, IL + 300, y0 + 108], radius=42, fill=WHITE,
                          outline=BRAND, width=4)
    p.d.text((IL + 150, y0 + 66), fa("بازگشت به خانه"), font=font(24, "Bold"),
             fill=BRAND, anchor="mm")
    p.d.rounded_rectangle([IR - 370, y0 + 24, IR, y0 + 108], radius=42, fill=BRAND)
    p.d.text((IR - 185, y0 + 66), fa("پیگیری سفارش"), font=font(25, "Bold"),
             fill=WHITE, anchor="mm")
    p.y = SH
    return p.save("payment-result")


def sc_return_request():
    """درخواست مرجوعی کالا"""
    p = Phone(title="درخواست مرجوعی")
    y0 = p.y
    p.d.rounded_rectangle([IL, y0, IR, y0 + 118], radius=18, fill=WHITE,
                          outline=LINE, width=3)
    p.imgph([IR - 92, y0 + 16, IR - 16, y0 + 92], radius=12)
    p.txt_fit(IR - 108, y0 + 26, "غذای خشک گربه ۱۰ کیلو", 340, 23, "Bold", INK, "rm")
    p.txt_fit(IR - 108, y0 + 58, "سفارش #۱۲۳۴ - تحویل: ۱۴۰۵/۰۷/۱۰", 340, 19,
              "Regular", SUB, "rm")
    p.chip("۳ روز باقی‌مانده", left=IL + 18, y=y0 + 66, bg=GOLD_SOFT, fg="#8A6A2B",
           h=36, size=17)
    p.y += 136
    p.section("دلیل مرجوعی")
    p.radio("کالای آسیب‌دیده یا خراب", "در اثر حمل یا تولید", selected=True, h=76)
    p.radio("مغایرت با توضیحات", "رنگ، سایز یا مدل متفاوت", h=76)
    p.radio("کالای اشتباه ارسال شده", "اقلام سفارش دیگر", h=76)
    p.radio("انصراف از خرید", "فقط پیش از ارسال فروشنده", h=76)
    p.field("شرح مشکل (حداکثر ۵۰۰ حرف)", "اختیاری اما تسریع‌کننده رسیدگی",
            placeholder=True, h=88)
    p.section("نوع بازگرداندن کالا")
    p.radio("پیک فروشگاه", "فروشنده پیک می‌فرستد - رایگان", selected=True, h=76)
    p.radio("پست پیشتاز", "پیش‌پرداخت توسط AMPET - ۳ تا ۵ روز", h=76)
    p.notice("فروشنده ۷۲ ساعت فرصت پاسخ دارد",
             "در صورت عدم پاسخ، روش «پست پیشتاز» به‌طور خودکار اعمال می‌شود")
    y0 = SH - 140
    p.d.rectangle([0, y0, SW, SH], fill=WHITE)
    p.d.line([0, y0, SW, y0], fill=LINE, width=2)
    p.txt(IR - 8, y0 + 40, "۲۱۰,۰۰۰ تومان", 28, "Bold", BRAND, "rm")
    p.txt(IR - 8, y0 + 78, "بازگشت به کیف پول AMPET", 19, "Regular", SUB, "rm")
    p.d.rounded_rectangle([IL, y0 + 24, IL + 340, y0 + 108], radius=42, fill=BRAND)
    p.d.text((IL + 170, y0 + 66), fa("ثبت درخواست مرجوعی"), font=font(25, "Bold"),
             fill=WHITE, anchor="mm")
    p.y = SH
    return p.save("return-request")


def sc_orders():
    """لیست سفارش‌های من"""
    p = Phone(title="سفارش‌های من", left_icon="search")
    p.tabs(["همه", "در جریان", "تحویل شده", "مرجوعی"], active=1, h=62)
    orders = [
        ("پت‌شاپ لایف‌لند", "#۱۲۳۴ - ۳ قلم - ۱۴۰۵/۰۷/۱۲", "۵۵۲,۰۰۰",
         "در حال ارسال", GOLD_SOFT, "#8A6A2B", ["پیگیری", "لغو سفارش"]),
        ("داروخانه دامپزشکی مهر", "#۱۲۳۵ - ۱ قلم - ۱۴۰۵/۰۷/۱۲", "۲۱۰,۰۰۰",
         "در انتظار تأیید", BLUE_SOFT, "#31538F", ["پیگیری", "لغو سفارش"]),
        ("گرومینگ آرامش", "#۱۲۲۸ - خدمت - ۱۴۰۵/۰۷/۰۹", "۳۵۰,۰۰۰",
         "نوبت رزرو شده", BRAND_SOFT, BRAND, ["جزئیات نوبت", "لغو نوبت"]),
        ("پت‌شاپ لایف‌لند", "#۱۲۰۱ - ۲ قلم - ۱۴۰۵/۰۶/۲۸", "۴۸۰,۰۰۰",
         "تحویل شده", "#EDF6F3", "#2C7A67", ["ثبت نظر", "خرید مجدد"]),
        ("پت‌فود کرج", "#۱۱۸۸ - ۴ قلم - ۱۴۰۵/۰۶/۲۱", "۹۲۰,۰۰۰",
         "مرجوعی در حال بررسی", RED_SOFT, RED, ["جزئیات مرجوعی", "پشتیبانی"]),
    ]
    for shop, meta, amt, st, bg, fg, acts in orders:
        y0 = p.y
        p.d.rounded_rectangle([IL, y0, IR, y0 + 196], radius=18, fill=WHITE,
                              outline=LINE, width=3)
        p.txt_fit(IR - 20, y0 + 30, shop, 340, 24, "Bold", INK, "rm")
        p.chip(st, left=IL + 18, y=y0 + 16, bg=bg, fg=fg, h=40, size=18)
        p.txt_fit(IR - 20, y0 + 66, meta, 400, 19, "Regular", SUB, "rm")
        p.d.line([IL + 16, y0 + 96, IR - 16, y0 + 96], fill="#EEF1F5", width=2)
        p.txt_fit(IR - 20, y0 + 124, amt + " تومان", 240, 26, "Bold", BRAND, "rm")
        bw = (IR - IL - 16 - 12) // 2
        for k, a in enumerate(acts):
            x1 = IR - 16 - k * (bw + 12)
            x0 = x1 - bw
            prim = (k == len(acts) - 1)
            p.d.rounded_rectangle([x0, y0 + 148, x1, y0 + 184], radius=18,
                                  fill=BRAND if prim else WHITE,
                                  outline=None if prim else LINE, width=3)
            p.d.text(((x0 + x1) / 2, y0 + 166), fa(a), font=font(19, "Bold"),
                     fill=WHITE if prim else INK, anchor="mm")
        p.y += 210
    p.bottom_nav(["خانه", "سبد", "نوبت‌ها", "حساب"], active=3)
    return p.save("orders")


def sc_store():
    """صفحه فروشگاه"""
    p = Phone(title="فروشگاه", left_icon="share")
    y0 = p.y
    p.d.rounded_rectangle([IL, y0, IR, y0 + 216], radius=22, fill=BRAND_SOFT,
                          outline=BRAND, width=3)
    p.avatar(IR - 74, y0 + 70, 48, "ل", fill=WHITE, color=BRAND, ring=WHITE)
    p.txt(IR - 144, y0 + 44, "پت‌شاپ لایف‌لند", 30, "Bold", INK, "rm")
    p.txt(IR - 144, y0 + 84, "پت‌شاپ - سعادت‌آباد - تهران", 20, "Regular", SUB, "rm")
    p.chip("فروشنده تأیید شده", left=IL + 18, y=y0 + 22, bg=WHITE, fg=BRAND,
           h=36, size=17)
    p.chip("۴.۸ از ۱,۲۴۰ نظر", left=IL + 18, y=y0 + 66, bg=WHITE, fg="#8A6A2B",
           h=36, size=17)
    p.d.line([IL + 18, y0 + 126, IR - 18, y0 + 126], fill="#CBE6E0", width=2)
    stats = [("محصولات", "۳۴۲"), ("رضایت", "۹۶٪"), ("ارسال", "۱ تا ۲ روز"), ("سفارش", "۱۸K")]
    cw = (IR - IL - 36) / 4
    for i, (k, v) in enumerate(stats):
        cx = IR - 18 - cw * (i + 0.5)
        p.txt_fit(cx, y0 + 150, v, cw - 6, 24, "Bold", BRAND, "ma")
        p.txt_fit(cx, y0 + 184, k, cw - 6, 18, "Regular", SUB, "ma")
    p.y += 236
    gw = (IR - IL - 16) // 2
    p.d.rounded_rectangle([IR - gw, p.y, IR, p.y + 76], radius=20, fill=BRAND)
    p.d.text(((IR - gw + IR) / 2, p.y + 38), fa("دنبال‌کردن"), font=font(23, "Bold"),
             fill=WHITE, anchor="mm")
    p.d.rounded_rectangle([IL, p.y, IL + gw, p.y + 76], radius=20, fill=WHITE,
                          outline=BRAND, width=4)
    p.d.text((IL + gw / 2, p.y + 38), fa("چت با فروشگاه"), font=font(23, "Bold"),
             fill=BRAND, anchor="mm")
    p.y += 96
    p.tabs(["محصولات", "خدمات", "نظرات", "درباره"], active=0, h=62)
    p.pills(["همه", "خوراک", "بهداشتی", "لوازم"], per_row=4, h=56, active=0)
    items = [("غذای خشک گربه ۱۰ کیلو", "۲,۴۵۰,۰۰۰", "-۱۵٪"),
             ("بازی موشی پارچه‌ای", "۱۸۹,۰۰۰", ""),
             ("قلاده ضد پارازیت", "۳۲۰,۰۰۰", "۳۰٪"),
             ("توالت گربه ارگانیک", "۲۴۵,۰۰۰", "")]
    cols, g = 2, 16
    w = (IR - IL - g) // cols
    hc = 244
    for i, (nm, pr, off) in enumerate(items):
        r_, c_ = i // cols, i % cols
        x1 = IR - c_ * (w + g)
        x0 = x1 - w
        yy = p.y + r_ * (hc + g)
        p.d.rounded_rectangle([x0, yy, x1, yy + hc], radius=16, fill=WHITE,
                              outline=LINE, width=3)
        p.imgph([x0 + 12, yy + 12, x1 - 12, yy + 132], radius=12)
        if off:
            p.chip(off, right=x1 - 12, y=yy + 20, bg=RED, fg=WHITE, h=34, size=17)
        p.txt_fit(x1 - 14, yy + 158, nm, w - 28, 21, "Medium", INK, "rm")
        p.txt_fit(x1 - 14, yy + 196, pr, w - 28, 24, "Bold", BRAND, "rm")
        p.txt_fit(x1 - 14, yy + 224, "تومان", w - 28, 17, "Regular", SUB, "rm")
    p.y += 2 * (hc + g) + 6
    p.notice("ارسال این فروشگاه بر عهده خود فروشگاه است",
             "کد تحویل ۶ رقمی فقط در وضعیت «در حال ارسال» فعال می‌شود",
             bg=BLUE_SOFT, fg="#31538F")
    p.bottom_nav(["خانه", "سبد", "نوبت‌ها", "حساب"], active=0)
    return p.save("store")


# ======================================================================
SCENES = [
    ("login", "ورود با کد تأیید (OTP)", sc_login),
    ("home", "صفحه اصلی (Home)", sc_home),
    ("search", "جستجو (Search)", sc_search),
    ("store", "صفحه فروشگاه (Store Page)", sc_store),
    ("product", "جزئیات محصول (Product Details)", sc_product),
    ("cart", "سبد خرید چند فروشگاهی (Cart)", sc_cart),
    ("address", "آدرس، گیرنده و بازه تحویل (Address & Slot)", sc_address),
    ("checkout", "تسویه و پرداخت (Checkout)", sc_checkout),
    ("payment-result", "نتیجه پرداخت (Payment Result)", sc_payment_result),
    ("orders", "سفارش‌های من (My Orders)", sc_orders),
    ("booking", "رزرو نوبت (Booking)", sc_booking),
    ("booking-detail", "جزئیات نوبت و لغو (Booking Detail)", sc_booking_detail),
    ("return-request", "درخواست مرجوعی (Return Request)", sc_return_request),
    ("wallet", "کیف پول مشتری (Customer Wallet)", sc_wallet),
    ("pet-profile", "پرونده حیوان خانگی (Pet Profile)", sc_pet),
    ("order-tracking", "پیگیری سفارش (Order Tracking)", sc_tracking),
    ("courier-delivery", "تأیید تحویل پیک (Courier Delivery)", sc_courier),
    ("online-visit", "ویزیت آنلاین (Online Visit)", sc_visit),
    ("chat", "چت (Chat)", sc_chat),
    ("seller-dashboard", "داشبورد فروشنده (Seller Dashboard)", sc_seller_dash),
    ("seller-bookings", "مدیریت نوبت‌ها (Seller Bookings)", sc_seller_bookings),
    ("seller-shipping", "مدیریت ارسال و پیک‌ها (Seller Shipping)", sc_seller_shipping),
    ("seller-wallet", "کیف پول و تسویه (Seller Wallet)", sc_seller_wallet),
    ("add-product", "افزودن کالای جدید (Add Product)", sc_add_product),
    ("add-service", "افزودن خدمت جدید (Add Service)", sc_add_service),
    ("add-provider", "افزودن سرویس‌دهنده (Add Provider)", sc_add_provider),
    ("manage-providers", "مدیریت سرویس‌دهندگان (Manage Providers)", sc_manage_providers),
    ("admin-panel", "پنل مدیریت (Admin Panel)", sc_admin),
]


def generate_all(only_missing=True):
    paths = {}
    for key, title, fn in SCENES:
        path = os.path.join(OUT, key + ".png")
        if only_missing and os.path.exists(path):
            paths[key] = path
            continue
        try:
            paths[key] = fn()
        except Exception as e:
            print("FAILED %s: %s" % (key, e))
            raise
    return paths


if __name__ == "__main__":
    generate_all(only_missing=False)
    print("Generated %d wireframes in %s" % (len(SCENES), OUT))
