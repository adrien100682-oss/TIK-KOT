#!/usr/bin/env python3
"""Collecte PAL : catalogue IGDB + annonces eBay -> data/*.json (sans dépendance externe)."""
import os, json, time, re, base64, datetime, urllib.request, urllib.parse, urllib.error, unicodedata

MAIN_MARKET = "EBAY_FR"      # eBay France
OTHER_MARKETS = ["EBAY_BE", "EBAY_GB", "EBAY_DE", "EBAY_IT", "EBAY_ES"]   # comparaison autres pays (jeux de valeur seulement)
MIN_VALUE = 50               # (autres pays) prix mini pour chercher un jeu
FOREIGN_MAX = 60             # (autres pays) nombre max de jeux cherchés par pays
GBP_EUR = 1.15               # taux approximatif livre -> euro
MAX_CALLS = 4500             # budget d'appels eBay par jour (quota gratuit estimé à ~5000)
DATA = "data"
TODAY = datetime.date.today().isoformat()
EUROPE = {"FR", "BE", "LU", "CH", "DE", "IT", "ES", "GB", "IE", "NL", "PT", "AT"}   # pays de vendeur acceptés
PRIORITY = ["ps2", "ps1", "ps3", "x360", "wii", "ds", "psp", "ps4"]   # consoles faciles à trouver en brocante/magasin : traitées en premier
CHEAP_MAX = 10          # € : un jeu dont les annonces FR "complet" valent en moyenne moins que ça est jugé "bon marché"
CHEAP_MIN_ADS = 3       # il faut au moins 3 annonces pour être sûr qu'il est bon marché
CHEAP_RECHECK = 14      # jours entre deux contrôles d'un jeu bon marché
UNSEEN_RECHECK = 6      # jours entre deux recherches d'un jeu jamais vu en vente (on continue de le chercher)
RESET_ONCE = {"ps2": "v2"}     # repart de zéro UNE seule fois (efface l'ancien historique, pollué par d'anciennes erreurs de tri)
CJK = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af]")                      # titres en japonais/chinois/coréen : ignorés

