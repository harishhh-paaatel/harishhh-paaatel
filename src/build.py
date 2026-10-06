"""Build the five self-contained animated SVGs for the GitHub profile README.

Run:  python3 src/build.py      (from the repository root)
Everything is inlined (fonts, portrait, icons); the SVGs make no network requests.
Motion is CSS-only so prefers-reduced-motion can switch it off; every element's
base attributes are its readable final state, so renderers without animation
still show a complete picture.
"""
import base64, hashlib, json, math, os
from html import escape as _esc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
OUT = os.path.join(ROOT, "assets")
os.makedirs(OUT, exist_ok=True)


def b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def esc(s):
    return _esc(s, quote=True)


OUTFIT = b64(os.path.join(SRC, "outfit-latin.woff2"))
MONO = b64(os.path.join(SRC, "jetbrains-mono-latin.woff2"))
PORTRAIT = "data:image/png;base64," + b64(os.path.join(SRC, "id.png"))
PORTRAIT_W, PORTRAIT_H = 560, 477
ICONS = json.load(open(os.path.join(SRC, "icons.json")))

NAVY, PANEL, PANEL2, LINE = "#070b16", "#0d1428", "#121b36", "#1f2a4a"
BLUE, RED, INK, MUTED, SOFT = "#247bff", "#ff354f", "#eef2fb", "#8d99b8", "#c3cce2"
MW = 0.6  # JetBrains Mono advance width per em


def mono_w(text, size):
    return len(text) * size * MW


BASE_CSS = (
    "@font-face{font-family:'HPDisplay';src:url(data:font/woff2;base64,%s) format('woff2');"
    "font-weight:100 900;font-style:normal;font-display:block}"
    "@font-face{font-family:'HPMono';src:url(data:font/woff2;base64,%s) format('woff2');"
    "font-weight:100 800;font-style:normal;font-display:block}"
    ".d{font-family:'HPDisplay','Outfit',system-ui,-apple-system,'Segoe UI',sans-serif}"
    ".m{font-family:'HPMono','JetBrains Mono',ui-monospace,Menlo,Consolas,monospace}"
    "text{text-rendering:geometricPrecision}"
    "@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important}}"
) % (OUTFIT, MONO)


def svg(p, w, h, title, desc, css, defs, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-labelledby="{p}-title {p}-desc">\n'
        f'<title id="{p}-title">{esc(title)}</title>\n<desc id="{p}-desc">{esc(desc)}</desc>\n'
        f"<style>{BASE_CSS}{css}</style>\n<defs>{defs}</defs>\n{body}\n</svg>\n"
    )


def frame(p, w, h):
    defs = (
        f'<pattern id="{p}-dots" width="22" height="22" patternUnits="userSpaceOnUse">'
        f'<circle cx="2" cy="2" r="1.1" fill="#ffffff" opacity=".075"/></pattern>'
        f'<linearGradient id="{p}-edge" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{BLUE}"/><stop offset=".5" stop-color="#2b3760" stop-opacity=".55"/>'
        f'<stop offset="1" stop-color="{RED}"/></linearGradient>'
        f'<radialGradient id="{p}-gb" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{BLUE}" stop-opacity=".22"/>'
        f'<stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="{p}-gr" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{RED}" stop-opacity=".16"/>'
        f'<stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient>'
        f'<clipPath id="{p}-frame"><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="26"/></clipPath>'
    )
    body = (
        f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="26" fill="{NAVY}"/>'
        f'<g clip-path="url(#{p}-frame)">'
        f'<rect width="{w}" height="{h}" fill="url(#{p}-dots)"/>'
        f'<circle cx="{w*0.12:.0f}" cy="{h*0.05:.0f}" r="{h*0.75:.0f}" fill="url(#{p}-gb)"/>'
        f'<circle cx="{w*0.92:.0f}" cy="{h*0.98:.0f}" r="{h*0.7:.0f}" fill="url(#{p}-gr)"/>'
        f"</g>"
        f'<rect x=".75" y=".75" width="{w-1.5}" height="{h-1.5}" rx="26.25" fill="none" '
        f'stroke="url(#{p}-edge)" stroke-width="1.5"/>'
    )
    return defs, body


def hairline_card(p, cid, x, y, w, h, rx=18, fill=PANEL):
    """Rounded card with a gradient hairline border."""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" fill-opacity=".92"/>'
        f'<rect x="{x+.5}" y="{y+.5}" width="{w-1}" height="{h-1}" rx="{rx-.5}" fill="none" '
        f'stroke="url(#{p}-hl)" stroke-width="1"/>'
    )


def hairline_grad(p):
    return (
        f'<linearGradient id="{p}-hl" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{BLUE}" stop-opacity=".75"/>'
        f'<stop offset=".45" stop-color="#2a3558" stop-opacity=".9"/>'
        f'<stop offset="1" stop-color="{RED}" stop-opacity=".7"/></linearGradient>'
    )


def icon(name, cx, cy, size, color=None):
    ic = ICONS[name]
    s = size / 24
    return (
        f'<path transform="translate({cx - size/2:.2f} {cy - size/2:.2f}) scale({s:.4f})" '
        f'd="{ic["path"]}" fill="{color or "#" + ic["hex"]}"/>'
    )


def rim_filters(p, scale=1.0):
    out = ""
    for key, color, dx in (("rb", BLUE, -7), ("rr", RED, 7)):
        out += (
            f'<filter id="{p}-{key}" x="-20%" y="-20%" width="140%" height="140%" color-interpolation-filters="sRGB">'
            f'<feFlood flood-color="{color}"/><feComposite in2="SourceAlpha" operator="in"/>'
            f'<feGaussianBlur stdDeviation="{4.5/scale:.2f}"/><feOffset dx="{dx/scale:.2f}" dy="{-3/scale:.2f}"/></filter>'
        )
    return out


def portrait_defs(p, w):
    """Embed the photo once; rim-light filters are sized for display width w."""
    return (f'<image id="{p}-img" href="{PORTRAIT}" width="{PORTRAIT_W}" height="{PORTRAIT_H}"/>'
            + rim_filters(p, w / PORTRAIT_W))


def portrait(p, x, y, w):
    """Photo with blue/crimson rim light; (x, y) is the image's top-left, w its display width."""
    s = w / PORTRAIT_W
    return (
        f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.5f})">'
        f'<use href="#{p}-img" filter="url(#{p}-rb)" opacity=".95"/>'
        f'<use href="#{p}-img" filter="url(#{p}-rr)" opacity=".85"/>'
        f'<use href="#{p}-img"/></g>'
    )


def chevron(x, y, s=1.0, color=BLUE, sw=2.4):
    return (
        f'<path d="M{x} {y - 6*s} L{x + 6*s} {y} L{x} {y + 6*s}" fill="none" stroke="{color}" '
        f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>'
    )


def ext_arrow(x, y, color=MUTED):
    return (
        f'<path d="M{x} {y+10} L{x+10} {y} M{x+3} {y} H{x+10} V{y+7}" fill="none" stroke="{color}" '
        f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
    )


ENTER = (
    "@keyframes {p}-up{{from{{opacity:0;transform:translateY(18px)}}to{{opacity:1;transform:none}}}}"
    "@keyframes {p}-left{{from{{opacity:0;transform:translateX(-22px)}}to{{opacity:1;transform:none}}}}"
    "@keyframes {p}-fade{{from{{opacity:0}}to{{opacity:1}}}}"
    ".{p}-up{{animation:{p}-up .8s cubic-bezier(.2,.8,.2,1) both}}"
    ".{p}-left{{animation:{p}-left .8s cubic-bezier(.2,.8,.2,1) both}}"
    ".{p}-fade{{animation:{p}-fade .9s ease-out both}}"
)


