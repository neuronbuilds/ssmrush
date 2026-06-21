#!/usr/bin/env python3
"""
Genera il sito web di SSM SpecialMente (landing + Privacy + Supporto), pronto per GitHub Pages.
- Prepara le immagini (icona + screenshot) in site/img/ dai file in ../store-assets/
- Scrive index.html (landing marketing) + privacy.html + supporto.html
Fonte testi legali: ../legal/*.md   ·   Uso: python3 site/build_site.py
"""
import os, re, html, json
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
IMG  = os.path.join(SITE, "img")
EMAIL = "neuron.builds@gmail.com"
BASE  = "https://neuronbuilds.github.io/ssmrush"
F_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
F_REG  = "/System/Library/Fonts/Supplemental/Arial.ttf"
LASTMOD = "2026-06-20"
# Pre-lancio: True = pagina "presto disponibile" + noindex (il pubblico non vede il sito completo).
# Al lancio metti False e rigenera → landing completa + SEO attiva.
COMING_SOON = True

# Per-page SEO metadata (keyword-rich, unique titles + descriptions)
META = {
    "index.html": dict(
        title="SSM SpecialMente — App per il concorso SSM: quiz, simulazioni e ripasso",
        desc="App offline per la preparazione al concorso di Specializzazione in Medicina (SSM): oltre 3.000 quesiti, simulazioni d'esame, coach adattivo e ripasso distanziato. Per iPhone e Android.",
        app=True, prio="1.0"),
    "privacy.html": dict(
        title="Privacy — SSM SpecialMente",
        desc="Informativa sulla privacy dell'app SSM SpecialMente: nessun dato personale raccolto, tutto offline. Titolare: Arianna Cocchiglia (Neuron Builds).",
        app=False, prio="0.3"),
    "supporto.html": dict(
        title="Supporto e FAQ — SSM SpecialMente",
        desc="Assistenza e domande frequenti su SSM SpecialMente, l'app offline per la preparazione al concorso SSM. Contatto: neuron.builds@gmail.com.",
        app=False, prio="0.3"),
}

SHOTS = [
    ("01-home.png",      "Tutto il concorso, offline"),
    ("02-coach.png",     "Sai cosa ripassare oggi"),
    ("03-allenati.png",  "Simula l'esame vero"),
    ("04-studio.png",    "Studia per materia"),
    ("05-progressi.png", "Monitora i progressi"),
]