# Consoles dans l'ordre de priorité. Chaque jour, le script traite celles qui sont "à renouveler" (selon "every"),
# les plus en retard d'abord, tant qu'il reste du budget d'appels. Pour en retirer une, supprime sa ligne.
CONSOLES = [
    {"key": "ps1", "name": "PlayStation 1", "igdb": 7, "q": "ps1", "need": [" ps1 ", " psx ", " ps one ", " psone ", " playstation 1 ", " playstation one "], "every": 2},
    {"key": "ps2", "name": "PlayStation 2", "igdb": 8, "q": "ps2", "need": [" ps2 ", " playstation 2 ", " ps 2 "], "every": 2},
    {"key": "gc", "name": "GameCube", "igdb": 21, "q": "gamecube", "need": [" gamecube ", " game cube ", " ngc "], "every": 5},
    {"key": "xbox", "name": "Xbox", "igdb": 11, "q": "xbox", "need": [" xbox "], "every": 5},
    {"key": "ps3", "name": "PlayStation 3", "igdb": 9, "q": "ps3", "need": [" ps3 ", " playstation 3 ", " ps 3 "], "every": 5},
    {"key": "x360", "name": "Xbox 360", "igdb": 12, "q": "xbox 360", "need": [" xbox 360 ", " x360 ", " 360 "], "every": 5},
    {"key": "ps4", "name": "PlayStation 4", "igdb": 48, "q": "ps4", "need": [" ps4 ", " playstation 4 ", " ps 4 "], "every": 5},
    {"key": "xone", "name": "Xbox One", "igdb": 49, "q": "xbox one", "need": [" xbox one ", " xone "], "every": 5},
    {"key": "switch", "name": "Nintendo Switch", "igdb": 130, "q": "switch", "need": [" switch ", " nintendo switch "], "every": 5, "ban": [" switch 2 "]},
    {"key": "wii", "name": "Wii", "igdb": 5, "q": "wii", "need": [" wii "], "every": 12, "ban": [" wii u ", " wiiu "]},
    {"key": "n64", "name": "Nintendo 64", "igdb": 4, "q": "n64", "need": [" n64 ", " nintendo 64 "], "every": 12},
    {"key": "snes", "name": "Super Nintendo", "igdb": 19, "q": "super nintendo", "need": [" snes ", " super nintendo ", " super nes ", " super famicom "], "every": 12},
    {"key": "nes", "name": "NES", "igdb": 18, "q": "nes", "need": [" nes ", " nintendo nes "], "every": 12},
    {"key": "md", "name": "Mega Drive", "igdb": 29, "q": "mega drive", "need": [" mega drive ", " megadrive ", " genesis "], "every": 12},
    {"key": "dc", "name": "Dreamcast", "igdb": 23, "q": "dreamcast", "need": [" dreamcast "], "every": 12},
    {"key": "saturn", "name": "Saturn", "igdb": 32, "q": "saturn", "need": [" saturn ", " sega saturn "], "every": 12},
    {"key": "gba", "name": "Game Boy Advance", "igdb": 24, "q": "game boy advance", "need": [" gba ", " game boy advance ", " gameboy advance "], "every": 12},
    {"key": "gbc", "name": "Game Boy Color", "igdb": 22, "q": "game boy color", "need": [" game boy color ", " gameboy color ", " gbc "], "every": 12},
    {"key": "gb", "name": "Game Boy", "igdb": 33, "q": "game boy", "need": [" game boy ", " gameboy ", " gb "], "every": 12},
    {"key": "ds", "name": "Nintendo DS", "igdb": 20, "q": "nintendo ds", "need": [" nds ", " nintendo ds ", " ds "], "every": 12},
    {"key": "3ds", "name": "Nintendo 3DS", "igdb": 37, "q": "3ds", "need": [" 3ds ", " nintendo 3ds "], "every": 12},
    {"key": "psp", "name": "PSP", "igdb": 38, "q": "psp", "need": [" psp "], "every": 12},
]
for c in CONSOLES:   # mots interdits = mots des autres consoles (sauf ceux contenus dans les nôtres)
    others = {w for o in CONSOLES if o is not c for w in o["need"]}
    c["_ban"] = [w for w in others if not any(w in n for n in c["need"])] + c.get("ban", [])
ORDER = ["ps2", "ps1", "ps3", "x360", "wii", "ds", "psp", "ps4", "gc", "xbox", "xone", "switch", "3ds", "gba", "gbc", "gb",
         "n64", "snes", "nes", "md", "dc", "saturn"]
EVERY = {"ps2": 2, "ps1": 2, "ps3": 3, "x360": 3, "wii": 3, "ds": 4, "psp": 4, "ps4": 4, "gc": 5, "xbox": 5, "xone": 7, "switch": 7}
for c in CONSOLES:
    c["every"] = EVERY.get(c["key"], c["every"])
CONSOLES.sort(key=lambda c: ORDER.index(c["key"]) if c["key"] in ORDER else 99)
COUNTRY_LANG = {"FR": "FR", "BE": "FR", "DE": "DE", "IT": "IT", "ES": "ES", "GB": "EN", "IE": "EN"}   # BE = français « probable »


def http(url, data=None, headers=None, method=None):
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    for i in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and i < 2:
                time.sleep(3 * (i + 1))
                continue
            raise RuntimeError(f"HTTP {e.code} sur {url.split('?')[0]} : {e.read()[:200]}")
        except urllib.error.URLError:
            time.sleep(2)
    raise RuntimeError("réseau indisponible")


def load(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return default


def save(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))


def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return " " + re.sub(r"[^a-z0-9]+", " ", s).strip() + " "


STOP = {"the", "a", "an", "of", "and", "de", "la", "le", "les", "du", "des", "et", "der", "die", "das"}

def toks(s):
    return frozenset(w for w in norm(s).split() if w not in STOP)