def delay(t):
    return f' style="animation-delay:{t:.2f}s"'


def neural_net(p):
    """Animated network inside the hero panel: signals hop layer to layer."""
    xs, sizes, cyc, gap = [700, 768, 836, 904], [3, 5, 5, 2], 246, 44
    nodes = [[(x, cyc + (j - (n - 1) / 2) * gap) for j in range(n)] for x, n in zip(xs, sizes)]
    out = (f'<text class="m" x="674" y="114" font-size="11" fill="{MUTED}">model.forward()</text>'
           f'<circle class="{p}-pulse" cx="868" cy="110" r="6" fill="#2bd67b"/><circle cx="868" cy="110" r="3" fill="#2bd67b"/>'
           f'<text class="m" x="880" y="114" font-size="10.5" fill="#2bd67b" letter-spacing=".8">LIVE</text>')
    for L in range(3):
        for a in nodes[L]:
            for c in nodes[L + 1]:
                out += f'<path d="M{a[0]} {a[1]:.1f} L{c[0]} {c[1]:.1f}" stroke="{SOFT}" stroke-opacity=".13" stroke-width="1"/>'
    for L in range(3):
        k = 0
        for i, a in enumerate(nodes[L]):
            for j, c in enumerate(nodes[L + 1]):
                if (i * 3 + j * 2 + L) % 3:
                    continue
                color = RED if L == 2 else BLUE
                out += (f'<path class="{p}-sig" d="M{a[0]} {a[1]:.1f} L{c[0]} {c[1]:.1f}" pathLength="100" stroke="{color}" '
                        f'stroke-width="2.4" stroke-linecap="round" stroke-dasharray="18 200" stroke-dashoffset="-100" fill="none"'
                        f'{delay(.8 + L*1.2 + (k % 3)*.08)}/>')
                k += 1
    for L, layer in enumerate(nodes):
        color = RED if L == 3 else BLUE
        for (x, y) in layer:
            out += (f'<circle cx="{x}" cy="{y:.1f}" r="8.5" fill="{PANEL2}" stroke="{color}" stroke-width="2"/>'
                    f'<circle class="{p}-node" cx="{x}" cy="{y:.1f}" r="4" fill="{color}" fill-opacity=".9"{delay(.8 + L*1.2)}/>')
    out += (f'<text class="m" x="904" y="{nodes[3][0][1] - 18:.1f}" font-size="9.5" fill="{SOFT}" text-anchor="middle">DETECT</text>'
            f'<text class="m" x="904" y="{nodes[3][1][1] + 27:.1f}" font-size="9.5" fill="{SOFT}" text-anchor="middle">ANSWER</text>'
            f'<text class="m" x="700" y="{nodes[0][0][1] - 18:.1f}" font-size="9.5" fill="{SOFT}" text-anchor="middle">INPUT</text>')
    return out