CSS = """
:root{--bg:#f4f6f9;--card:#fff;--ink:#1f2733;--muted:#5b6472;--accent:#e87a00;--accent2:#ffb24d;--navy:#222c3a;--deep:#151b26;--line:#e6e9ee}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased}
a{color:#b35e00;text-decoration:none}a:hover{text-decoration:underline}
.nav{position:sticky;top:0;z-index:20;background:rgba(255,255,255,.86);backdrop-filter:saturate(160%) blur(10px);border-bottom:1px solid var(--line)}
.nav .in{max-width:1040px;margin:0 auto;display:flex;align-items:center;gap:14px;padding:11px 20px}
.nav .logo{width:30px;height:30px;border-radius:8px;background:var(--navy);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:11px;letter-spacing:.5px}
.nav b{color:var(--navy);font-size:16px}.nav .sp{flex:1}
.nav a{color:var(--muted);font-weight:600;font-size:14px;margin-left:18px}.nav a:hover{color:var(--navy);text-decoration:none}
section{padding:64px 20px}.in{max-width:1040px;margin:0 auto}
.hero{background:linear-gradient(160deg,#2b3648,#151b26);color:#fff;text-align:center;padding:74px 20px 80px}
.hero .icon{width:104px;height:104px;border-radius:24px;box-shadow:0 18px 40px rgba(0,0,0,.45);display:block;margin:0 auto 22px}
.eyebrow{color:var(--accent2);font-weight:700;letter-spacing:2px;text-transform:uppercase;font-size:12.5px;margin-bottom:10px}
.hero h1{font-size:46px;line-height:1.05;margin:.1em 0 .2em;letter-spacing:-.5px}
.hero .lead{font-size:21px;font-weight:600;margin:.2em auto;max-width:640px;color:#eef1f6}
.hero .sub{font-size:16px;color:#b9c1cd;max-width:600px;margin:14px auto 0}
.badges{display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin-top:28px}
.badge{display:inline-flex;align-items:center;gap:8px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.18);color:#fff;border-radius:12px;padding:11px 16px;font-weight:600;font-size:14px}
.badge small{display:block;font-size:10.5px;color:#9aa3b1;font-weight:500;letter-spacing:.3px}
h2.t{font-size:30px;text-align:center;color:var(--navy);margin:0 0 8px;letter-spacing:-.3px}
.lede{text-align:center;color:var(--muted);max-width:620px;margin:0 auto 38px}
.why{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}
.why .c{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:24px;box-shadow:0 1px 2px rgba(20,30,50,.04)}
.why .c .ic{font-size:26px}.why .c h3{margin:.5em 0 .2em;color:var(--navy);font-size:18px}.why .c p{margin:0;color:var(--muted);font-size:15px}
.highlight{background:linear-gradient(120deg,#fff3e2,#ffe9cf);border:1px solid #f2d2a6;border-left:5px solid var(--accent);border-radius:14px;padding:20px 24px;margin:0 0 26px;display:flex;gap:16px;align-items:flex-start;text-align:left}
.highlight .ic{font-size:30px;line-height:1}.highlight b{color:var(--navy);font-size:18px;display:block;margin-bottom:3px}.highlight p{margin:0;color:#5a4a35;font-size:15.5px}
.feat{display:grid;grid-template-columns:repeat(2,1fr);gap:12px 28px;max-width:840px;margin:0 auto}
.feat div{padding:12px 0;border-bottom:1px solid var(--line);font-size:15.5px}.feat .k{color:var(--accent);font-weight:800;margin-right:8px}
.stats{background:var(--navy);color:#fff;border-radius:18px;display:flex;flex-wrap:wrap;justify-content:space-around;gap:18px;padding:30px 18px;text-align:center}
.stats .n{font-size:30px;font-weight:800;color:#fff}.stats .l{font-size:13px;color:#aab2c0;letter-spacing:.3px}
.shots{background:linear-gradient(180deg,#eef1f6,#f4f6f9)}
.strip{display:flex;gap:20px;overflow-x:auto;padding:8px 4px 18px;scroll-snap-type:x mandatory}
.shot{flex:0 0 auto;width:230px;scroll-snap-align:center;text-align:center}
.shot img{width:230px;border-radius:22px;box-shadow:0 14px 34px rgba(25,35,60,.18);border:1px solid #e3e7ee;background:#fff}
.shot .cap{font-size:13.5px;color:var(--muted);margin-top:12px;font-weight:600}
footer{background:var(--deep);color:#aeb6c2;text-align:center;padding:44px 20px}
footer .links a{color:#dfe4ec;margin:0 12px;font-weight:600}
footer .small{font-size:12.5px;color:#7f8896;max-width:620px;margin:16px auto 0;line-height:1.6}
/* content pages */
.wrap{max-width:760px;margin:0 auto;padding:34px 20px 60px}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:30px 30px 34px;box-shadow:0 1px 2px rgba(20,30,50,.04)}
.card h1{font-size:26px;color:var(--navy);margin:.1em 0 .1em}
.card h2{font-size:17px;color:var(--navy);margin:1.7em 0 .5em}
.updated{color:var(--muted);font-size:13.5px;margin:0 0 1.3em}
.owner{background:#fbf3e6;border-left:4px solid var(--accent);border-radius:8px;padding:12px 16px;font-size:14.5px;margin:0 0 1.2em}
.card ul{padding-left:1.2em}.card li{margin:.3em 0}
@media(max-width:720px){.hero h1{font-size:36px}.why,.feat{grid-template-columns:1fr}.nav a.hidem{display:none}}
"""

