"""Gera marketing/treino-animado.svg e embute no index.html.
Uso: python3 marketing/gerar-animacao.py  (a partir da raiz do repositório)"""
import re, pathlib

REP = 2.4                 # segundos por repetição
SCENE = REP * 2           # 2 repetições por exercício (1 fala por repetição)
SPL = 'calcMode="spline" keyTimes="0;.5;1" keySplines=".45 0 .55 1;.45 0 .55 1"'
PELE, TOP, LEG, TENIS = "#c68b63", "#f97316", "#27272a", "#f4f4f5"
HEAD0 = (252, 106)

def anim(attr, a, b):
    if a == b: return ""
    return f'<animate attributeName="{attr}" values="{a};{b};{a}" {SPL} dur="{REP}s" repeatCount="indefinite"/>'

def line(color, w, p1, p2, q1=None, q2=None):
    q1, q2 = q1 or p1, q2 or p2
    inner = "".join([anim("x1", p1[0], q1[0]), anim("y1", p1[1], q1[1]), anim("x2", p2[0], q2[0]), anim("y2", p2[1], q2[1])])
    return f'<line x1="{p1[0]}" y1="{p1[1]}" x2="{p2[0]}" y2="{p2[1]}" stroke="{color}" stroke-width="{w}">{inner}</line>'

def poly(color, w, up, down=None):
    down = down or up
    s = lambda pts: " ".join(f"{x},{y}" for x, y in pts)
    a = "" if up == down else f'<animate attributeName="points" values="{s(up)};{s(down)};{s(up)}" {SPL} dur="{REP}s" repeatCount="indefinite"/>'
    return f'<polyline points="{s(up)}" stroke="{color}" stroke-width="{w}" stroke-linejoin="round">{a}</polyline>'

def moving(inner, up, down, base=(0, 0), rot=0):
    du = (up[0] - base[0], up[1] - base[1]); dd = (down[0] - base[0], down[1] - base[1])
    a = "" if up == down else f'<animateTransform attributeName="transform" type="translate" values="{du[0]} {du[1]};{dd[0]} {dd[1]};{du[0]} {du[1]}" {SPL} dur="{REP}s" repeatCount="indefinite"/>'
    return f'<g transform="translate({du[0]} {du[1]})">{a}<g transform="translate({base[0]} {base[1]}) rotate({rot})">{inner}</g></g>'

def halter(up, down=None, rot=0):
    return moving('<use href="#ta-halter"/>', up, down or up, rot=rot)

def cabeca(up, down=None):
    down = down or up
    h = ('<path d="M236 98 C220 104 218 124 226 136 C228 122 232 112 240 106 Z" fill="#2a1a12"/>'
         f'<circle cx="252" cy="106" r="20" fill="{PELE}"/>'
         '<path d="M232 104 C232 88 244 82 254 84 C266 86 273 96 272 106 C262 98 246 96 232 104 Z" fill="#2a1a12"/>'
         '<circle cx="262" cy="108" r="2.4" fill="#18100b"/>'
         '<path d="M258 116 C262 119 266 118 268 115" stroke="#7a3a2c" stroke-width="2" fill="none" stroke-linecap="round"/>')
    du = (up[0]-HEAD0[0], up[1]-HEAD0[1]); dd = (down[0]-HEAD0[0], down[1]-HEAD0[1])
    a = "" if up == down else f'<animateTransform attributeName="transform" type="translate" values="{du[0]} {du[1]};{dd[0]} {dd[1]};{du[0]} {du[1]}" {SPL} dur="{REP}s" repeatCount="indefinite"/>'
    return f'<g transform="translate({du[0]} {du[1]})">{a}{h}</g>'

def pe(a, b): return f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="{TENIS}" stroke-width="10"/>'