# ---------- Catalogue IGDB ----------
_TOK = {}

def build_catalog(cfg):
    cid, sec = os.environ["TWITCH_CLIENT_ID"], os.environ["TWITCH_CLIENT_SECRET"]
    if "t" not in _TOK:
        q = urllib.parse.urlencode({"client_id": cid, "client_secret": sec, "grant_type": "client_credentials"})
        _TOK["t"] = http("https://id.twitch.tv/oauth2/token?" + q, data=b"", method="POST")["access_token"]
    tok = _TOK["t"]
    h = {"Client-ID": cid, "Authorization": "Bearer " + tok}
    P = cfg["igdb"]
    variantes = [   # du plus précis au plus large : on garde la première qui renvoie des jeux
        f"platforms=({P}) & release_dates.region=(1,8) & version_parent=null",
        f"platforms=({P}) & release_dates.release_region=(1,8) & version_parent=null",
        f"platforms=({P}) & release_dates.region=(1,8)",
        f"platforms=({P}) & version_parent=null",
        f"platforms=({P})",
    ]
    def page(where, off):
        body = f"fields name,cover.image_id,platforms; where {where}; sort id asc; limit 500; offset {off};"
        return http("https://api.igdb.com/v4/games", body.encode(), h, "POST")
    where, first = None, []
    for i, w in enumerate(variantes):
        try:
            first = page(w, 0)
        except RuntimeError as e:
            print(f"Variante {i + 1} refusée : {e}")
            continue
        print(f"Variante {i + 1} : {len(first)} jeux sur la première page")
        if first:
            where = w
            break
    if not where:
        raise RuntimeError(f"IGDB ne renvoie aucun jeu pour {cfg['name']} (numéro de plateforme à vérifier).")
    games, seen, off, pg = [], set(), 0, first
    while True:
        for g in pg:
            n = norm(g["name"])
            if n in seen:
                continue
            seen.add(n)
            img = (g.get("cover") or {}).get("image_id")
            games.append({"id": g["id"], "t": g["name"], "cover": img, "x": 1 if g.get("platforms") == [P] else 0})
        if len(pg) < 500:
            break
        off += 500
        time.sleep(0.4)
        pg = page(where, off)
    print(f"Catalogue {cfg['name']} : {len(games)} jeux")
    return {"date": TODAY, "games": games}


# ---------- Classement des annonces ----------
def has(t, words):
    return any(w in t for w in words)

BAD = [" lot ", " lots ", " bundle ", " pack ", " custom ", " repro ", " reproduction ", " copie ", " copy ", " backup ",
       " burned ", " grave ", " console ", " manette ", " controller ", " memory card ", " carte memoire ", " poster ",
       " guide ", " soundtrack ", " ost ", " figurine ", " peluche ", " x2 ", " x3 ", " x4 ", " 2 jeux ", " 3 jeux "]
# Jeux japonais / américains / importés : jamais comptés comme PAL
NOT_PAL = [" ntsc ", " jap ", " japan ", " japon ", " japonais ", " japanese ", " jp ", " usa ", " us import ", " import ", " asia "]
BOX_ONLY = [" boite seule ", " boitier seul ", " boite vide ", " case only ", " box only ", " empty case ", " sans jeu ",
            " jaquette seule ", " notice seule ", " cover only ", " manual only ", " nur ovp ", " nur hulle ", " cover seule "]
DISC_ONLY = [" disque seul ", " cd seul ", " dvd seul ", " loose ", " disc only ", " game only ", " sans boite ",
             " sans boitier ", " sans jaquette ", " sans etui ", " jeu seul ", " cd only ", " ohne hulle ", " ohne ovp ",
             " nur disc ", " nur spiel ", " senza custodia ", " sin caja "]