def head(path, m):
    canonical = BASE + "/" if path == "index.html" else f"{BASE}/{path}"
    t = html.escape(m["title"]); d = html.escape(m["desc"])
    ld = ""
    if m.get("app") and not COMING_SOON:
        obj = {
            "@context":"https://schema.org","@type":"MobileApplication",
            "name":"SSM SpecialMente","operatingSystem":"iOS, Android",
            "applicationCategory":"EducationalApplication","inLanguage":"it",
            "description":m["desc"],"image":BASE+"/img/icon.png","url":BASE+"/",
            "publisher":{"@type":"Organization","name":"Neuron Builds","email":EMAIL},
        }
        ld = '<script type="application/ld+json">'+json.dumps(obj, ensure_ascii=False)+'</script>'
    return (
        '<!doctype html><html lang="it"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>{t}</title>'
        f'<meta name="description" content="{d}">'
        f'<meta name="robots" content="{"noindex, nofollow" if COMING_SOON else "index, follow"}">'
        f'<link rel="canonical" href="{canonical}">'
        '<meta name="theme-color" content="#222c3a">'
        '<link rel="icon" href="img/favicon.png">'
        '<meta property="og:type" content="website">'
        '<meta property="og:site_name" content="SSM SpecialMente">'
        '<meta property="og:locale" content="it_IT">'
        f'<meta property="og:title" content="{t}">'
        f'<meta property="og:description" content="{d}">'
        f'<meta property="og:url" content="{canonical}">'
        f'<meta property="og:image" content="{BASE}/img/og-image.png">'
        '<meta property="og:image:width" content="1200">'
        '<meta property="og:image:height" content="630">'
        '<meta name="twitter:card" content="summary_large_image">'
        f'<meta name="twitter:title" content="{t}">'
        f'<meta name="twitter:description" content="{d}">'
        f'<meta name="twitter:image" content="{BASE}/img/og-image.png">'
        f'{ld}'
        f'<style>{CSS}</style></head><body>')

def nav():
    extra = "" if COMING_SOON else ('<a class="hidem" href="index.html#funzioni">Funzioni</a>'
                                    '<a class="hidem" href="index.html#screenshot">Screenshot</a>')
    return ('<div class="nav"><div class="in"><div class="logo">SSM</div><b>SSM SpecialMente</b>'
            '<span class="sp"></span>' + extra +
            '<a href="privacy.html">Privacy</a><a href="supporto.html">Supporto</a></div></div>')

FOOTER = (f'<footer><div class="links"><a href="index.html">Home</a><a href="privacy.html">Privacy</a>'
          f'<a href="supporto.html">Supporto</a><a href="mailto:{EMAIL}">Contatti</a></div>'
          f'<p class="small">© 2026 Neuron Builds · <a href="mailto:{EMAIL}" style="color:#aeb6c2">{EMAIL}</a><br>'
          f'A scopo esclusivamente didattico. I quesiti sono materiale originale di pratica e non riproducono '
          f'le prove ufficiali del concorso.</p></footer></body></html>')

def page(path, m, inner):
    return head(path, m) + nav() + inner + FOOTER