# --------------------------------------------------------------------------- hero
def build_hero():
    p, W, H = "hr", 1000, 480
    fdefs, fbody = frame(p, W, H)
    css = ENTER.format(p=p) + (
        f"@keyframes {p}-type{{from{{opacity:0}}to{{opacity:1}}}}"
        f".{p}-ch{{animation:{p}-type .01s linear both}}"
        f"@keyframes {p}-blink{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}"
        f".{p}-caret{{animation:{p}-blink 1s steps(1) infinite}}"
        f"@keyframes {p}-rise{{from{{transform:translateY(112px)}}to{{transform:none}}}}"
        f".{p}-rise{{animation:{p}-rise 1s cubic-bezier(.16,.84,.24,1) both}}"
        f"@keyframes {p}-role{{0%{{opacity:0;transform:translateY(16px)}}3.5%{{opacity:1;transform:none}}"
        f"25%{{opacity:1;transform:none}}28.5%{{opacity:0;transform:translateY(-16px)}}"
        f"100%{{opacity:0;transform:translateY(-16px)}}}}"
        f".{p}-role{{animation:{p}-role 12s cubic-bezier(.2,.8,.2,1) infinite both}}"
        f"@keyframes {p}-pulse{{0%,100%{{opacity:.15}}50%{{opacity:.6}}}}"
        f".{p}-pulse{{animation:{p}-pulse 2s ease-in-out infinite}}"
        f"@keyframes {p}-sig{{0%{{stroke-dashoffset:18}}33%,100%{{stroke-dashoffset:-100}}}}"
        f".{p}-sig{{animation:{p}-sig 3.6s linear infinite}}"
        f"@keyframes {p}-node{{0%{{fill-opacity:1}}30%,100%{{fill-opacity:.25}}}}"
        f".{p}-node{{animation:{p}-node 3.6s ease-out infinite}}"
    )
    defs = fdefs + hairline_grad(p) + (
        f'<clipPath id="{p}-n1"><rect x="40" y="126" width="600" height="104"/></clipPath>'
        f'<clipPath id="{p}-n2"><rect x="40" y="230" width="600" height="104"/></clipPath>'
        f'<clipPath id="{p}-pc"><rect x="652" y="80" width="300" height="324" rx="22"/></clipPath>'
        f'<linearGradient id="{p}-pbg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#15204a"/>'
        f'<stop offset="1" stop-color="#0a1020"/></linearGradient>'
        f'<radialGradient id="{p}-halo" cx=".5" cy=".42" r=".5"><stop offset="0" stop-color="{BLUE}" stop-opacity=".45"/>'
        f'<stop offset=".6" stop-color="{BLUE}" stop-opacity=".08"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>'
        f'<linearGradient id="{p}-sep" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{BLUE}" stop-opacity=".6"/>'
        f'<stop offset=".6" stop-color="{LINE}"/><stop offset="1" stop-color="{RED}" stop-opacity=".6"/></linearGradient>'
    )
    b = [fbody]
    # top bar
    b.append(
        f'<g class="{p}-fade"{delay(0)}>'
        f'<text class="m" x="48" y="52" font-size="13" font-weight="600" fill="{INK}" letter-spacing="1.2">K G HARISH PATEL'
        f'<tspan fill="{MUTED}" font-weight="400"> / github.com/harishhh-paaatel</tspan></text></g>'
    )
    pill_t = "OPEN TO AI/ML & SWE INTERNSHIPS"
    pw = mono_w(pill_t, 11.5) + 44
    px = 952 - pw
    b.append(
        f'<g class="{p}-fade"{delay(.2)}>'
        f'<rect x="{px:.1f}" y="33" width="{pw:.1f}" height="28" rx="14" fill="{PANEL}" stroke="{LINE}"/>'
        f'<circle class="{p}-pulse" cx="{px+18:.1f}" cy="47" r="7.5" fill="#2bd67b"/>'
        f'<circle cx="{px+18:.1f}" cy="47" r="3.6" fill="#2bd67b"/>'
        f'<text class="m" x="{px+32:.1f}" y="51.2" font-size="11.5" fill="{SOFT}" letter-spacing=".2">{esc(pill_t)}</text></g>'
    )
    # typed greeting, one character at a time
    greet = "> hello, world. I'm"
    for i, ch in enumerate(greet):
        if ch == " ":
            continue
        b.append(
            f'<text class="m {p}-ch" x="{48 + i*12}" y="108" font-size="20" fill="{BLUE}"'
            f'{delay(.25 + i*.055)}>{esc(ch)}</text>'
        )
    b.append(f'<rect class="{p}-caret" x="{48 + len(greet)*12 + 3}" y="91" width="10" height="21" fill="{RED}" opacity=".9"/>')
    # rising-mask name
    b.append(
        f'<g clip-path="url(#{p}-n1)"><text class="d {p}-rise" x="44" y="210" font-size="92" font-weight="800" '
        f'fill="{INK}" letter-spacing="-2.5"{delay(1.2)}>K G Harish</text></g>'
        f'<g clip-path="url(#{p}-n2)"><text class="d {p}-rise" x="44" y="306" font-size="92" font-weight="800" '
        f'fill="{BLUE}" letter-spacing="-2.5"{delay(1.38)}>Patel<tspan fill="{RED}">.</tspan></text></g>'
    )
    # cycling roles
    roles = ["AI/ML Engineer", "Computer Vision builder", "Generative AI · GraphRAG", "Edge AI for PCB inspection"]
    b.append(f'<g class="{p}-fade"{delay(2.0)}>' + chevron(50, 353, 1.1, RED, 2.6) + "</g>")
    for i, r in enumerate(roles):
        b.append(
            f'<g class="{p}-role" opacity="{1 if i == 0 else 0}"{delay(2.05 + 3*i)}>'
            f'<text class="m" x="70" y="360" font-size="21" font-weight="500" fill="{INK}">{esc(r)}</text></g>'
        )
    b.append(
        f'<g class="{p}-up"{delay(2.3)}><text class="d" x="48" y="398" font-size="22" fill="{SOFT}">'
        f"I turn real-world problems into ML systems.</text></g>"
    )
    # portrait panel
    b.append(
        f'<g class="{p}-up"{delay(.55)}>'
        f'<rect x="652" y="80" width="300" height="324" rx="22" fill="url(#{p}-pbg)"/>'
        f'<g clip-path="url(#{p}-pc)">'
        f'<circle cx="802" cy="210" r="190" fill="url(#{p}-halo)"/>'
        + "".join(
            f'<line x1="{652 + k*30}" y1="80" x2="{652 + k*30}" y2="404" stroke="#ffffff" stroke-opacity=".04"/>'
            for k in range(1, 10)
        )
        + neural_net(p)
        + "</g>"
        f'<rect x="652.5" y="80.5" width="299" height="323" rx="21.5" fill="none" stroke="url(#{p}-hl)"/>'
        f'<rect x="628" y="378" width="190" height="34" rx="9" fill="{RED}"/>'
        f'<text class="m" x="646" y="400" font-size="12.5" font-weight="600" fill="#ffffff" letter-spacing="1.1">CV · GENAI · EDGE AI</text>'
        f"</g>"
    )
    # info row
    b.append(f'<g class="{p}-fade"{delay(2.6)}><rect x="48" y="426" width="904" height="1" fill="url(#{p}-sep)"/></g>')
    pin = lambda x, y: (
        f'<path d="M{x} {y-7} a5 5 0 0 1 5 5 c0 4 -5 9 -5 9 s-5 -5 -5 -9 a5 5 0 0 1 5 -5z" fill="none" '
        f'stroke="{RED}" stroke-width="1.7"/><circle cx="{x}" cy="{y-2}" r="1.6" fill="{RED}"/>'
    )
    bag = lambda x, y: (
        f'<rect x="{x-7}" y="{y-5}" width="14" height="10" rx="2" fill="none" stroke="{BLUE}" stroke-width="1.7"/>'
        f'<path d="M{x-3} {y-5} v-2.5 h6 v2.5" fill="none" stroke="{BLUE}" stroke-width="1.7"/>'
    )
    cap = lambda x, y: (
        f'<path d="M{x-8} {y-3} L{x} {y-7} L{x+8} {y-3} L{x} {y+1} Z" fill="none" stroke="{INK}" stroke-width="1.6" stroke-linejoin="round"/>'
        f'<path d="M{x-4.5} {y-1} v4 c3 2 6 2 9 0 v-4" fill="none" stroke="{INK}" stroke-width="1.6"/>'
    )
    items = [(pin, "Bengaluru, India"), (bag, "Project Intern @ ProEmbSys Technologies"), (cap, "B.E. CSE '27 · MIT Mysore")]
    x = 56
    for k, (fn, t) in enumerate(items):
        b.append(
            f'<g class="{p}-up"{delay(2.65 + k*.12)}>{fn(x, 456)}'
            f'<text class="m" x="{x+16}" y="460.5" font-size="13.5" fill="{SOFT}">{esc(t)}</text></g>'
        )
        x += 16 + mono_w(t, 13.5) + 34
    desc = ("Animated intro: K G Harish Patel, AI/ML Engineer working on computer vision, generative AI and edge AI. "
            "Project Intern at ProEmbSys Technologies, Bengaluru; B.E. CSE 2027 at MIT Mysore.")
    return svg(p, W, H, "K G Harish Patel — AI/ML Engineer", desc, css, defs, "\n".join(b))