INCOMPLETE = [" sans notice ", " sans manuel ", " no manual ", " ohne anleitung ", " notice manquante ", " sans livret "]
NEW_WORDS = [" sealed ", " blister ", " scelle ", " brand new ", " neuf sous ", " factory sealed "]
COMPLETE = [" complet ", " complete ", " cib ", " avec notice ", " avec boite ", " avec boitier ", " boite et notice ",
            " notice incluse ", " with manual ", " avec manuel ", " vollstandig ", " komplett ", " mit anleitung ", " mit ovp ",
            " completo ", " con caja ", " con scatola ", " en boite ", " with box ", " boxed ", " compleet ", " met boekje "]
LANGS = {
    "FR": [" pal fr ", " pal fra ", " francais ", " version francaise ", " fra ", " vf ", " vfr ", " fr ", " frans ", " franse "],
    "DE": [" pal de ", " pal ger ", " deutsch ", " german ", " allemand ", " version allemande "],
    "IT": [" pal it ", " pal ita ", " italiano ", " italian ", " italien ", " ita "],
    "ES": [" pal es ", " pal esp ", " espanol ", " spanish ", " espagnol ", " esp "],
    "EN": [" pal uk ", " pal eng ", " english ", " anglais ", " uk ", " eng "],
}
# Éditions spéciales : le prix ne doit PAS être mélangé avec celui de la version standard
SPECIAL = {
    "collector": [" collector ", " collectors ", " edition collector ", " coffret ", " steelbook ", " ultimate edition ", " deluxe "],
    "limitee": [" limited ", " limitee ", " edition limitee ", " special edition ", " edition speciale ", " anniversary ", " edition anniversaire "],
    "budget": [" platinum ", " greatest hits ", " best of ", " classics ", " player s choice ", " the best ", " essentials "],
    "presse": [" presse ", " press ", " promo ", " promotional ", " not for resale ", " nfr ", " demo ", " preview ",
               " review copy ", " vente interdite ", " exemplaire de presse "],
}

def special(title, gname):
    """Étiquette d'édition spéciale (collector/limitee/budget/presse) ou ''. Ignore les mots qui font partie du nom du jeu."""
    t, gn = norm(title), norm(gname)
    for label, words in SPECIAL.items():
        for w in words:
            if w in t and w not in gn:
                return label
    return ""

def classify(title, cond_id, cfg):
    """Retourne l'état : neuf / complet / disque / boite, ou None si douteux (annonce ignorée)."""
    t = norm(title)
    if has(t, BAD) or has(t, NOT_PAL) or has(t, cfg["_ban"]) or not has(t, cfg["need"]):
        return None
    if has(t, BOX_ONLY):
        return "boite"
    if has(t, DISC_ONLY):
        return "disque"
    if has(t, INCOMPLETE):
        return None
    if cond_id in ("1000", "1500") or has(t, NEW_WORDS):
        return "neuf"
    if has(t, COMPLETE):
        return "complet"
    if cond_id in ("2750", "3000", "4000", "5000", "6000"):
        return "incertain"       # occasion, mais rien n'indique si la boîte/la notice sont là
    return None

def language(title, country):
    """(langue, certaine?) : titre explicite sinon pays du vendeur (probable)."""
    t = norm(title)
    found = [l for l, ws in LANGS.items() if has(t, ws)]
    if len(found) == 1:
        return found[0], True
    if len(found) > 1:
        return None, False
    l = COUNTRY_LANG.get(country)
    return (l, False) if l else (None, False)

def to_eur(v, cur):
    if cur == "EUR":
        return v
    if cur == "GBP":
        return v * GBP_EUR
    return None

def num(v):
    """Lit un nombre même écrit « 26,60 », « 1 249,00 » ou « 1,249.00 »."""
    s = str(v).strip().replace(" ", "").replace("\u00a0", "")
    if "," in s and "." in s:
        s = s.replace(",", "") if s.rfind(".") > s.rfind(",") else s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    return float(s)

def total_price(it):
    p = it.get("price") or {}
    cur = p.get("currency")
    base = to_eur(num(p["value"]), cur) if p.get("value") is not None else None
    if base is None:
        return None
    ship = None
    for o in it.get("shippingOptions") or []:
        c = o.get("shippingCost") or {}
        if c.get("value") is not None and c.get("currency", cur) == cur:
            v = num(c["value"])
            ship = v if ship is None else min(ship, v)
    if ship is None:
        return None          # port inconnu : on ignore plutôt que de fausser le prix
    return round(base + to_eur(ship, cur), 2)

