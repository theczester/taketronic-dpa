"""Taketronic DPA: generuje grafiki z ramką i feed XML dla Meta (zamiennik Cropink)."""
import hashlib, io, os, re, sys, shutil, urllib.request
import xml.etree.ElementTree as ET
from PIL import Image, ImageFont, ImageDraw

SRC = os.environ.get("SELLY_FEED_URL", "")      # pełny feed Facebook z Selly (wszystkie produkty)
BASE = os.environ.get("PUBLIC_BASE", "").rstrip("/")  # np. https://taketronic-dpa.pages.dev
OUT = os.environ.get("OUT_DIR", "out")
MIN_ITEMS = int(os.environ.get("MIN_ITEMS", "5"))
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "assets", "Montserrat-Bold.ttf")
LOGO = Image.open(os.path.join(HERE, "assets", "logo.png")).convert("RGBA")

G = "http://base.google.com/ns/1.0"
ET.register_namespace("g", G)
S = 1200
RED, GREEN, BLACK = (232, 25, 44), (0, 159, 66), (0, 0, 0)
IMG_BOX = (60, 80, 1140, 875)        # x0, y0, x1, y1 obszar zdjęcia (wg Figmy)
TITLE_Y, TITLE_MAX_W = 940, 1040     # środek pionowy tytułu (wg Figmy)
PRICE_RIGHT, PRICE_BASE = 1141, 1145
BAR_Y = 1160

def font(sz): return ImageFont.truetype(FONT, sz)

def fetch(url_or_path):
    if os.path.exists(url_or_path):
        return open(url_or_path, "rb").read()
    req = urllib.request.Request(url_or_path, headers={"User-Agent": "Mozilla/5.0 taketronic-dpa"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()

def fmt_price(p):
    m = re.match(r"\s*([\d.,]+)", p or "")
    if not m: return ""
    v = round(float(m.group(1).replace(",", ".")), 2)
    if v == int(v):
        return f"{int(v)} zł"                      # 8999 zł
    return f"{v:.2f}".replace(".", ",") + " zł"    # 1989,99 zł

def fit_title(draw, text):
    for sz in range(50, 33, -2):
        f = font(sz)
        if draw.textlength(text, font=f) <= TITLE_MAX_W:
            return [text], f
    f = font(38); words = text.split(); lines = [""]
    for w in words:
        t = (lines[-1] + " " + w).strip()
        if draw.textlength(t, font=f) <= TITLE_MAX_W or not lines[-1]: lines[-1] = t
        else: lines.append(w)
    return lines[:2], f

def render(product_img, title, price):
    can = Image.new("RGB", (S, S), "white")
    d = ImageDraw.Draw(can)
    p = Image.open(io.BytesIO(product_img)).convert("RGBA")
    bw, bh = IMG_BOX[2] - IMG_BOX[0], IMG_BOX[3] - IMG_BOX[1]
    sc = min(bw / p.width, bh / p.height)
    p = p.resize((max(1, round(p.width * sc)), max(1, round(p.height * sc))), Image.LANCZOS)
    can.paste(p, (IMG_BOX[0] + (bw - p.width) // 2, IMG_BOX[1] + (bh - p.height) // 2), p)
    lines, f = fit_title(d, title.upper())
    lh = f.size * 1.2; y0 = TITLE_Y - lh * len(lines) / 2
    for i, ln in enumerate(lines):
        d.text((S / 2, y0 + i * lh + lh / 2), ln, font=f, fill=BLACK, anchor="mm")
    can.paste(LOGO, (60, 1055), LOGO)
    pf = font(116)
    while d.textlength(price, font=pf) > 780: pf = font(pf.size - 4)
    d.text((PRICE_RIGHT, PRICE_BASE), price, font=pf, fill=RED, anchor="rs")
    d.rectangle((0, BAR_Y, S, S), fill=GREEN)
    return can

def main():
    if not SRC or not BASE:
        sys.exit("Brak SELLY_FEED_URL albo PUBLIC_BASE")
    root = ET.fromstring(fetch(SRC))
    items = root.findall(".//item")
    if len(items) < MIN_ITEMS:
        sys.exit(f"Za mało produktów w źródle ({len(items)}), nie publikuję")
    shutil.rmtree(OUT, ignore_errors=True); os.makedirs(os.path.join(OUT, "img"))
    ok = 0
    for it in items:
        g = lambda t: (it.findtext(f"{{{G}}}{t}") or "").strip()
        pid, title, img = g("id"), (g("title") or it.findtext("title") or ""), g("image_link")
        price = fmt_price(g("sale_price") or g("price"))
        if not img or img.endswith("empty.jpg"):
            print(f"[{pid}] brak zdjęcia w Selly, pomijam (zostaje w feedzie bez ramki)")
            continue
        try:
            raw = fetch(img)
            h = hashlib.md5((title + price).encode() + raw).hexdigest()[:8]
            name = f"{pid}-{h}.jpg"
            render(raw, title, price).save(os.path.join(OUT, "img", name), "JPEG", quality=90)
            el = it.find(f"{{{G}}}image_link"); el.text = f"{BASE}/img/{name}"
            ok += 1
        except Exception as e:
            print(f"[{pid}] błąd grafiki, zostawiam oryginalne zdjęcie: {e}")
    ET.ElementTree(root).write(os.path.join(OUT, "feed.xml"), encoding="utf-8", xml_declaration=True)
    open(os.path.join(OUT, ".nojekyll"), "w").close()
    print(f"Gotowe: {ok}/{len(items)} grafik, feed: {BASE}/feed.xml")
    if ok == 0: sys.exit("Żadna grafika się nie wygenerowała")

if __name__ == "__main__":
    main()