# ---------- inline markdown for legal pages ----------
def inline(t):
    t = html.escape(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', t)
    t = re.sub(r'"([^"]+)"', r'“\1”', t)
    t = re.sub(r'([\w.+-]+@[\w-]+\.[\w.-]+)', r'<a href="mailto:\1">\1</a>', t)
    return t

def md_to_html(md):
    lines = md.split('\n'); out=[]; i=0; first=True
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip(): i+=1; continue
        m = re.match(r'^(#{1,3})\s+(.*)', ln)
        if m:
            lvl=len(m.group(1)); txt=m.group(2)
            if lvl==1 and first: first=False
            else: tag = "h2" if lvl==1 else f"h{lvl}"; out.append(f"<{tag}>{inline(txt)}</{tag}>")
            i+=1; continue
        if re.match(r'^\s*[-*]\s+', ln):
            items=[]
            while i<len(lines) and re.match(r'^\s*[-*]\s+', lines[i]):
                items.append(re.sub(r'^\s*[-*]\s+','',lines[i].rstrip())); i+=1
            out.append("<ul>"+"".join(f"<li>{inline(x)}</li>" for x in items)+"</ul>"); continue
        para=[]
        while i<len(lines) and lines[i].strip() and not re.match(r'^#{1,3}\s',lines[i]) and not re.match(r'^\s*[-*]\s',lines[i]):
            para.append(lines[i].strip()); i+=1
        out.append(f"<p>{inline(' '.join(para))}</p>")
    return "\n".join(out)

# ---------- images ----------
def prep_images():
    os.makedirs(IMG, exist_ok=True)
    icon_src = os.path.join(ROOT,"store-assets","icons","app-store-icon-1024.png")
    ic = Image.open(icon_src).convert("RGB")
    ic.resize((256,256), Image.LANCZOS).save(os.path.join(IMG,"icon.png"))
    ic.resize((48,48), Image.LANCZOS).save(os.path.join(IMG,"favicon.png"))
    for fn,_ in SHOTS:
        s = Image.open(os.path.join(ROOT,"store-assets","screenshots","ios-iphone-6.9",fn)).convert("RGB")
        w=460; h=int(s.size[1]*w/s.size[0])
        s.resize((w,h), Image.LANCZOS).save(os.path.join(IMG,"shot-"+fn.split("-")[0]+".png"))
    # social-share image (1200×630) for Open Graph / Twitter cards
    W,H=1200,630; top=(43,54,72); bot=(21,27,38)
    col=Image.new("RGB",(1,H))
    for y in range(H):
        t=y/(H-1); col.putpixel((0,y),tuple(int(top[i]+(bot[i]-top[i])*t) for i in range(3)))
    og=col.resize((W,H)); d=ImageDraw.Draw(og)
    icon=ic.resize((210,210),Image.LANCZOS)
    mask=Image.new("L",(210,210),0); ImageDraw.Draw(mask).rounded_rectangle([0,0,209,209],radius=46,fill=255)
    og.paste(icon,(96,210),mask)
    d.text((360,224),"APP PER IL CONCORSO SSM",font=ImageFont.truetype(F_BOLD,26),fill=(255,178,77))
    d.text((360,262),"SSM SpecialMente",font=ImageFont.truetype(F_BOLD,82),fill=(255,255,255))
    d.text((360,372),"Lo sprint intelligente verso il concorso SSM",font=ImageFont.truetype(F_REG,32),fill=(201,209,221))
    og.save(os.path.join(IMG,"og-image.png"))

# ---------- landing ----------
WHY = [
    ("🎯","Coach adattivo","Ogni giorno sai cosa ripassare: l'app pianifica in base ai tuoi errori, ai quesiti “scaduti” e agli argomenti ancora scoperti."),
    ("🔁","Ripasso distanziato","I concetti tornano nel momento esatto in cui stai per dimenticarli, per fissarli nella memoria a lungo termine."),
    ("📝","Simulazioni reali","140 quesiti in 210 minuti, esattamente come al concorso, con gestione del tempo e calcolo del punteggio."),
    ("🔒","Offline, senza abbonamenti","Paghi una volta e hai tutto, per sempre. Nessuna pubblicità, nessun account, nessun dato raccolto."),
    ("🃏","Flashcard a richiamo attivo","Memorizza con il metodo dell'active recall: flashcard divise per materia per fissare i concetti chiave."),
    ("🪤","Trappole d'esame","Impara a riconoscere i distrattori più insidiosi — le risposte “quasi giuste” costruite apposta per farti sbagliare."),
    ("📊","Analisi errori e calibrazione","Scopri se sei troppo sicuro o troppo prudente e affina la strategia di risposta sui tuoi dati reali."),
    ("📚","Mini-lezioni e trucchi","Ripassi rapidi, glossario e mnemonici per richiamare i concetti chiave proprio quando ti servono."),
]
FEAT = [
    "Oltre 3.000 quesiti e casi clinici in stile prova",
    "Allenamento per materia su 30 specialità",
    "Simulazioni rapide e a tempo, oltre alla completa",
    "Statistiche, livelli, traguardi e serie giornaliera",
    "Tutto incluso: nessun contenuto a pagamento extra",
]
STATS = [("3.053","quesiti"),("874","flashcard"),("101","mini-lezioni"),("30","specialità"),("140/210","simulazione")]

def landing():
    why = "".join(f'<div class="c"><div class="ic">{e}</div><h3>{t}</h3><p>{d}</p></div>' for e,t,d in WHY)
    feat= "".join(f'<div><span class="k">›</span>{x}</div>' for x in FEAT)
    stats="".join(f'<div><div class="n">{n}</div><div class="l">{l}</div></div>' for n,l in STATS)
    shots="".join(
        f'<div class="shot"><img src="img/shot-{fn.split("-")[0]}.png" alt="{html.escape(cap)}" loading="lazy"><div class="cap">{html.escape(cap)}</div></div>'
        for fn,cap in SHOTS)
    return f"""
<header class="hero">
  <img class="icon" src="img/icon.png" alt="Icona SSM SpecialMente">
  <div class="eyebrow">App di preparazione · Concorso SSM</div>
  <h1>SSM SpecialMente</h1>
  <p class="lead">Lo sprint intelligente verso il concorso SSM.</p>
  <p class="sub">Coach adattivo, simulazioni come la prova reale e ripasso distanziato — oltre 3.000 quesiti, tutto offline. Quesiti tarati un gradino sopra la prova: arrivi al concorso in vantaggio.</p>
  <div class="badges">
    <span class="badge">App Store<small>Presto disponibile</small></span>
    <span class="badge">Google Play<small>Presto disponibile</small></span>
  </div>
</header>

<section id="perche"><div class="in">
  <h2 class="t">Perché SSM SpecialMente è diversa</h2>
  <p class="lede">Non è l'ennesimo archivio di domande da scorrere a caso: ti dice cosa ripassare e ti allena come alla prova vera.</p>
  <div class="highlight"><div class="ic">📈</div><div><b>Tarati per portarti più in alto</b><p>I quesiti sono pensati un gradino sopra la prova reale — distrattori curati e casi clinici realistici. È un allenamento volutamente esigente: se te la cavi qui, al concorso arrivi con un solido margine di vantaggio.</p></div></div>
  <div class="why">{why}</div>
</div></section>

<section id="funzioni" style="padding-top:8px"><div class="in">
  <h2 class="t">Tutto quello che ti serve</h2>
  <p class="lede">Un unico strumento per le settimane decisive.</p>
  <div class="feat">{feat}</div>
  <div class="stats" style="margin-top:42px">{stats}</div>
</div></section>

<section id="screenshot" class="shots"><div class="in">
  <h2 class="t">Dentro l'app</h2>
  <p class="lede">Home, coach, allenamento, studio e progressi — scorri per dare un'occhiata.</p>
  <div class="strip">{shots}</div>
</div></section>
"""

def coming_soon():
    return """
<header class="hero" style="padding:118px 20px 128px">
  <img class="icon" src="img/icon.png" alt="Icona SSM SpecialMente">
  <div class="eyebrow">Concorso SSM · Preparazione</div>
  <h1>SSM SpecialMente</h1>
  <p class="lead">Presto disponibile.</p>
  <p class="sub">L'app per la preparazione al concorso SSM — oltre 3.000 quesiti, simulazioni d'esame e coach adattivo, tutto offline — sta arrivando su App Store e Google Play.</p>
  <div class="badges">
    <span class="badge">App Store<small>Presto disponibile</small></span>
    <span class="badge">Google Play<small>Presto disponibile</small></span>
  </div>
</header>
"""

def build():
    prep_images()
    with open(os.path.join(ROOT,"legal","privacy-policy.md"),encoding="utf-8") as f: priv=f.read()
    with open(os.path.join(ROOT,"legal","supporto.md"),encoding="utf-8") as f: supp=f.read()

    priv_inner = ('<div class="wrap"><main class="card">'
        '<h1>Informativa sulla Privacy</h1>'
        '<p class="updated">Ultimo aggiornamento: giugno 2026</p>'
        '<p class="owner"><strong>Titolare del trattamento:</strong> Arianna Cocchiglia '
        '(operante come <em>Neuron Builds</em>) — Via Luigi Lucatello 2, 35121 Padova (PD), Italia — '
        f'<a href="mailto:{EMAIL}">{EMAIL}</a></p>'
        + md_to_html("\n".join(priv.split('\n')[7:])) + '</main></div>')

    supp_inner = ('<div class="wrap"><main class="card"><h1>Supporto</h1>'
        + md_to_html("\n".join(supp.split('\n')[1:])) + '</main></div>')

    os.makedirs(SITE, exist_ok=True)
    index_inner = coming_soon() if COMING_SOON else landing()
    inners = {"index.html": index_inner, "privacy.html": priv_inner, "supporto.html": supp_inner}
    for name, inner in inners.items():
        with open(os.path.join(SITE,name),"w",encoding="utf-8") as f:
            f.write(page(name, META[name], inner))
        print("✓ site/"+name)
    # robots.txt — pre-lancio blocca tutta l'indicizzazione
    with open(os.path.join(SITE,"robots.txt"),"w",encoding="utf-8") as f:
        if COMING_SOON:
            f.write("User-agent: *\nDisallow: /\n")
        else:
            f.write(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
    # sitemap.xml — vuoto in pre-lancio (non pubblicizza pagine)
    urls = ""
    if not COMING_SOON:
        for name,m in META.items():
            loc = BASE+"/" if name=="index.html" else f"{BASE}/{name}"
            urls += f'  <url><loc>{loc}</loc><lastmod>{LASTMOD}</lastmod><changefreq>monthly</changefreq><priority>{m["prio"]}</priority></url>\n'
    with open(os.path.join(SITE,"sitemap.xml"),"w",encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+urls+'</urlset>\n')
    print(("✓ MODALITÀ PRE-LANCIO: noindex + 'presto disponibile'" if COMING_SOON else "✓ SEO attiva (landing completa)"))
    print("✓ robots.txt + sitemap.xml + immagini")

if __name__ == "__main__":
    build()
    print("Fatto.")