# Cada exercício: (rótulo, [fala 1, fala 2], corpo SVG). "up" = início, "down" = meio da repetição.
EXERCICIOS = [
  ("AGACHAMENTO", ["Desce mais!", "Isso! Peito aberto!"], [
      pe((250,304),(276,306)),
      line(LEG,20,(250,302),(252,255),None,(270,258)),
      line(LEG,24,(250,205),(252,255),(212,250),(270,258)),
      line(TOP,32,(250,200),(250,135),(214,245),(240,180)),
      poly(PELE,12,[(250,140),(262,168),(274,150)],[(240,185),(256,212),(266,194)]),
      halter((276,146),(268,190),rot=90),
      cabeca((252,106),(242,151)) ]),
  ("ROSCA DIRETA", ["Cotovelo parado!", "Boa! Mais 3!"], [
      pe((250,304),(276,306)),
      line(LEG,20,(250,302),(250,255)), line(LEG,24,(250,205),(250,255)),
      line(TOP,32,(250,200),(250,135)),
      poly(PELE,12,[(250,140),(254,186),(256,230)],[(250,140),(254,186),(276,148)]),
      halter((258,234),(278,152)),
      cabeca((252,106)) ]),
  ("DESENVOLVIMENTO", ["Abdômen firme!", "Sobe até o fim!"], [
      pe((250,304),(276,306)),
      line(LEG,20,(250,302),(250,255)), line(LEG,24,(250,205),(250,255)),
      line(TOP,32,(250,200),(250,135)),
      poly(PELE,12,[(250,140),(260,172),(258,128)],[(250,140),(256,100),(256,62)]),
      halter((258,122),(256,56)),
      cabeca((252,106)) ]),
  ("AFUNDO", ["Joelho alinhado!", "Desce reto!"], [
      pe((290,304),(314,306)), pe((196,298),(212,305)),
      line(LEG,20,(204,302),(232,254),None,(222,292)),
      line(LEG,22,(250,205),(232,254),(250,245),(222,292)),
      line(LEG,20,(290,302),(274,252),None,(290,250)),
      line(LEG,24,(250,205),(274,252),(250,245),(290,250)),
      line(TOP,32,(250,200),(250,135),(250,240),(250,175)),
      poly(PELE,12,[(250,140),(254,172),(256,200)],[(250,180),(254,212),(256,240)]),
      halter((256,206),(256,246)),
      cabeca((252,106),(252,146)) ]),
  ("REMADA CURVADA", ["Coluna reta!", "Puxa com as costas!"], [
      pe((250,304),(276,306)),
      line(LEG,20,(250,302),(258,258)), line(LEG,24,(232,215),(258,258)),
      line(TOP,32,(232,212),(290,176)),
      poly(PELE,12,[(288,180),(290,214),(292,246)],[(288,180),(268,192),(282,218)]),
      halter((292,252),(282,224)),
      cabeca((312,160)) ]),
  ("FLEXÃO", ["Corpo em linha!", "Peito perto do chão!"], [
      pe((166,298),(170,306)),
      line(LEG,22,(172,300),(246,266),None,(246,290)),
      line(TOP,30,(246,266),(318,242),(246,290),(322,282)),
      poly(PELE,12,[(318,244),(326,274),(332,303)],[(322,282),(302,290),(332,303)]),
      cabeca((342,226),(350,266)) ]),
]

N = len(EXERCICIOS); TOTAL = SCENE * N

def cena(i, rotulo, falas, corpo):
    if N == 1: vis = ""
    else:
        kt = [0]; vals = ["1" if i == 0 else "0"]
        if i > 0: kt.append(i / N); vals.append("1")
        if i < N - 1: kt.append((i + 1) / N); vals.append("0")
        vis = f'<animate attributeName="opacity" calcMode="discrete" values="{";".join(vals)}" keyTimes="{";".join(f"{k:.4f}" for k in kt)}" dur="{TOTAL}s" repeatCount="indefinite"/>'
    f1, f2 = falas
    return f'''
  <g opacity="{1 if i == 0 else 0}">{vis}
    <g stroke-linecap="round" fill="none">{"".join(corpo)}</g>
    <rect x="40" y="266" width="{max(150, 14 + 10.5*len(rotulo))}" height="28" rx="14" fill="{TOP}"/>
    <text x="{40 + max(150, 14 + 10.5*len(rotulo))/2}" y="285" text-anchor="middle" font-family="Montserrat, Arial, sans-serif" font-weight="900" font-style="italic" font-size="13" fill="#fff">{rotulo}</text>
    <text x="430" y="44" text-anchor="middle" font-family="Montserrat, Arial, sans-serif" font-weight="800" font-size="15" fill="#18181b">{f1}<animate attributeName="opacity" calcMode="discrete" values="1;0" keyTimes="0;.5" dur="{SCENE}s" repeatCount="indefinite"/></text>
    <text x="430" y="44" text-anchor="middle" font-family="Montserrat, Arial, sans-serif" font-weight="800" font-size="15" fill="#18181b" opacity="0">{f2}<animate attributeName="opacity" calcMode="discrete" values="0;1" keyTimes="0;.5" dur="{SCENE}s" repeatCount="indefinite"/></text>
    <g font-family="Montserrat, Arial, sans-serif" font-weight="700" font-size="10" fill="#71717a">
      <text x="40" y="330">{i+1}/{N}</text>
    </g>
  </g>'''

