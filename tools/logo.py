"""Eisenbraun Electric Co. mark: an inductor (coil) symbol inside a circle, the coil's
open arcs and crossing loops reading as stacked cursive E's.

The coil is a prolate trochoid on a vertical axis:
    x(t) = cx - amp * cos(t)
    y(t) = y0 + pitch * t + kink * sin(t)
At t = 0, 2pi, ... the curve is at its left extreme moving fast (the open arcs of the E's);
at t = pi, 3pi, ... it is at its right extreme with dy/dt = pitch - kink < 0, so it doubles
back and crosses itself (the loops). kink / pitch sets loop size: > 1 for any loop at all.
The curve starts and ends on the axis (x = cx), where the vertical leads attach: it leaves
the top lead heading right, so the first and last features are loops, and the mark is
mirror-symmetric top to bottom. `arcs` open arcs sit between `arcs + 1` loops.

Everything is generated in a 100 x 100 box centered on (50, 50). Pure Python, no deps:
    python3 tools/logo.py [outdir]             # writes the logo set (default: logo/)
"""
import math

def coil_points(arcs, cx, top, bottom, amp, kink_ratio, steps=60):
    # loops at t = -pi, pi, ..., (2*arcs - 1)*pi; arcs at t = 0, 2pi, ..., 2*(arcs - 1)*pi
    t0, t1 = -1.5 * math.pi, 2 * (arcs - 1) * math.pi + 1.5 * math.pi
    # choose pitch so the curve's endpoints sit exactly at top and bottom
    # (sin is +1 at t0 and -1 at t1, so the kink terms shorten the span by 2 * kink)
    span = bottom - top
    pitch = span / ((t1 - t0) - 2 * kink_ratio)
    kink = kink_ratio * pitch
    y0 = top - (pitch * t0 + kink * math.sin(t0))
    n = int(steps * (t1 - t0) / math.pi)
    pts = []
    for i in range(n + 1):
        t = t0 + (t1 - t0) * i / n
        pts.append((cx - amp * math.cos(t), y0 + pitch * t + kink * math.sin(t)))
    return pts

def path_d(pts):
    # Catmull-Rom through the samples, emitted as cubic Beziers: smooth and compact
    d = [f"M{pts[0][0]:.2f},{pts[0][1]:.2f}"]
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C{c1[0]:.2f},{c1[1]:.2f} {c2[0]:.2f},{c2[1]:.2f} {p2[0]:.2f},{p2[1]:.2f}")
    return "".join(d)

def fillet(corner, coil, sign, reverse=False):
    """Classic fillet across the corner where the stem meets the coil. `coil` runs away
    from the corner; the fillet rejoins it at coil[-1] and leaves the stem the same
    arc length back from the corner, with both handles pointing at the corner (tangent
    to the stem and to the coil). For the bottom, reverse=True emits it coil -> stem."""
    L = sum(math.dist(coil[i], coil[i + 1]) for i in range(len(coil) - 1))
    jx, jy = coil[-1]
    tx, ty = coil[-1][0] - coil[-2][0], coil[-1][1] - coil[-2][1]
    n = math.hypot(tx, ty); tx, ty = tx / n, ty / n
    sx, sy = corner[0], corner[1] - sign * L       # back up the stem by L
    h = L * 0.55
    p1 = (sx, sy + sign * h)                       # stem tangent, toward the corner
    p2 = (jx - tx * h, jy - ty * h)                # coil tangent, toward the corner
    if not reverse:
        return f"V{sy:.2f}C{p1[0]:.2f},{p1[1]:.2f} {p2[0]:.2f},{p2[1]:.2f} {jx:.2f},{jy:.2f}"
    return f"C{p2[0]:.2f},{p2[1]:.2f} {p1[0]:.2f},{p1[1]:.2f} {sx:.2f},{sy:.2f}"