def photo(it):
    u = (it.get("image") or {}).get("imageUrl")
    if not u or not u.startswith("https://"):
        return None
    return re.sub(r"/s-l\d+\.", "/s-l500.", u)


# ---------- eBay ----------
def ebay_token():
    raw = f"{os.environ['EBAY_APP_ID']}:{os.environ['EBAY_CERT_ID']}".encode()
    h = {"Authorization": "Basic " + base64.b64encode(raw).decode(),
         "Content-Type": "application/x-www-form-urlencoded"}
    body = urllib.parse.urlencode({"grant_type": "client_credentials",
                                   "scope": "https://api.ebay.com/oauth/api_scope"}).encode()
    return http("https://api.ebay.com/identity/v1/oauth2/token", body, h, "POST")["access_token"]

def ebay_search(tok, market, q):
    p = urllib.parse.urlencode({"q": q, "limit": 100, "filter": "buyingOptions:{FIXED_PRICE}"})
    h = {"Authorization": "Bearer " + tok, "X-EBAY-C-MARKETPLACE-ID": market,
         "X-EBAY-C-ENDUSERCTX": "contextualLocation=country%3DFR%2Czip%3D77000"}
    return http("https://api.ebay.com/buy/browse/v1/item_summary/search?" + p, headers=h).get("itemSummaries", [])


def due(info):
    """Faut-il (re)chercher ce jeu aujourd'hui ?  info = [date, bon_marché, déjà_vu] ou None (jamais cherché)."""
    if not info:
        return True
    age = (datetime.date.today() - datetime.date.fromisoformat(info[0])).days
    return age >= (CHEAP_RECHECK if info[1] else (0 if info[2] else UNSEEN_RECHECK))

def load_scan(key):
    return {} if is_fresh(key) else load(f"{DATA}/{key}/scan.json", {})

def is_fresh(key):
    return key in RESET_ONCE and not os.path.exists(f"{DATA}/{key}/reset_{RESET_ONCE[key]}.flag")