HEADER = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 360" class="w-full h-auto" role="img" aria-label="Animação: Felipe acompanhando uma aluna em agachamento, rosca direta, desenvolvimento, afundo, remada curvada e flexão">
  <defs>
    <linearGradient id="ta-bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1c1c20"/><stop offset="1" stop-color="#0b0b0d"/></linearGradient>
    <radialGradient id="ta-glow" cx=".5" cy=".55" r=".6"><stop offset="0" stop-color="#f97316" stop-opacity=".28"/><stop offset="1" stop-color="#f97316" stop-opacity="0"/></radialGradient>
    <clipPath id="ta-cab"><circle cx="470" cy="98" r="36"/></clipPath>
    <g id="ta-halter">
      <rect x="-14" y="-3" width="28" height="6" rx="3" fill="#a1a1aa"/>
      <rect x="-20" y="-10" width="9" height="20" rx="3" fill="#3f3f46"/>
      <rect x="11" y="-10" width="9" height="20" rx="3" fill="#3f3f46"/>
    </g>
  </defs>
  <rect width="640" height="360" rx="28" fill="url(#ta-bg)"/>
  <rect width="640" height="360" rx="28" fill="url(#ta-glow)"/>
  <rect x="40" y="40" width="300" height="200" rx="10" fill="#ffffff" opacity=".03"/>
  <line x1="70" y1="40" x2="40" y2="110" stroke="#fff" stroke-opacity=".05" stroke-width="10"/>
  <line x1="130" y1="40" x2="70" y2="180" stroke="#fff" stroke-opacity=".04" stroke-width="6"/>
  <rect x="0" y="306" width="640" height="54" fill="#09090b"/>
  <line x1="0" y1="306" x2="640" y2="306" stroke="#27272a" stroke-width="3"/>
  <ellipse cx="252" cy="309" rx="70" ry="6" fill="#000" opacity=".5"/>
  <ellipse cx="470" cy="309" rx="44" ry="6" fill="#000" opacity=".5"/>
  <rect x="336" y="18" width="188" height="40" rx="20" fill="#fafafa"/>
  <path d="M440 56 L456 74 L462 56 Z" fill="#fafafa"/>'''

PERSONAL = '''
  <g stroke-linecap="round" fill="none">
    <line x1="462" y1="215" x2="456" y2="302" stroke="#18181b" stroke-width="20"/>
    <line x1="478" y1="215" x2="486" y2="302" stroke="#18181b" stroke-width="20"/>
    <line x1="446" y1="305" x2="460" y2="305" stroke="#f4f4f5" stroke-width="10"/>
    <line x1="484" y1="305" x2="500" y2="305" stroke="#f4f4f5" stroke-width="10"/>
    <line x1="470" y1="212" x2="470" y2="146" stroke="#0c0c0e" stroke-width="40"/>
    <polyline points="486,150 500,192 510,168" stroke="#9b6342" stroke-width="12" stroke-linejoin="round"/>
    <polyline points="454,150 432,178 410,166" stroke="#9b6342" stroke-width="12" stroke-linejoin="round">
      <animate attributeName="points" values="454,150 432,178 410,166;454,150 430,174 406,156;454,150 432,178 410,166" dur="1.2s" repeatCount="indefinite"/>
    </polyline>
  </g>
  <text x="470" y="186" text-anchor="middle" font-family="Montserrat, Arial, sans-serif" font-weight="800" font-size="8" fill="#e4e4e7" letter-spacing=".5">PERSONAL</text>
  <rect x="504" y="150" width="14" height="24" rx="3" fill="#27272a" stroke="#52525b" stroke-width="1.5"/>
  <rect x="506.5" y="153" width="9" height="16" rx="1.5" fill="#22c55e"><animate attributeName="opacity" values=".4;1;.4" dur="2s" repeatCount="indefinite"/></rect>
  <g>
    <animateTransform attributeName="transform" type="rotate" values="-3 470 120;3 470 120;-3 470 120" dur="2.4s" repeatCount="indefinite"/>
    <image href="/avatar.svg" x="434" y="62" width="72" height="72" clip-path="url(#ta-cab)"/>
    <circle cx="470" cy="98" r="36" fill="none" stroke="#f97316" stroke-width="2"/>
  </g>
  <g>
    <animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;.15;.2;.42;.47;1" dur="7.2s" repeatCount="indefinite"/>
    <animateTransform attributeName="transform" type="translate" values="0 10;0 10;0 0;0 0;0 -6;0 -6" keyTimes="0;.15;.2;.42;.47;1" dur="7.2s" repeatCount="indefinite"/>
    <rect x="452" y="226" width="168" height="40" rx="12" fill="#18181b" stroke="#22c55e" stroke-opacity=".6"/>
    <circle cx="472" cy="246" r="10" fill="#22c55e"/>
    <path d="M467 246 L471 250 L478 242" stroke="#0b0b0d" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
    <text x="488" y="243" font-family="Montserrat, Arial, sans-serif" font-weight="800" font-size="10.5" fill="#fff">Check-in recebido</text>
    <text x="488" y="257" font-family="Montserrat, Arial, sans-serif" font-weight="600" font-size="9" fill="#a1a1aa">Treino de hoje feito</text>
  </g>
</svg>'''

svg = HEADER + "".join(cena(i, *e) for i, e in enumerate(EXERCICIOS)) + PERSONAL
root = pathlib.Path(__file__).resolve().parent.parent
(root / "marketing/treino-animado.svg").write_text(svg + "\n", encoding="utf-8")
idx = root / "index.html"; html = idx.read_text(encoding="utf-8")
html, n = re.subn(r'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 360".*?</svg>', lambda m: svg, html, count=1, flags=re.S)
assert n == 1, "animação não encontrada no index.html"
idx.write_text(html, encoding="utf-8")
print(f"{N} exercícios, ciclo de {TOTAL:.1f}s")