def mark(arcs=3, ring_r=36, fill=0.8, aspect=0.62, kink_ratio=2.2, roundover=0.12,
         lead_out=10, stroke=4.0, ring=True, steps=60):
    """Return the mark's geometry as SVG path data (stroked, no fill), 100x100 box.

    aspect: coil width / height between its endpoints. fill: the coil is scaled so its
    farthest point (end loops included, which rise past the endpoints) sits at
    fill * ring_r from the center, keeping even clearance inside the ring.
    roundover: size of the fillet where stem meets coil, as the fraction of a turn of coil
    it replaces (0 = sharp corner); the bottom mirrors the top.
    steps: samples per half turn; lower gives a smaller file (each sample is one cubic).
    """
    cx = cy = 50
    coil = coil_points(arcs, 0, -1, 1, aspect, kink_ratio, steps)
    reach = max(math.hypot(x, y) for x, y in coil)
    k = fill * ring_r / reach
    coil = [(cx + x * k, cy + y * k) for x, y in coil]
    # a fraction f of a turn is 2 * steps * f samples
    j = round(roundover * 2 * steps)
    body = coil[j:len(coil) - j]
    d = f"M{cx},{cy - ring_r - lead_out}"
    if j:
        d += fillet(coil[0], coil[:j + 1], +1)
    else:
        d += f"V{coil[0][1]:.2f}"
    d += path_d(body)[path_d(body).index("C"):]   # body's curves, minus its own moveto
    if j:
        d += fillet(coil[-1], coil[-1:-j - 2:-1], -1, reverse=True)
    d += f"V{cy + ring_r + lead_out}"
    parts = [d]
    circle = (f"M{cx - ring_r},{cy}a{ring_r},{ring_r} 0 1,0 {2 * ring_r},0"
              f"a{ring_r},{ring_r} 0 1,0 {-2 * ring_r},0Z") if ring else ""
    return {"d": "".join(parts), "ring": circle, "stroke": stroke}

def svg(m, color="#fff", bg=None, size=None, view=(0, 0, 100, 100), corner=0.19):
    vb = " ".join(str(v) for v in view)
    dim = f' width="{size}" height="{size}"' if size else ""
    back = ""
    if bg == "sky":
        back = ('<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
                '<stop offset="0" stop-color="#1d325f"/><stop offset="1" stop-color="#2b5488"/>'
                f'</linearGradient></defs><rect x="{view[0]}" y="{view[1]}" width="{view[2]}" '
                f'height="{view[3]}" rx="{view[2] * corner:.1f}" fill="url(#sky)"/>')
    g = (f'<g fill="none" stroke="{color}" stroke-width="{m["stroke"]}" '
         f'stroke-linecap="round" stroke-linejoin="round">'
         f'<path d="{m["ring"]}"/><path d="{m["d"]}"/></g>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}"{dim}>{back}{g}</svg>'

METALS = {
    # brushed finish: a narrow tonal drift (start, middle, end), a rim for dark grounds, and
    # optional grain strength / shade (how far the streaks are pulled toward dark)
    "silver": {"tones": ("#b8bcc2", "#cfd2d7", "#afb3ba"), "rim": "#373a40",
               "grain": 0.6, "shade": 0.06},   # light surface: stronger, slightly darker streaks
    "nickel": {"tones": ("#9c988f", "#b0aca3", "#959189"), "rim": "#3a3935"},
}

def svg_metal(m, metal="silver", outline=None, hairline=0.4, grain=None, bg=None):
    """Large-format mark in brushed metal, the same overall width as the flat mark: a
    hairline outline (default: the metal's own dark rim) around a stroke narrowed by
    2 * hairline, which is filled with a flat metal tone and fine vertical
    grain (fractal noise stretched along y, soft-light blended at `grain` strength), masked to
    the mark. Two passes over the same geometry, so crossings merge without seams."""
    t = METALS[metal]
    outline = outline or t["rim"]
    grain = t.get("grain", 0.45) if grain is None else grain
    shade = t.get("shade", 0)
    inner = m["stroke"] - 2 * hairline   # outline's outer edge matches the flat mark
    stops = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in zip((0, 0.5, 1), t["tones"]))
    paths = f'<path d="{m["ring"]}"/><path d="{m["d"]}"/>'
    common = 'fill="none" stroke-linecap="round" stroke-linejoin="round"'
    defs = (f'<linearGradient id="tone" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="100" y2="100">{stops}</linearGradient>'
            f'<filter id="brush" x="0" y="0" width="100" height="100" filterUnits="userSpaceOnUse">'
            f'<feTurbulence type="fractalNoise" baseFrequency="4.8 0.015" numOctaves="1" seed="7" result="n"/>'
            f'<feColorMatrix in="n" type="saturate" values="0" result="gray"/>'
            f'<feComponentTransfer in="gray" result="soft">'
            f'<feFuncR type="linear" slope="1" intercept="{-shade}"/><feFuncG type="linear" slope="1" intercept="{-shade}"/>'
            f'<feFuncB type="linear" slope="1" intercept="{-shade}"/>'
            f'<feFuncA type="linear" slope="0" intercept="{grain}"/></feComponentTransfer>'
            f'<feBlend in="soft" in2="SourceGraphic" mode="soft-light" result="b"/>'
            f'<feComposite in="b" in2="SourceGraphic" operator="in"/></filter>'
            f'<mask id="wire" maskUnits="userSpaceOnUse" x="0" y="0" width="100" height="100">'
            f'<g {common} stroke="#fff" stroke-width="{inner}">{paths}</g></mask>')
    back = f'<rect width="100" height="100" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs>{defs}</defs>{back}'
            f'<g {common} stroke="{outline}" stroke-width="{m["stroke"]}">{paths}</g>'
            f'<rect width="100" height="100" fill="url(#tone)" filter="url(#brush)" mask="url(#wire)"/></svg>')