# --------------------------------------------------------------------------- about + life
def build_about():
    p, W, H = "ab", 1000, 470
    fdefs, fbody = frame(p, W, H)
    CY, CH = 140, 300  # carousel card
    cx0, cw = 560, 392
    cyc, n = 12, 3
    start = 0.6
    css = ENTER.format(p=p) + (
        f"@keyframes {p}-slide{{0%{{opacity:0;transform:translateX(26px)}}4%{{opacity:1;transform:none}}"
        f"33.3%{{opacity:1;transform:none}}37.3%{{opacity:0;transform:translateX(-26px)}}100%{{opacity:0;transform:translateX(-26px)}}}}"
        f".{p}-slide{{animation:{p}-slide {cyc}s cubic-bezier(.2,.8,.2,1) infinite both}}"
        f"@keyframes {p}-seg0{{0%{{transform:scaleX(0)}}33.33%{{transform:scaleX(1)}}99.5%{{transform:scaleX(1)}}100%{{transform:scaleX(0)}}}}"
        f"@keyframes {p}-seg1{{0%,33.33%{{transform:scaleX(0)}}66.66%{{transform:scaleX(1)}}99.5%{{transform:scaleX(1)}}100%{{transform:scaleX(0)}}}}"
        f"@keyframes {p}-seg2{{0%,66.66%{{transform:scaleX(0)}}99.5%{{transform:scaleX(1)}}100%{{transform:scaleX(0)}}}}"
        + "".join(f".{p}-s{i}{{animation:{p}-seg{i} {cyc}s linear infinite both}}" for i in range(n))
        + f"@keyframes {p}-spin{{0%,100%{{transform:scaleX(1)}}50%{{transform:scaleX(.18)}}}}"
        f".{p}-rotor{{transform-box:fill-box;transform-origin:center;animation:{p}-spin .18s linear infinite}}"
        f"@keyframes {p}-scan{{0%,100%{{opacity:.35}}50%{{opacity:1}}}}"
        f".{p}-scan{{animation:{p}-scan 1.6s ease-in-out infinite}}"
        f"@keyframes {p}-bob{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-6px)}}}}"
        f".{p}-bob{{animation:{p}-bob 2.4s ease-in-out infinite}}"
    )
    defs = fdefs + hairline_grad(p) + (
        f'<clipPath id="{p}-card"><rect x="{cx0}" y="{CY}" width="{cw}" height="{CH}" rx="20"/></clipPath>'
        f'<linearGradient id="{p}-bar" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{BLUE}"/>'
        f'<stop offset="1" stop-color="#5aa2ff"/></linearGradient>'
    )
    b = [fbody]
    b.append(
        f'<g class="{p}-fade"{delay(0)}><text class="m" x="48" y="56" font-size="13" fill="{MUTED}" letter-spacing="1.6">'
        f'02 <tspan fill="{RED}">/</tspan> ABOUT · WHAT I DO</text></g>'
        f'<g class="{p}-up"{delay(.1)}><text class="d" x="46" y="104" font-size="36" font-weight="700" fill="{INK}" '
        f'letter-spacing="-.6">Engineer by default. <tspan fill="{BLUE}">AI builder underneath.</tspan></text></g>'
    )
    caps = [
        ("Computer Vision", "YOLOv8 · MobileNet-SSD · OpenCV pipelines"),
        ("Generative AI", "LLMs · RAG · GraphRAG · knowledge graphs"),
        ("Edge AI", "TFLite · latency, FPS, SRAM & energy profiling"),
        ("Backend APIs", "FastAPI · SQLAlchemy · JWT & role-based auth"),
        ("Data & ML", "scikit-learn · Pandas · NumPy · PyTorch"),
    ]
    for i, (t, s) in enumerate(caps):
        y = 168 + i * 58
        sep = (f'<rect x="48" y="{y+34}" width="472" height="1" fill="{LINE}"/>' if i < len(caps) - 1 else "")
        b.append(
            f'<g class="{p}-left"{delay(.35 + i*.12)}>'
            f'<text class="m" x="48" y="{y}" font-size="13" font-weight="600" fill="{BLUE}">0{i+1}</text>'
            f'<text class="d" x="86" y="{y+1}" font-size="21" font-weight="600" fill="{INK}">{esc(t)}</text>'
            f'<text class="m" x="86" y="{y+22}" font-size="12.5" fill="{MUTED}">{esc(s)}</text>{sep}</g>'
        )
    # carousel card
    seg_x0, seg_w_total, gap = cx0 + 28, cw - 56, 10
    seg_w = (seg_w_total - gap * (n - 1)) / n
    card = [hairline_card(p, "c", cx0, CY, cw, CH, rx=20)]
    card.append(
        f'<text class="m" x="{cx0+28}" y="{CY+36}" font-size="12" fill="{MUTED}" letter-spacing="1.6">SELECTED WORK</text>'
        f'<text class="m" x="{cx0+cw-28}" y="{CY+36}" font-size="12" fill="{MUTED}" text-anchor="end" letter-spacing="1">1-2-3</text>'
    )
    for i in range(n):
        sx = seg_x0 + i * (seg_w + gap)
        card.append(
            f'<rect x="{sx:.1f}" y="{CY+50}" width="{seg_w:.1f}" height="4" rx="2" fill="#ffffff" fill-opacity=".12"/>'
            f'<g transform="translate({sx:.1f} {CY+50})"><rect class="{p}-s{i}" width="{seg_w:.1f}" height="4" rx="2" '
            f'fill="url(#{p}-bar)" transform="scale({1 if i == 0 else 0} 1)"{delay(start)}/></g>'
        )
    mid = cx0 + cw / 2
    iy = CY + 128  # illustration centre line
    nodes = [(-118, -26), (-62, -48), (-58, 8), (0, -18), (58, -50), (64, 14), (118, -14), (-14, 40), (100, 44)]
    edges = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (3, 5), (4, 6), (5, 6), (2, 7), (7, 5), (5, 8), (1, 4)]
    path = [(0, 2), (2, 3), (3, 5), (5, 6)]
    pt = lambda i: (mid + nodes[i][0], iy + nodes[i][1])
    ill_graph = "".join(
        f'<line x1="{pt(a)[0]}" y1="{pt(a)[1]}" x2="{pt(c)[0]}" y2="{pt(c)[1]}" stroke="{SOFT}" stroke-opacity=".28" stroke-width="1.5"/>'
        for a, c in edges)
    ill_graph += f'<g class="{p}-scan">' + "".join(
        f'<line x1="{pt(a)[0]}" y1="{pt(a)[1]}" x2="{pt(c)[0]}" y2="{pt(c)[1]}" stroke="{RED}" stroke-width="2.5" stroke-linecap="round"/>'
        for a, c in path) + "</g>"
    on_path = {i for e in path for i in e}
    for i in range(len(nodes)):
        x, y = pt(i)
        hot = i in on_path
        ill_graph += (f'<circle cx="{x}" cy="{y}" r="{11 if i == 3 else 8}" fill="{PANEL2}" stroke="{RED if hot else BLUE}" stroke-width="2"/>'
                      f'<circle cx="{x}" cy="{y}" r="{4 if i == 3 else 3}" fill="{RED if hot else BLUE}"/>')
    ill_graph += (f'<rect x="{mid-140}" y="{iy-64}" width="44" height="18" rx="9" fill="{RED}"/>'
                  f'<text class="m" x="{mid-118}" y="{iy-51}" font-size="9.5" font-weight="700" fill="#ffffff" text-anchor="middle">QUERY</text>'
                  f'<rect x="{mid+96}" y="{iy-54}" width="44" height="18" rx="9" fill="{BLUE}"/>'
                  f'<text class="m" x="{mid+118}" y="{iy-41}" font-size="9.5" font-weight="700" fill="#ffffff" text-anchor="middle">LLM</text>')
    arms = [(-62, -22), (62, -22), (-62, 22), (62, 22)]
    ill_drone = f'<g class="{p}-bob">'
    for ax, ay in arms:
        ill_drone += f'<line x1="{mid}" y1="{iy}" x2="{mid+ax}" y2="{iy+ay}" stroke="{SOFT}" stroke-width="5" stroke-linecap="round"/>'
    for ax, ay in arms:
        ill_drone += (
            f'<line x1="{mid+ax}" y1="{iy+ay}" x2="{mid+ax}" y2="{iy+ay-12}" stroke="{SOFT}" stroke-width="3"/>'
            f'<ellipse class="{p}-rotor" cx="{mid+ax}" cy="{iy+ay-13}" rx="30" ry="3.5" fill="{BLUE}" fill-opacity=".85"/>'
        )
    ill_drone += (
        f'<rect x="{mid-26}" y="{iy-14}" width="52" height="28" rx="10" fill="{PANEL2}" stroke="{SOFT}" stroke-width="2"/>'
        f'<circle cx="{mid}" cy="{iy+6}" r="6" fill="{RED}"/><circle cx="{mid}" cy="{iy+6}" r="2.4" fill="#ffffff"/></g>'
        f'<path d="M{mid-130} {iy+56} Q {mid} {iy+20} {mid+130} {iy+56}" fill="none" stroke="{BLUE}" stroke-opacity=".5" '
        f'stroke-width="1.5" stroke-dasharray="3 6"/>'
    )
    ill_pcb = (
        f'<rect x="{mid-110}" y="{iy-50}" width="220" height="104" rx="10" fill="#0e3b2c" stroke="#1d6b4f"/>'
        + "".join(
            f'<path d="M{mid-110} {iy-30 + k*18} H{mid-60 + (k%2)*12} V{iy-20 + k*16} H{mid-34}" fill="none" '
            f'stroke="#c9a54a" stroke-opacity=".7" stroke-width="2"/>' for k in range(4))
        + f'<rect x="{mid-34}" y="{iy-30}" width="68" height="64" rx="6" fill="#111827" stroke="#3b4660"/>'
        + "".join(f'<rect x="{mid-28 + k*12}" y="{iy-36}" width="5" height="6" fill="#c9a54a"/>'
                  f'<rect x="{mid-28 + k*12}" y="{iy+34}" width="5" height="6" fill="#c9a54a"/>' for k in range(5))
        + f'<text class="m" x="{mid}" y="{iy+6}" font-size="11" fill="{MUTED}" text-anchor="middle">MCU</text>'
        + "".join(
            f'<path d="M{mid+40} {iy-22 + k*14} H{mid+110}" stroke="#c9a54a" stroke-opacity=".7" stroke-width="2"/>' for k in range(4))
        + f'<g class="{p}-scan"><rect x="{mid+52}" y="{iy-30}" width="46" height="34" rx="3" fill="none" stroke="{RED}" '
        f'stroke-width="2" stroke-dasharray="5 3"/><rect x="{mid+52}" y="{iy-46}" width="46" height="15" rx="3" fill="{RED}"/>'
        f'<text class="m" x="{mid+75}" y="{iy-35}" font-size="9.5" font-weight="700" fill="#ffffff" text-anchor="middle">SHORT</text></g>'
    )
    slides = [
        ("GENAI · GRAPHRAG", "Knowledge graphs + LLMs", ["Extracts entities into a NetworkX graph,", "benchmarked against chunk-based RAG."], ill_graph),
        ("DRONES · INNOVOTSAVA 2026", "2nd Prize, Drone Fair", ["Drone navigation in AirSim + Unreal,", "RGB + pose capture, 3D reconstruction."], ill_drone),
        ("HARDWARE × AI", "AI on the factory floor", ["Spotting PCB defects with YOLOv8 and", "MobileNet-SSD, tuned for edge hardware."], ill_pcb),
    ]
    for i, (tag, title, lines, ill) in enumerate(slides):
        tw = mono_w(tag, 10.5) + 24
        g = (
            f'<g class="{p}-slide" opacity="{1 if i == 0 else 0}"{delay(start + 4*i)}>{ill}'
            f'<rect x="{cx0+28}" y="{CY+196}" width="{tw:.1f}" height="22" rx="11" fill="{BLUE}" fill-opacity=".14" stroke="{BLUE}" stroke-opacity=".5"/>'
            f'<text class="m" x="{cx0+40}" y="{CY+211}" font-size="10.5" fill="#8fbaff" letter-spacing=".6">{esc(tag)}</text>'
            f'<text class="d" x="{cx0+28}" y="{CY+248}" font-size="25" font-weight="700" fill="{INK}">{esc(title)}</text>'
            + "".join(
                f'<text class="d" x="{cx0+28}" y="{CY+272 + k*20}" font-size="15.5" fill="{SOFT}">{esc(l)}</text>'
                for k, l in enumerate(lines))
            + "</g>"
        )
        card.append(g)
    b.append(f'<g class="{p}-up"{delay(.5)}>' + card[0] + f'<g clip-path="url(#{p}-card)">' + "".join(card[1:]) + "</g></g>")
    desc = ("Capabilities: computer vision, generative AI, edge AI, backend APIs, data and ML. Selected work: "
            "a GraphRAG knowledge system, drone navigation and 3D reconstruction (2nd prize, Innovotsava 2026 Drone Fair), "
            "PCB defect detection on edge hardware.")
    return svg(p, W, H, "About K G Harish Patel", desc, css, defs, "\n".join(b))


