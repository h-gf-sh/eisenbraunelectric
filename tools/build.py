"""Build the static eisenbraunelectric.co pages from the text captured off the live Wix site.

Run from the project root. Reads _reference/capture/{home,about}-rich.json (rendered rich-text HTML pulled with
Playwright) and writes site/index.html and site/about/index.html. Text is carried
over verbatim from the live markup; only Wix's styling spans are stripped.
"""
import json, re, html
from bs4 import BeautifulSoup, NavigableString

def load(name):
    d = json.load(open(f"_reference/capture/{name}-rich.json"))
    return {b["id"]: b["html"] for b in d["rts"]}

home, about = load("home"), load("about")

# Contact address moved off eisenbraunmusic.com (domain being wound down).
OLD_CONTACT, CONTACT = "tom@eisenbraunmusic.com", "tom@eisenbraunelectric.co"

def inline(node):
    """Serialize a node's children to clean inline HTML (em / strong / a / br)."""
    out = []
    for c in node.children:
        if isinstance(c, NavigableString):
            out.append(html.escape(str(c).replace(" ", " ").replace("​", ""), quote=False))
            continue
        st = (c.get("style") or "").replace(" ", "")
        inner = inline(c)
        if c.name == "br":
            out.append("<br>")
        elif c.name == "a":
            href = c.get("href", "")
            ext = c.get("target") == "_blank"
            attrs = f' href="{html.escape(href)}"' + (' target="_blank" rel="noopener"' if ext else "")
            out.append(f"<a{attrs}>{inner}</a>")
        elif "font-style:italic" in st:
            out.append(f"<em>{inner}</em>")
        elif "font-weight:bold" in st:
            out.append(f"<strong>{inner}</strong>")
        else:
            out.append(inner)
    return "".join(out)

def tidy(s):
    s = re.sub(r"[ \t]*\n[ \t]*", " ", s)          # source newlines are not meaningful
    s = re.sub(r" {2,}", " ", s)
    s = re.sub(r"\s*<br>\s*", "<br>", s)
    s = re.sub(r"^(<br>)+|(<br>)+$", "", s.strip())
    return s.strip()

def split_heading_block(h):
    """Wix blocks: <h1><br><span><span 22px>Title</span><br><span 16px>blurb</span></span><br>&nbsp;</h1>"""
    soup = BeautifulSoup(h, "html.parser")
    title_span = None
    for sp in soup.find_all("span"):
        st = (sp.get("style") or "").replace(" ", "")
        if re.search(r"font-size:(2[0-9])px", st) and sp.get_text(strip=True) not in ("", "]"):
            title_span = sp
            break
    title = tidy(inline(title_span))
    title_span.decompose()
    first_h1 = soup.find("h1", string=None)
    body_parts = []
    for el in soup.find_all(["h1", "p"], recursive=False):
        txt = el.get_text().replace(" ", "").replace("​", "").strip()
        if not txt:
            continue
        body_parts.append((el.name, tidy(inline(el))))
    return title, body_parts

def section_title_html(title):
    # "Still Life— released 2019" -> name + release note, kept verbatim
    m = re.match(r"^(.*?—)\s*(released \d{4})$", title)
    if m:
        return f'{m.group(1)} <span class="rel">{m.group(2)}</span>'
    return title