def svg_graphite(m):
    """The flat black mark with the brushed silver mark (black hairline) laid over it at
    50% opacity: a dark brushed graphite. For light grounds."""
    metal = svg_metal(m, "silver", outline="#1a1a1a")
    head, body = metal.split("</defs>", 1)
    body = body.removesuffix("</svg>")
    black = (f'<g fill="none" stroke="#000" stroke-width="{m["stroke"]}" stroke-linecap="round" '
             f'stroke-linejoin="round"><path d="{m["ring"]}"/><path d="{m["d"]}"/></g>')
    return f'{head}</defs>{black}<g opacity="0.5">{body}</g></svg>'

VARIANTS = {
    # name: (renderer, kwargs) -- large-format set, all at stroke 3
    "mark":              ("flat",  {"color": "#000"}),
    "mark-white":        ("flat",  {"color": "#fff"}),
    "mark-silver":       ("metal", {"metal": "silver", "outline": "#1a1a1a"}),
    "mark-silver-dark":  ("metal", {"metal": "silver"}),
    "mark-graphite":     ("graphite", {}),
    "mark-nickel":       ("metal", {"metal": "nickel", "outline": "#1a1a1a"}),
    "mark-nickel-dark":  ("metal", {"metal": "nickel"}),
}

if __name__ == "__main__":
    import sys, os
    out = sys.argv[1] if len(sys.argv) > 1 else "logo"
    os.makedirs(out, exist_ok=True)
    m = mark(stroke=3.0)
    for name, (kind, kw) in VARIANTS.items():
        render = {"flat": svg, "metal": svg_metal, "graphite": svg_graphite}[kind]
        open(f"{out}/{name}.svg", "w").write(render(m, **kw))
    try:  # 2048px transparent PNGs, if a headless Chrome is around (see favicons.py)
        import favicons, tempfile
        with tempfile.TemporaryDirectory() as tmp:
            for name in VARIANTS:
                open(f"{out}/{name}.png", "wb").write(
                    favicons.png(open(f"{out}/{name}.svg").read(), 2048, tmp))
    except SystemExit:
        print("no headless Chrome: wrote SVGs only")
    print("wrote", out, sorted(os.listdir(out)))
