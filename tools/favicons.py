"""Favicon set from tools/logo.py, written into site/:
    favicon.svg            sky tile, rounded corners (modern browsers)
    favicon.ico            16 + 32 px PNGs packed in an ICO (legacy, Windows)
    apple-touch-icon.png   180 px, full-bleed square (iOS rounds it itself)

Rasterizes with Playwright's chrome-headless-shell (or CHROME=/path/to/chrome).
    python3 tools/favicons.py
"""
import glob, os, struct, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(__file__))
import logo

# heavier line as the icon gets smaller, so the coil doesn't break up
STROKE = {16: 7.5, 32: 6.5, 180: 5.0, "svg": 5.5}
LEAD = 14

def tile(stroke, rounded=True):
    # 16 samples per half turn: ~4KB instead of ~15KB, no visible difference at icon sizes
    m = logo.mark(stroke=stroke, lead_out=LEAD, steps=16)
    return logo.svg(m, bg="sky", corner=0.19 if rounded else 0)

def chrome():
    if os.environ.get("CHROME"):
        return os.environ["CHROME"]
    hits = glob.glob(os.path.expanduser(
        "~/Library/Caches/ms-playwright/chromium_headless_shell-*/*/chrome-headless-shell"))
    if not hits:
        sys.exit("no chrome-headless-shell found; set CHROME=/path/to/chrome")
    return sorted(hits)[-1]

def png(svg_text, size, tmp):
    src = os.path.join(tmp, f"{size}.html")
    out = os.path.join(tmp, f"{size}.png")
    open(src, "w").write(
        f'<!doctype html><style>html,body{{margin:0;background:transparent}}'
        f'svg{{display:block;width:{size}px;height:{size}px}}</style>{svg_text}')
    subprocess.run([chrome(), "--headless", "--hide-scrollbars", "--force-device-scale-factor=1",
                    "--default-background-color=00000000", f"--window-size={size},{size}",
                    f"--screenshot={out}", "file://" + src],
                   check=True, capture_output=True)
    return open(out, "rb").read()

def ico(pngs):
    # ICO with embedded PNGs: header, one 16-byte entry per image, then the PNG bytes
    head = struct.pack("<HHH", 0, 1, len(pngs))
    offset = 6 + 16 * len(pngs)
    entries, blobs = b"", b""
    for size, data in pngs:
        entries += struct.pack("<BBBBHHII", size % 256, size % 256, 0, 0, 1, 32, len(data), offset)
        blobs += data
        offset += len(data)
    return head + entries + blobs

if __name__ == "__main__":
    site = sys.argv[1] if len(sys.argv) > 1 else "site"
    open(f"{site}/favicon.svg", "w").write(tile(STROKE["svg"]))
    with tempfile.TemporaryDirectory() as tmp:
        small = [(n, png(tile(STROKE[n]), n, tmp)) for n in (16, 32)]
        open(f"{site}/favicon.ico", "wb").write(ico(small))
        open(f"{site}/apple-touch-icon.png", "wb").write(png(tile(STROKE[180], rounded=False), 180, tmp))
    print("wrote", ", ".join(f"{site}/{f}" for f in ("favicon.svg", "favicon.ico", "apple-touch-icon.png")))