EMBEDS = {
    "light-is-sound-made-visible": ('youtube', 'https://www.youtube.com/embed/zcBaPQwS2ZA', 'Light Is Sound Made Visible [Visual Album w/o titles]'),
    "the-imagined-psaltery": ('soundcloud', 'https://w.soundcloud.com/player/?url=https%3A%2F%2Fapi.soundcloud.com%2Fplaylists%2F696557559&visual=true&show_artwork=true&color=%23ff5500&show_comments=true&show_playcount=true', 'from the imagined psaltery by Tom Eisenbraun'),
    "still-life": ('bandcamp', 'https://bandcamp.com/EmbeddedPlayer/album=1607365099/size=large/bgcol=333333/linkcol=ffffff/minimal=true/transparent=true/', 'Still Life by Tom Eisenbraun', 'https://tomeisenbraun.bandcamp.com/album/still-life'),
    "guided-meditation-for-the-solar-eclipse": ('bandcamp', 'https://bandcamp.com/EmbeddedPlayer/album=3446417610/size=large/bgcol=333333/linkcol=ffffff/minimal=true/transparent=true/', 'Guided Meditation for the Solar Eclipse by Tom Eisenbraun', 'https://tomeisenbraun.bandcamp.com/album/guided-meditation-for-the-solar-eclipse'),
    "memory-of-the-sound-of-home": ('bandcamp', 'https://bandcamp.com/EmbeddedPlayer/album=1065130046/size=large/bgcol=333333/linkcol=ffffff/minimal=true/transparent=true/', 'Memory of the Sound of Home by Tom Eisenbraun', 'https://tomeisenbraun.bandcamp.com/album/memory-of-the-sound-of-home'),
    "radio-ghost": ('bandcamp', 'https://bandcamp.com/EmbeddedPlayer/album=1572416429/size=large/bgcol=ffffff/linkcol=0687f5/minimal=true/transparent=true/', 'Radio Ghost by Tom Eisenbraun', 'https://tomeisenbraun.bandcamp.com/album/radio-ghost'),
    "slow-joy": ('bandcamp', 'https://bandcamp.com/EmbeddedPlayer/album=1723711786/size=large/bgcol=333333/linkcol=ffffff/minimal=true/transparent=true/', 'Slow Joy by Tom Eisenbraun', 'https://tomeisenbraun.bandcamp.com/album/slow-joy'),
    "the-october-country": ('bandcamp', 'https://bandcamp.com/EmbeddedPlayer/album=3081737407/size=large/bgcol=333333/linkcol=ffffff/minimal=true/transparent=true/', 'The October Country by Tom Eisenbraun', 'https://tomeisenbraun.bandcamp.com/album/the-october-country'),
}

def embed_html(slug):
    e = EMBEDS[slug]
    kind, src, title = e[0], e[1], e[2]
    t = html.escape(title)
    if kind == "youtube":
        return (f'<div class="embed embed-yt"><iframe src="{src}" title="{t}" loading="lazy" '
                f'allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
                f'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>')
    if kind == "soundcloud":
        return (f'<div class="embed embed-sc"><iframe src="{html.escape(src)}" title="{t}" loading="lazy" '
                f'allow="autoplay; encrypted-media"></iframe></div>')
    return (f'<div class="embed embed-bc"><iframe src="{src}" title="{t}" loading="lazy" seamless>'
            f'<a href="{e[3]}">{t}</a></iframe></div>')

# (slug, nav label, Wix block id) in page order
SECTIONS = [
    ("the-imagined-psaltery", "the imagined psaltery—", "comp-k4s80zyg"),
    ("still-life", "still life—", "comp-kqq2dn1r"),
    ("guided-meditation-for-the-solar-eclipse", "guided meditation for the solar eclipse—", "comp-kqq2mz7w"),
    ("memory-of-the-sound-of-home", "memory of the sound of home—", "comp-kqq2pjr5"),
    ("radio-ghost", "radio ghost—", "comp-kqq3az3u"),
    ("slow-joy", "slow joy—", "comp-kqq3ql3f"),
    ("the-october-country", "the october country—", "comp-kqq4ddj2"),
]
# Links are root-relative clean paths (what Vercel's cleanUrls serves), so no click
# goes through a 308. Preview with `vercel dev` from site/, not file://.
def nav_for(page):
    home = "#" if page == "home" else "/#"
    items = [("home", "/"),
             ("light is sound made visible—", home + "light-is-sound-made-visible")]
    items += [(label, home + slug) for slug, label, _ in SECTIONS]
    items += [("contact", "/about")]
    return items