# --------------------------------------------------------------------------- stack
def build_stack():
    p, W, H = "st", 1000, 540
    fdefs, fbody = frame(p, W, H)
    cx, cy, tilt, k = 286, 334, -12, 0.56
    orbits = [
        (94, 22, 1, ["Python", "PyTorch", "OpenCV", "TensorFlow"]),
        (166, 34, -1, ["scikit-learn", "NumPy", "pandas", "Ultralytics", "Jupyter"]),
        (236, 48, 1, ["FastAPI", "Docker", "PostgreSQL", "SQLite", "Git", "Linux"]),
    ]
    labels = {"Ultralytics": "YOLOv8", "TensorFlow": "TF Lite", "pandas": "Pandas"}
    css = ENTER.format(p=p)
    for i, (_, dur, dirn, _) in enumerate(orbits):
        a = 360 * dirn
        css += (
            f"@keyframes {p}-o{i}{{from{{transform:rotate(0deg)}}to{{transform:rotate({a}deg)}}}}"
            f"@keyframes {p}-c{i}{{from{{transform:rotate(0deg)}}to{{transform:rotate({-a}deg)}}}}"
            f".{p}-o{i}{{animation:{p}-o{i} {dur}s linear infinite}}.{p}-c{i}{{animation:{p}-c{i} {dur}s linear infinite}}"
        )
    css += (
        f"@keyframes {p}-core{{0%,100%{{opacity:.55}}50%{{opacity:1}}}}.{p}-core{{animation:{p}-core 3s ease-in-out infinite}}"
    )
    defs = fdefs + hairline_grad(p) + (
        f'<radialGradient id="{p}-coreg" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{BLUE}" stop-opacity=".9"/>'
        f'<stop offset=".55" stop-color="{BLUE}" stop-opacity=".25"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>'
        f'<linearGradient id="{p}-ring" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{BLUE}" stop-opacity=".7"/>'
        f'<stop offset=".5" stop-color="#3a4770" stop-opacity=".5"/><stop offset="1" stop-color="{RED}" stop-opacity=".7"/></linearGradient>'
    )
    b = [fbody]
    b.append(
        f'<g class="{p}-fade"{delay(0)}><text class="m" x="48" y="56" font-size="13" fill="{MUTED}" letter-spacing="1.6">'
        f'03 <tspan fill="{RED}">/</tspan> STACK</text></g>'
        f'<g class="{p}-up"{delay(.1)}><text class="d" x="46" y="104" font-size="36" font-weight="700" fill="{INK}" '
        f'letter-spacing="-.6">The stack behind <tspan fill="{BLUE}">my ML systems.</tspan></text></g>'
    )
    sys = [f'<circle cx="{cx}" cy="{cy}" r="70" fill="url(#{p}-coreg)" class="{p}-core"/>']
    for r, _, _, _ in orbits:
        sys.append(
            f'<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r*k:.1f}" transform="rotate({tilt} {cx} {cy})" fill="none" '
            f'stroke="url(#{p}-ring)" stroke-width="1.2" stroke-dasharray="2 5"/>'
        )
    sys.append(
        f'<circle cx="{cx}" cy="{cy}" r="21" fill="{PANEL2}" stroke="{BLUE}" stroke-width="1.5"/>'
        f'<text class="m" x="{cx}" y="{cy+4.5}" font-size="13" font-weight="700" fill="{INK}" text-anchor="middle">AI</text>'
    )
    for i, (r, _, _, names) in enumerate(orbits):
        n = len(names)
        for j, name in enumerate(names):
            a0 = 360 * j / n + (55, 8, 40)[i]
            lab = labels.get(name, name)
            sys.append(
                f'<g transform="translate({cx} {cy}) rotate({tilt}) scale(1 {k})">'
                f'<g transform="rotate({a0:.2f})"><g class="{p}-o{i}"><g transform="translate({r} 0)">'
                f'<g class="{p}-c{i}"><g transform="rotate({-a0:.2f}) scale(1 {1/k:.5f}) rotate({-tilt})">'
                f'<circle r="19" fill="{INK}"/><circle r="19" fill="none" stroke="{BLUE}" stroke-opacity=".55" stroke-width="2"/>'
                + icon(name, 0, 0, 22)
                + f'<rect x="{-mono_w(lab, 10.5)/2 - 6:.1f}" y="24" width="{mono_w(lab, 10.5) + 12:.1f}" height="17" rx="8.5" fill="{NAVY}" fill-opacity=".85"/>'
                f'<text class="m" y="36.5" font-size="10.5" fill="{SOFT}" text-anchor="middle">{esc(lab)}</text>'
                f"</g></g></g></g></g></g>"
            )
    b.append(f'<g class="{p}-fade"{delay(.3)}>' + "".join(sys) + "</g>")
    groups = [
        ("LANGUAGES", ["Python", "JavaScript", "TypeScript", "C", "SQL"]),
        ("ML & VISION", ["PyTorch", "TensorFlow Lite", "scikit-learn", "YOLOv8", "MobileNet-SSD", "OpenCV"]),
        ("GENAI & NLP", ["LLMs", "RAG", "GraphRAG", "NetworkX", "Entity extraction"]),
        ("BACKEND & TOOLS", ["FastAPI", "SQLAlchemy", "PostgreSQL", "SQLite", "Docker", "Git", "Linux"]),
    ]
    x0, x1, y = 576, 956, 150
    fs, ch_h, gap = 12, 26, 7
    for gi, (gname, chips) in enumerate(groups):
        part = [f'<text class="m" x="{x0}" y="{y}" font-size="11.5" font-weight="600" fill="{BLUE}" letter-spacing="1.6">{esc(gname)}</text>']
        x, row_y = x0, y + 12
        for c in chips:
            w = mono_w(c, fs) + 24
            if x + w > x1:
                x, row_y = x0, row_y + ch_h + gap
            part.append(
                f'<rect x="{x:.1f}" y="{row_y}" width="{w:.1f}" height="{ch_h}" rx="9" fill="{PANEL}" stroke="url(#{p}-hl)"/>'
                f'<text class="m" x="{x+12:.1f}" y="{row_y+18.5}" font-size="{fs}" fill="{INK}">{esc(c)}</text>'
            )
            x += w + gap
        b.append(f'<g class="{p}-up"{delay(.5 + gi*.15)}>' + "".join(part) + "</g>")
        y = row_y + ch_h + 30
    print('  stack chips end at', y - 30)
    assert y - 30 < H - 24, f"stack chips overflow: {y}"
    desc = ("Tech stack. Orbiting icons: Python, PyTorch, OpenCV, TensorFlow Lite, scikit-learn, NumPy, Pandas, YOLOv8, "
            "Jupyter, FastAPI, Docker, PostgreSQL, SQLite, Git, Linux. Grouped chips list languages, ML and vision, "
            "GenAI and NLP, backend and tools.")
    return svg(p, W, H, "Tech stack", desc, css, defs, "\n".join(b))