def run_console(cfg, games, tok, budget):
    """Collecte une console. Retourne (appels utilisés, arrêt d'urgence ?)."""
    key = cfg["key"]
    D = f"{DATA}/{key}"
    os.makedirs(D, exist_ok=True)
    def ld(name, default):          # ancienne organisation : les données PS2 étaient à la racine
        v = load(f"{D}/{name}")
        return v if v is not None else (load(f"{DATA}/{name}", default) if key == "ps2" else default)

    gt = {g["id"]: toks(g["t"]) for g in games}
    # suites : jeux dont le nom contient strictement tous les mots de celui-ci
    supers = {gid: [t2 for g2, t2 in gt.items() if g2 != gid and t < t2] for gid, t in gt.items()}
    # Annonce qui contient AUSSI le nom d'un autre jeu plus long (ex. « Vandal Hearts II ... Suikoden 2 » : démo en bonus) :
    # elle appartient à l'autre jeu, pas à celui-ci.
    df = {}
    for t in gt.values():
        for w in t:
            df[w] = df.get(w, 0) + 1
    byrare = {}
    for gid, t in gt.items():
        if t:
            byrare.setdefault(min(t, key=lambda w: (df[w], w)), []).append(gid)
    def other_game(gid, tt):
        t = gt[gid]
        for w in tt:
            for g2 in byrare.get(w, ()):
                t2 = gt[g2]
                if g2 != gid and len(t2) > len(t) and t2 <= tt and not t <= t2:
                    return True
        return False
    flag = f"{D}/reset_{RESET_ONCE[key]}.flag" if key in RESET_ONCE else None
    fresh = is_fresh(key)                                 # première collecte après remise à zéro ?
    if fresh:
        print(f"{cfg['name']} : remise à zéro de l'historique (une seule fois).")
    hist = {} if fresh else ld("history.json", {})
    fxd = {} if fresh else load(f"{D}/fx.json", {})   # jeux dont les autres pays ont été cherchés : date
    sinfo = {} if fresh else load(f"{D}/scan.json", {})   # par jeu : [date de recherche, bon marché ?, déjà vu en vente ?]
    hval = {int(gid): max([h["last"] for h in ks.values() if h.get("last")] or [0]) for gid, ks in hist.items()}
    todo = [g for g in games if due(sinfo.get(str(g["id"])))]
    todo.sort(key=lambda g: (-hval.get(g["id"], 0), (sinfo.get(str(g["id"])) or [""])[0]))   # valeur d'abord, puis les plus anciens
    print(f"{cfg['name']} : {len(todo)} jeux à chercher sur {len(games)}")
    seen, rows, searched = set(), [], set()
    state = {"calls": 0, "errors": 0, "stop": False, "amb": 0}

    def scan(g, m):
        if state["stop"] or state["calls"] >= budget:
            return
        state["calls"] += 1
        try:
            items = ebay_search(tok, m, f"{g['t']} {cfg['q']}")
        except RuntimeError as e:
            print("Erreur :", e)
            state["errors"] += 1
            if state["errors"] >= 5:
                print("Trop d'erreurs d'affilée : arrêt (quota dépassé ou panne eBay).")
                state["stop"] = True
            return
        state["errors"] = 0
        gid = g["id"]
        for it in items:
            iid = it["itemId"]
            title = it.get("title", "")
            tt = toks(title)
            if iid in seen or not gt[gid] <= tt or any(sp <= tt for sp in supers[gid]):
                continue
            if other_game(gid, tt):
                state["amb"] += 1
                continue                  # le titre contient le nom d'un autre jeu (démo/bonus) : on ne l'attribue pas à celui-ci
            country = (it.get("itemLocation") or {}).get("country")
            if (country and country not in EUROPE) or CJK.search(title):
                continue                  # vendeur hors Europe ou titre asiatique : on ignore
            cond = classify(title, it.get("conditionId"), cfg)
            lang, sure = language(title, country)
            tot = total_price(it)
            if not cond or not lang or tot is None:
                continue
            if tot >= 300 and state.get("hp", 0) < 30:
                state["hp"] = state.get("hp", 0) + 1
                print("PRIX ÉLEVÉ :", title[:70], "| prix brut :", it.get("price"), "| port :",
                      [o.get("shippingCost") for o in it.get("shippingOptions") or []])
            sp = special(title, g["t"])
            seen.add(iid)
            rows.append({"id": iid, "g": gid, "k": f"{lang}|{cond}" + (f"|{sp}" if sp else ""), "p": tot,
                         "u": it.get("itemWebUrl"), "s": sure, "m": m, "i": photo(it)})
        searched.add((gid, m))

    for g in todo:                        # 1) les jeux à renouveler sur eBay.fr
        scan(g, MAIN_MARKET)
    val = {}                              # 2) autres pays : jeux de valeur seulement
    for r in rows:
        val[r["g"]] = max(val.get(r["g"], 0), r["p"])
    for gid, ks in hist.items():
        for h in ks.values():
            if h.get("last"):
                val[int(gid)] = max(val.get(int(gid), 0), h["last"])
    cand = [g for g in sorted(games, key=lambda g: -val.get(g["id"], 0)) if val.get(g["id"], 0) >= MIN_VALUE]
    per = max(0, min(FOREIGN_MAX, (budget - state["calls"]) // max(1, len(OTHER_MARKETS))))
    for m in OTHER_MARKETS:
        for g in cand[:per]:
            scan(g, m)
    for g in cand[:per]:
        if (g["id"], OTHER_MARKETS[0] if OTHER_MARKETS else MAIN_MARKET) in searched:
            fxd[str(g["id"])] = TODAY
    save(f"{D}/fx.json", fxd)
    print(f"{cfg['name']} : {state['calls']} appels eBay, {len(rows)} annonces retenues, "
          f"{state['amb']} écartées (titre contenant le nom d'un autre jeu)")

    # Garde-fou : prix aberrant (>= 500 € et >= 40 fois la médiane des autres annonces du même jeu) = ignoré
    bygame = {}
    for r in rows:
        bygame.setdefault(r["g"], []).append(r)
    bad = set()
    for gid, lst in bygame.items():
        for r in lst:
            others = sorted(x["p"] for x in lst if x is not r)
            if r["p"] >= 500 and len(others) >= 2 and r["p"] >= 40 * others[len(others) // 2]:
                bad.add(r["id"])
                print(f"Prix aberrant ignoré : {r['p']} € (autres annonces : {others[:4]}) {r['u']}")
    rows = [r for r in rows if r["id"] not in bad]

    # Mémoire par jeu : bon marché (on le recontrôlera rarement) ou jamais vu (on continue de le chercher)
    by = {}
    for r in rows:
        if r["k"].endswith("|complet"):
            by.setdefault(r["g"], {}).setdefault(r["k"].split("|")[0], []).append(r["p"])
    def cheap(gid):
        langs = by.get(gid) or {}
        if len(langs.get("FR", [])) < CHEAP_MIN_ADS:
            return False
        return all(sum(sorted(ps)[:3]) / len(sorted(ps)[:3]) < CHEAP_MAX for ps in langs.values())
    rowg = {r["g"] for r in rows}
    for gid in {g for g, m in searched if m == MAIN_MARKET}:
        was = str(gid) in hist and any(h.get("last") for h in hist[str(gid)].values())
        sinfo[str(gid)] = [TODAY, 1 if cheap(gid) else 0, 1 if (gid in rowg or was) else 0]
    save(f"{D}/scan.json", sinfo)
    print(f"{cfg['name']} : {sum(1 for v in sinfo.values() if v[1])} jeux jugés bon marché (< {CHEAP_MAX} €), "
          f"{sum(1 for v in sinfo.values() if not v[2])} jamais vus en vente")

    # Annonces disparues depuis hier = ventes estimées
    prev = {} if fresh else ld("snap.json", {})
    today_ids = {r["id"] for r in rows}
    gone, snap = {}, {r["id"]: [r["g"], r["k"], r["m"]] for r in rows}
    for iid, v in prev.items():
        gid, k, m = v[0], v[1], (v[2] if len(v) > 2 else MAIN_MARKET)
        if iid in today_ids:
            continue
        if (gid, m) in searched:
            gone[(gid, k)] = gone.get((gid, k), 0) + 1
        else:
            snap[iid] = v                 # pas cherché aujourd'hui : on le garde pour demain
    save(f"{D}/snap.json", snap)

    # Agrégation du jour
    groups = {}
    for r in rows:
        groups.setdefault((r["g"], r["k"]), []).append(r)

    for gk in set(groups) | set(gone):
        gid, k = gk
        lst = sorted(groups.get(gk, []), key=lambda r: r["p"])
        ref = round(sum(r["p"] for r in lst[:3]) / len(lst[:3]), 2) if lst else None
        h = hist.setdefault(str(gid), {}).setdefault(k, {"s": []})
        if ref is not None:
            h["last"], h["date"] = ref, TODAY
        h["s"] = (h["s"] + [[TODAY, ref, len(lst), gone.get(gk, 0)]])[-400:]
        if lst:
            h["now"] = {"n": len(lst), "ref": ref, "min": lst[0]["p"], "url": lst[0]["u"],
                        "top": [[r["p"], r["u"], r.get("i") if j == 0 else None] for j, r in enumerate(lst[:3])],
                        "sure": sum(1 for r in lst if r["s"]), "d": TODAY}
        else:
            h.pop("now", None)
    scanned = {g for g, m in searched}
    for gid, ks in hist.items():          # annonces plus vues : on retire l'état « en vente »
        for k, h in ks.items():
            if (int(gid), k) in groups or "now" not in h:
                continue
            old = (datetime.date.today() - datetime.date.fromisoformat(h["now"].get("d", TODAY))).days
            if int(gid) not in scanned:   # jeu pas cherché aujourd'hui (bon marché) : on garde l'ancien état un moment
                if old >= 21:
                    h.pop("now")
                continue
            if (k.startswith("FR|") and (int(gid), MAIN_MARKET) in searched) or old >= 7:
                h.pop("now")
    save(f"{D}/history.json", hist)

    # Fichier lu par le site
    limit = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
    out = []
    for g in games:
        ks = hist.get(str(g["id"]))
        if not ks:
            continue
        d = {}
        for k, h in ks.items():
            e = dict(h.get("now") or {})
            e["last"], e["date"] = h.get("last"), h.get("date")
            e["sold30"] = sum(x[3] for x in h["s"] if x[0] >= limit)
            e["since"] = h["s"][0][0]
            d[k] = e
        out.append({"id": g["id"], "t": g["t"], "cover": g["cover"], "x": g.get("x", 0), "fx": fxd.get(str(g["id"])), "k": d})
    save(f"{D}/latest.json", {"updated": TODAY, "console": cfg["name"], "catalog_total": len(games), "games": out})
    if fresh and not state["stop"]:
        with open(flag, "w") as f:
            f.write(TODAY)
    return state["calls"], state["stop"]


def main():
    os.makedirs(DATA, exist_ok=True)
    state = load(f"{DATA}/state.json", {})
    def retard(c):          # >= 1 : la console est à renouveler (jamais traitée = en tête)
        d = state.get(c["key"])
        return 1e9 if not d else (datetime.date.today() - datetime.date.fromisoformat(d)).days / c["every"]
    order = sorted([c for c in CONSOLES if retard(c) >= 1],
                   key=lambda c: (c["key"] not in PRIORITY, PRIORITY.index(c["key"]) if c["key"] in PRIORITY else 0, -retard(c)))
    have_ebay = bool(os.environ.get("EBAY_APP_ID") and os.environ.get("EBAY_CERT_ID"))
    tok, used, ran = (ebay_token() if have_ebay else None), 0, 0
    for cfg in order:
        D = f"{DATA}/{cfg['key']}"
        os.makedirs(D, exist_ok=True)
        cat = load(f"{D}/catalog.json") or (load(f"{DATA}/catalog.json") if cfg["key"] == "ps2" else None)
        if not cat or not cat.get("games") or "x" not in cat["games"][0] or (datetime.date.today() - datetime.date.fromisoformat(cat["date"])).days >= 7:
            try:
                cat = build_catalog(cfg)
            except RuntimeError as e:
                print("Catalogue impossible :", e)
                continue
            save(f"{D}/catalog.json", cat)
        if not have_ebay:
            print("Clés eBay absentes : seul le catalogue a été mis à jour.")
            break
        sc = load_scan(cfg["key"])
        n = sum(1 for g in cat["games"] if due(sc.get(str(g["id"]))))   # nombre de jeux à chercher aujourd'hui
        if ran and used + n > MAX_CALLS:
            print(f"{cfg['name']} : trop gros pour le budget restant, repoussé.")
            continue
        calls, stop = run_console(cfg, cat["games"], tok, MAX_CALLS - used)
        used += calls
        ran += 1
        state[cfg["key"]] = TODAY
        save(f"{DATA}/state.json", state)
        if stop:
            break
    index = []
    for cfg in CONSOLES:
        lt = load(f"{DATA}/{cfg['key']}/latest.json") or (load(f"{DATA}/latest.json") if cfg["key"] == "ps2" else None)
        if lt:
            index.append({"key": cfg["key"], "name": cfg["name"], "updated": lt["updated"], "games": len(lt["games"])})
    save(f"{DATA}/consoles.json", index)
    print(f"Total : {used} appels eBay, {ran} console(s) traitée(s)")


if __name__ == "__main__":
    main()