def header(current, page):
    items = []
    for label, href in nav_for(page):
        cur = ' aria-current="page"' if label == current else ""
        items.append(f'<li><a href="{href}"{cur}>{label}</a></li>')
    return f"""<header class="site-header">
  <p class="site-title"><a href="/">Eisenbraun Electric Co.</a></p>
  <p class="site-tagline">[guitar arrangements by Tom Eisenbraun]</p>
  <nav aria-label="Sections"><ul>
    {chr(10).join('    ' + i for i in items).strip()}
  </ul></nav>
</header>"""

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
{desc}<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{title}">
{ogdesc}<meta property="og:url" content="{canonical}">
<meta property="og:type" content="website">
<meta property="og:image" content="https://eisenbraunelectric.co/assets/sky.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="{a}fonts/newsreader-latin-opsz-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{a}style.css">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
</head>
"""

def page_head(title, description, canonical, a):
    d = f'<meta name="description" content="{html.escape(description)}">\n' if description else ""
    od = f'<meta property="og:description" content="{html.escape(description)}">\n' if description else ""
    return HEAD.format(title=html.escape(title), desc=d, ogdesc=od, canonical=canonical, a=a)

# ---------- home ----------
essay_soup = BeautifulSoup(home["comp-m99cwcss"], "html.parser")
essay = [tidy(inline(h)) for h in essay_soup.find_all("h1") if h.get_text().replace(" ", "").strip()]

parts = []
parts.append(f"""<section id="light-is-sound-made-visible" class="sec sec-lead">
  <h2>light is sound made visible</h2>
  {embed_html("light-is-sound-made-visible")}
  <div class="essay">
    {chr(10).join(f'    <p>{p}</p>' for p in essay).strip()}
  </div>
</section>""")

for slug, label, cid in SECTIONS:
    title, body = split_heading_block(home[cid])
    body_html = []
    for tag, frag in body:
        if tag == "p":  # the quoted verse block under Slow Joy
            body_html.append(f'<p class="verse">{frag}</p>')
        else:
            # Radio Ghost carries its italic coda after a blank line: split on <br><br>
            for i, chunk in enumerate(frag.split("<br><br>")):
                body_html.append(f"<p>{chunk}</p>")
    # Slow Joy: "and right now" sits as its own verse paragraph after the excerpt
    parts.append(f"""<section id="{slug}" class="sec sec-{slug}">
  <h2>{section_title_html(title)}</h2>
  <div class="blurb">
    {chr(10).join('    ' + b for b in body_html).strip()}
  </div>
  {embed_html(slug)}
</section>""")

home_html = page_head("Tom Eisenbraun | Eisenbraun Electric Co",
                      "Electric guitar arrangements, experimental soundscapes, ambience for days.  Eisenbraun Electric Co.",
                      "https://eisenbraunelectric.co/", "/assets/") + f"""<body class="page-home">
<div class="sky" aria-hidden="true"></div>
<div class="frame">
{header("home", "home")}
<main>
{chr(10).join(parts)}
</main>
</div>
</body>
</html>
"""
open("site/index.html", "w").write(home_html)

# ---------- about ----------
ab = BeautifulSoup(about["comp-krgr82q5"], "html.parser")
raw = tidy(inline(ab.find("h1")))
chunks = [c.strip() for c in raw.split("<br><br>") if c.strip()]
# chunks[0] = "About—", then the paragraphs; the last holds "Correspondence welcomed:<br><strong><em>mail</em></strong>"
about_paras = "\n    ".join(f"<p>{c}</p>" for c in chunks[1:]).replace(OLD_CONTACT, CONTACT)
about_html = page_head("contact | eisenbraunelectric",
                       "",
                       "https://eisenbraunelectric.co/about", "/assets/") + f"""<body class="page-about">
<div class="sky" aria-hidden="true"></div>
<div class="frame">
{header("contact", "about")}
<main>
<section class="sec about">
  <h2>{chunks[0]}</h2>
  <div class="about-body">
    {about_paras}
  </div>
</section>
</main>
</div>
</body>
</html>
"""
open("site/about/index.html", "w").write(about_html)
print("wrote site/index.html", len(home_html), "and site/about/index.html", len(about_html))