# --------------------------------------------------------------------------- id + dashboard
def build_id():
    p, W, H = "id", 1000, 620
    fdefs, fbody = frame(p, W, H)
    PX, PY = 222, -70  # pendulum pivot (above the frame)
    CW, CHt = 272, 452  # card size
    card_top = 200  # relative to pivot
    PH = CW - 40  # square photo frame
    css = ENTER.format(p=p) + (
        f"@keyframes {p}-drop{{0%{{transform:translateY(-720px)}}58%{{transform:translateY(16px)}}"
        f"74%{{transform:translateY(-7px)}}88%{{transform:translateY(3px)}}100%{{transform:translateY(0)}}}}"
        f".{p}-drop{{animation:{p}-drop 1.15s cubic-bezier(.3,.7,.4,1) .25s both}}"
        f"@keyframes {p}-settle{{0%{{transform:rotate(6.5deg)}}22%{{transform:rotate(-4.6deg)}}44%{{transform:rotate(3.3deg)}}"
        f"64%{{transform:rotate(-2.4deg)}}82%{{transform:rotate(2deg)}}100%{{transform:rotate(1.7deg)}}}}"
        f"@keyframes {p}-sway{{0%,100%{{transform:rotate(1.7deg)}}50%{{transform:rotate(-1.7deg)}}}}"
        f".{p}-swing{{animation:{p}-settle 3.6s ease-in-out .9s both,{p}-sway 4.6s ease-in-out 4.5s infinite}}"
        f"@keyframes {p}-sweep{{0%{{transform:translateX(0)}}45%,100%{{transform:translateX(560px)}}}}"
        f".{p}-sweep{{animation:{p}-sweep 6s cubic-bezier(.45,.05,.55,.95) 2.2s infinite}}"
    )
    defs = fdefs + hairline_grad(p) + (
        f'<linearGradient id="{p}-strapA" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#16306b"/><stop offset="1" stop-color="{BLUE}"/></linearGradient>'
        f'<linearGradient id="{p}-strapB" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5a1424"/><stop offset="1" stop-color="{RED}"/></linearGradient>'
        f'<linearGradient id="{p}-metal" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f4f6fb"/>'
        f'<stop offset=".45" stop-color="#9aa4ba"/><stop offset=".7" stop-color="#e3e7f0"/><stop offset="1" stop-color="#6b7488"/></linearGradient>'
        f'<linearGradient id="{p}-band" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{BLUE}"/>'
        f'<stop offset="1" stop-color="{RED}"/></linearGradient>'
        f'<linearGradient id="{p}-foil" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffffff" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="#ffffff" stop-opacity=".22"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="{p}-ph" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#15204a"/><stop offset="1" stop-color="#0a1020"/></linearGradient>'
        f'<radialGradient id="{p}-halo" cx=".5" cy=".42" r=".5"><stop offset="0" stop-color="{RED}" stop-opacity=".35"/>'
        f'<stop offset=".6" stop-color="{BLUE}" stop-opacity=".1"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>'
        f'<clipPath id="{p}-cardc"><rect x="{-CW/2}" y="{card_top}" width="{CW}" height="{CHt}" rx="20"/></clipPath>'
        f'<clipPath id="{p}-phc"><rect x="{-CW/2+20}" y="{card_top+58}" width="{PH}" height="{PH}" rx="12"/></clipPath>'
        + portrait_defs(p, 309)
    )
    b = [fbody]
    # lanyard + card, drawn relative to the pivot
    L = []
    L.append(
        f'<path d="M-74 0 L-8 {card_top-40} L6 {card_top-40} L-58 0 Z" fill="url(#{p}-strapA)"/>'
        f'<path d="M74 0 L8 {card_top-40} L-6 {card_top-40} L58 0 Z" fill="url(#{p}-strapB)"/>'
        f'<path d="M-66 0 L0 {card_top-40}" stroke="#ffffff" stroke-opacity=".18" stroke-width="1" stroke-dasharray="6 6"/>'
        f'<path d="M66 0 L0 {card_top-40}" stroke="#ffffff" stroke-opacity=".18" stroke-width="1" stroke-dasharray="6 6"/>'
        # clasp
        f'<rect x="-15" y="{card_top-46}" width="30" height="16" rx="4" fill="url(#{p}-metal)" stroke="#5d6679" stroke-width=".8"/>'
        f'<path d="M-8 {card_top-30} v10 a8 8 0 0 0 16 0 v-10" fill="none" stroke="url(#{p}-metal)" stroke-width="4.5"/>'
        f'<circle cx="0" cy="{card_top-12}" r="6.5" fill="none" stroke="url(#{p}-metal)" stroke-width="3.5"/>'
    )
    x0 = -CW / 2
    c = [f'<rect x="{x0}" y="{card_top}" width="{CW}" height="{CHt}" rx="20" fill="{PANEL}"/>']
    c.append(f'<rect x="{x0}" y="{card_top}" width="{CW}" height="40" fill="url(#{p}-band)"/>')
    c.append(f'<rect x="-26" y="{card_top+12}" width="52" height="10" rx="5" fill="{NAVY}" fill-opacity=".85"/>')
    c.append(f'<text class="m" x="{x0+18}" y="{card_top+31}" font-size="9.5" font-weight="600" fill="#ffffff" letter-spacing="1.4">DEV ID</text>')
    c.append(f'<text class="m" x="{-x0-18}" y="{card_top+31}" font-size="9.5" font-weight="600" fill="#ffffff" text-anchor="end" letter-spacing="1.4">2026</text>')
    c.append(
        f'<rect x="{x0+20}" y="{card_top+58}" width="{PH}" height="{PH}" rx="12" fill="url(#{p}-ph)"/>'
        f'<g clip-path="url(#{p}-phc)"><circle cx="0" cy="{card_top+58+PH*.45:.0f}" r="{PH*.62:.0f}" fill="url(#{p}-halo)"/>'
        f'{portrait(p, -134, card_top + 64, 309)}</g>'
        f'<rect x="{x0+20.5}" y="{card_top+58.5}" width="{PH-1}" height="{PH-1}" rx="11.5" fill="none" stroke="url(#{p}-hl)"/>'
    )
    c.append(
        f'<text class="d" x="{x0+20}" y="{card_top+322}" font-size="24" font-weight="800" fill="{INK}" letter-spacing="-.3">K G Harish Patel</text>'
        f'<text class="m" x="{x0+20}" y="{card_top+342}" font-size="10.5" fill="{BLUE}" letter-spacing="1.1">AI/ML · CV · GENAI · EDGE AI</text>'
    )
    rows = [("ROLE", "Project Intern, ProEmbSys"), ("STUDY", "B.E. CSE '27 · MIT Mysore")]
    for i, (k_, v) in enumerate(rows):
        yy = card_top + 368 + i * 20
        c.append(
            f'<text class="m" x="{x0+20}" y="{yy}" font-size="9.5" fill="{MUTED}" letter-spacing="1">{k_}</text>'
            f'<text class="m" x="{x0+72}" y="{yy}" font-size="10.5" fill="{SOFT}">{esc(v)}</text>'
        )
    # barcode from the username hash
    hsh = hashlib.sha256(b"harishhh-paaatel").digest()
    bx, by = x0 + 20, card_top + 404
    for byte in hsh[:22]:
        for wbit in (byte & 3, (byte >> 2) & 3):
            w_ = 1 + wbit * 0.8
            if bx + w_ > x0 + 150:
                break
            c.append(f'<rect x="{bx:.1f}" y="{by}" width="{w_:.1f}" height="26" fill="{INK}"/>')
            bx += w_ + 1.6 + ((byte >> 4) & 1)
    c.append(f'<text class="m" x="{-x0-20}" y="{card_top+422}" font-size="9.5" fill="{MUTED}" text-anchor="end">@harishhh-paaatel</text>')
    # foil sweep (outer group moves, inner band is skewed)
    c.append(
        f'<g class="{p}-sweep"><rect x="{x0-190}" y="{card_top-20}" width="110" height="{CHt+40}" '
        f'fill="url(#{p}-foil)" transform="skewX(-18)"/></g>'
    )
    card = (
        f'<g clip-path="url(#{p}-cardc)">' + "".join(c) + "</g>"
        f'<rect x="{x0+.5}" y="{card_top+.5}" width="{CW-1}" height="{CHt-1}" rx="19.5" fill="none" stroke="url(#{p}-hl)"/>'
    )
    b.append(
        f'<g transform="translate({PX} {PY})"><g class="{p}-drop"><g class="{p}-swing">'
        + "".join(L) + card + "</g></g></g>"
    )
    # dashboard
    DX = 430
    b.append(
        f'<g class="{p}-fade"{delay(.2)}><text class="m" x="{DX}" y="62" font-size="13" fill="{MUTED}" letter-spacing="1.6">'
        f'04 <tspan fill="{RED}">/</tspan> BY THE NUMBERS · CHECKED 07 OCT 2026</text></g>'
        f'<g class="{p}-up"{delay(.3)}><text class="d" x="{DX-2}" y="108" font-size="36" font-weight="700" fill="{INK}" '
        f'letter-spacing="-.6">Built, shipped, <tspan fill="{BLUE}">verified.</tspan></text></g>'
    )
    metrics = [
        ("2", "INTERNSHIPS", "ProEmbSys (Sep 2026–now)", "Tech Mindsparc (Sep–Dec 2024)"),
        ("2", "CERTIFICATIONS", "JPMorgan Chase · Forage (2025)", "Intel × Digital India (2025)"),
        ("2nd", "PRIZE", "Innovotsava 2026", "Drone Fair"),
        ("4", "PCB DEFECT CLASSES", "shorts · opens", "missing solder · misalignment"),
    ]
    mw, mh, gx, gy = 252, 112, 18, 16
    for i, (num, lab, l1, l2) in enumerate(metrics):
        mx = DX + (i % 2) * (mw + gx)
        my = 136 + (i // 2) * (mh + gy)
        accent = BLUE if i % 3 == 0 else RED
        b.append(
            f'<g class="{p}-up"{delay(.5 + i*.12)}>' + hairline_card(p, "m", mx, my, mw, mh, rx=16)
            + f'<rect x="{mx+18}" y="{my+18}" width="26" height="3" rx="1.5" fill="{accent}"/>'
            f'<text class="d" x="{mx+18}" y="{my+64}" font-size="40" font-weight="800" fill="{INK}" letter-spacing="-1">{num}</text>'
            f'<text class="m" x="{mx+18 + (len(num)*24 + 12)}" y="{my+62}" font-size="10.5" font-weight="600" fill="{accent}" letter-spacing="1.2">{esc(lab)}</text>'
            f'<text class="m" x="{mx+18}" y="{my+86}" font-size="11" fill="{SOFT}">{esc(l1)}</text>'
            f'<text class="m" x="{mx+18}" y="{my+101}" font-size="11" fill="{MUTED}">{esc(l2)}</text></g>'
        )
    ry = 136 + 2 * (mh + gy) + 14
    b.append(
        f'<g class="{p}-up"{delay(1.0)}>' + hairline_card(p, "r", DX, ry, 2*mw + gx, 160, rx=16)
        + f'<text class="m" x="{DX+20}" y="{ry+30}" font-size="11.5" font-weight="600" fill="{BLUE}" letter-spacing="1.6">LATEST PUSHES</text>'
        f'<text class="m" x="{DX + 2*mw + gx - 20}" y="{ry+30}" font-size="10.5" fill="{MUTED}" text-anchor="end">public repos · GitHub</text>'
    )
    pushes = [("Portfolio_01", "HTML · CSS · JS", "03 Oct 2026"),
              ("incodevision-intern", "Python · ML", "17 Jul 2026"),
              ("dronetwin", "Python · OpenCV", "11 Jun 2026")]
    for i, (name, lang, date) in enumerate(pushes):
        yy = ry + 62 + i * 34
        b.append(
            f'<rect x="{DX+20}" y="{yy-22}" width="{2*mw + gx - 40}" height="1" fill="{LINE}"/>'
            f'<circle cx="{DX+26}" cy="{yy-5}" r="4" fill="{BLUE if i != 1 else RED}"/>'
            f'<text class="m" x="{DX+40}" y="{yy}" font-size="13" font-weight="600" fill="{INK}">{esc(name)}</text>'
            f'<text class="m" x="{DX+232}" y="{yy}" font-size="11.5" fill="{MUTED}">{esc(lang)}</text>'
            f'<text class="m" x="{DX + 2*mw + gx - 20}" y="{yy}" font-size="11.5" fill="{SOFT}" text-anchor="end">{date}</text>'
        )
    b.append("</g>")
    desc = ("Hanging developer ID card for K G Harish Patel beside verified numbers as of 7 Oct 2026: 2 internships, "
            "2 certifications, 2nd prize at the Innovotsava 2026 Drone Fair, 4 PCB defect classes, "
            "and the latest pushes to Portfolio_01, incodevision-intern and dronetwin.")
    return svg(p, W, H, "Developer ID and dashboard", desc, css, defs, "\n".join(b))


# --------------------------------------------------------------------------- connect
def globe(cx, cy):
    return (
        f'<circle cx="{cx}" cy="{cy}" r="10" fill="none" stroke="{BLUE}" stroke-width="2"/>'
        f'<ellipse cx="{cx}" cy="{cy}" rx="4.5" ry="10" fill="none" stroke="{BLUE}" stroke-width="1.8"/>'
        f'<path d="M{cx-10} {cy} H{cx+10} M{cx-8.5} {cy-5} H{cx+8.5} M{cx-8.5} {cy+5} H{cx+8.5}" stroke="{BLUE}" stroke-width="1.4"/>'
    )


LINKS = [
    ("github", "GitHub", "github.com/harishhh-paaatel", "https://github.com/harishhh-paaatel",
     lambda x, y: icon("GitHub", x, y, 24)),
    ("linkedin", "LinkedIn", "linkedin.com/in/kg-harish-patel", "https://www.linkedin.com/in/kg-harish-patel",
     lambda x, y: icon("LinkedIn", x, y, 24)),
    ("email", "Email", "kgharishpatel@gmail.com", "mailto:kgharishpatel@gmail.com",
     lambda x, y: icon("Gmail", x, y, 24)),
    ("portfolio", "Portfolio", "harishhh-paaatel.github.io/Portfolio_01", "https://harishhh-paaatel.github.io/Portfolio_01/",
     lambda x, y: globe(x, y)),
]


def build_connect():
    p, W, H = "cn", 1000, 400
    fdefs, fbody = frame(p, W, H)
    css = ENTER.format(p=p) + (
        f"@keyframes {p}-nudge{{0%,100%{{opacity:.2;transform:translateY(0)}}35%{{opacity:1;transform:translateY(7px)}}}}"
        f".{p}-nudge{{animation:{p}-nudge 1.5s ease-in-out infinite}}"
    )
    defs = fdefs + hairline_grad(p) + portrait_defs(p, 400) + (
        f'<clipPath id="{p}-pc"><rect x="40" y="40" width="300" height="320" rx="22"/></clipPath>'
        f'<linearGradient id="{p}-pbg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#15204a"/><stop offset="1" stop-color="#0a1020"/></linearGradient>'
        f'<radialGradient id="{p}-halo" cx=".5" cy=".42" r=".5"><stop offset="0" stop-color="{RED}" stop-opacity=".35"/>'
        f'<stop offset=".6" stop-color="{BLUE}" stop-opacity=".1"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>'
    )
    b = [fbody]
    b.append(
        f'<g class="{p}-up"{delay(.1)}>'
        f'<rect x="40" y="40" width="300" height="320" rx="22" fill="url(#{p}-pbg)"/>'
        f'<g clip-path="url(#{p}-pc)"><circle cx="190" cy="180" r="200" fill="url(#{p}-halo)"/>'
        + portrait(p, 10, 52, 400) + "</g>"
        f'<rect x="40.5" y="40.5" width="299" height="319" rx="21.5" fill="none" stroke="url(#{p}-hl)"/>'
        f'<rect x="56" y="310" width="158" height="32" rx="9" fill="{BLUE}"/>'
        f'<text class="m" x="72" y="331" font-size="12" font-weight="600" fill="#ffffff" letter-spacing="1.3">SAY HELLO</text>'
        f'</g>'
    )
    b.append(
        f'<g class="{p}-fade"{delay(.2)}><text class="m" x="430" y="96" font-size="13" fill="{MUTED}" letter-spacing="1.6">'
        f'05 <tspan fill="{RED}">/</tspan> CONNECT</text></g>'
        f'<g class="{p}-up"{delay(.3)}><text class="d" x="427" y="156" font-size="44" font-weight="700" fill="{INK}" letter-spacing="-.8">'
        f'Have a problem worth</text>'
        f'<text class="d" x="427" y="208" font-size="44" font-weight="700" fill="{INK}" letter-spacing="-.8">solving? '
        f'<tspan fill="{BLUE}">Let\'s talk.</tspan></text></g>'
        f'<g class="{p}-up"{delay(.5)}><text class="m" x="430" y="262" font-size="14" fill="{SOFT}">'
        f'GitHub · LinkedIn · Email · Portfolio</text>'
        f'<text class="m" x="430" y="290" font-size="13" fill="{MUTED}">Tap a card below to open it.</text></g>'
    )
    for i in range(3):
        b.append(f'<g class="{p}-fade"{delay(.8)}><g class="{p}-nudge"{delay(.6 + i*.18)}>'
                 f'<path d="M{436 + i*22} 318 l7 7 l7 -7" fill="none" stroke="{RED if i == 2 else BLUE}" stroke-width="3" '
                 f'stroke-linecap="round" stroke-linejoin="round"/></g></g>')
    desc = ("Connect with K G Harish Patel on GitHub, LinkedIn, email or his portfolio. "
            "The clickable link cards are directly below this image.")
    return svg(p, W, H, "Connect with K G Harish Patel", desc, css, defs, "\n".join(b))


def build_link(key):
    """One clickable card for the README; GitHub links the whole image."""
    _, name, handle, url, ic = next(l for l in LINKS if l[0] == key)
    p, W, H = "lk" + key[:2], 480, 112
    css = ENTER.format(p=p) + (
        f"@keyframes {p}-go{{0%,70%,100%{{transform:translate(0,0)}}80%{{transform:translate(3px,-3px)}}}}"
        f".{p}-go{{animation:{p}-go 3s ease-in-out 1s infinite}}"
    )
    defs = hairline_grad(p) + (
        f'<linearGradient id="{p}-bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0f1834"/>'
        f'<stop offset="1" stop-color="{NAVY}"/></linearGradient>'
    )
    hw = mono_w(handle, 13)
    body = (
        f'<g class="{p}-up">'
        f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="20" fill="url(#{p}-bg)"/>'
        f'<rect x="1.5" y="1.5" width="{W-3}" height="{H-3}" rx="19.5" fill="none" stroke="url(#{p}-hl)" stroke-width="1.5"/>'
        f'<circle cx="56" cy="56" r="28" fill="{INK}"/>' + ic(56, 56)
        + f'<text class="d" x="104" y="50" font-size="24" font-weight="700" fill="{INK}">{name}</text>'
        f'<text class="m" x="104" y="76" font-size="13" fill="{MUTED}">{esc(handle)}</text>'
        f'<g class="{p}-go">' + ext_arrow(W - 42, 24, SOFT) + "</g></g>"
    )
    assert 104 + hw < W - 16, (handle, hw)
    return svg(p, W, H, f"{name}: {handle}", f"Opens {url}", css, defs, body)


if __name__ == "__main__":
    for name, fn in [("hero", build_hero), ("about-life", build_about), ("stack", build_stack),
                     ("id-dashboard", build_id), ("connect", build_connect)] + [
                     ("link-" + l[0], (lambda k: lambda: build_link(k))(l[0])) for l in LINKS]:
        data = fn()
        path = os.path.join(OUT, name + ".svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(data)
        print(f"{name:14s} {len(data.encode())/1024:7.1f} KB")
