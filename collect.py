#!/usr/bin/env python3
"""Collecte PS2 PAL : catalogue IGDB + annonces eBay -> data/*.json (sans dépendance externe)."""
import os, json, time, re, base64, datetime, urllib.request, urllib.parse, urllib.error, unicodedata

IGDB_PLATFORM = 8            # PlayStation 2
MARKETS = ["EBAY_FR"]        # plus tard : "EBAY_DE", "EBAY_IT", "EBAY_ES"
MAX_CALLS = 4500             # sécurité sur le quota gratuit eBay
DATA = "data"
TODAY = datetime.date.today().isoformat()
COUNTRY_LANG = {"FR": "FR", "DE": "DE", "IT": "IT", "ES": "ES", "GB": "EN", "IE": "EN"}


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


# ---------- Catalogue IGDB ----------
def build_catalog():
    cid, sec = os.environ["TWITCH_CLIENT_ID"], os.environ["TWITCH_CLIENT_SECRET"]
    q = urllib.parse.urlencode({"client_id": cid, "client_secret": sec, "grant_type": "client_credentials"})
    tok = http("https://id.twitch.tv/oauth2/token?" + q, data=b"", method="POST")["access_token"]
    h = {"Client-ID": cid, "Authorization": "Bearer " + tok}
    games, seen, off = [], set(), 0
    while True:
        body = (f"fields name,cover.image_id; where platforms=({IGDB_PLATFORM}) & release_dates.region=1 "
                f"& release_dates.platform={IGDB_PLATFORM} & version_parent=null; sort id asc; limit 500; offset {off};")
        page = http("https://api.igdb.com/v4/games", body.encode(), h, "POST")
        for g in page:
            n = norm(g["name"])
            if n in seen:
                continue
            seen.add(n)
            img = (g.get("cover") or {}).get("image_id")
            games.append({"id": g["id"], "t": g["name"], "cover": img})
        if len(page) < 500:
            break
        off += 500
        time.sleep(0.4)
    print(f"Catalogue : {len(games)} jeux")
    return {"date": TODAY, "games": games}


# ---------- Classement des annonces ----------
def has(t, words):
    return any(w in t for w in words)

BAD = [" lot ", " lots ", " bundle ", " pack ", " custom ", " repro ", " reproduction ", " copie ", " copy ", " backup ",
       " burned ", " grave ", " console ", " manette ", " controller ", " memory card ", " carte memoire ", " poster ",
       " guide ", " soundtrack ", " ost ", " figurine ", " peluche ", " x2 ", " x3 ", " x4 ", " 2 jeux ", " 3 jeux "]
OTHER_PLAT = [" ps1 ", " ps3 ", " ps4 ", " ps5 ", " psp ", " psx ", " xbox ", " gamecube ", " wii ", " switch ", " dreamcast "]
BOX_ONLY = [" boite seule ", " boitier seul ", " boite vide ", " case only ", " box only ", " empty case ", " sans jeu ",
            " jaquette seule ", " notice seule ", " cover only ", " manual only ", " nur ovp ", " nur hulle ", " cover seule "]
DISC_ONLY = [" disque seul ", " cd seul ", " dvd seul ", " loose ", " disc only ", " game only ", " sans boite ",
             " sans boitier ", " sans jaquette ", " sans etui ", " jeu seul ", " cd only ", " ohne hulle ", " ohne ovp ",
             " nur disc ", " nur spiel ", " senza custodia ", " sin caja "]
INCOMPLETE = [" sans notice ", " sans manuel ", " no manual ", " ohne anleitung ", " notice manquante ", " sans livret "]
NEW_WORDS = [" sealed ", " blister ", " scelle ", " brand new ", " neuf sous ", " factory sealed "]
COMPLETE = [" complet ", " complete ", " cib ", " avec notice ", " avec boite ", " avec boitier ", " boite et notice ",
            " notice incluse ", " with manual ", " avec manuel ", " vollstandig ", " komplett ", " mit anleitung ", " mit ovp ",
            " completo ", " con caja ", " con scatola ", " en boite ", " with box ", " boxed "]
LANGS = {
    "FR": [" pal fr ", " pal fra ", " francais ", " version francaise ", " fra "],
    "DE": [" pal de ", " pal ger ", " deutsch ", " german ", " allemand ", " version allemande "],
    "IT": [" pal it ", " pal ita ", " italiano ", " italian ", " italien ", " ita "],
    "ES": [" pal es ", " pal esp ", " espanol ", " spanish ", " espagnol ", " esp "],
    "EN": [" pal uk ", " pal eng ", " english ", " anglais ", " uk ", " eng "],
}

def classify(title, cond_id):
    """Retourne l'état : neuf / complet / disque / boite, ou None si douteux (annonce ignorée)."""
    t = norm(title)
    if has(t, BAD) or has(t, OTHER_PLAT):
        return None
    if " ps2 " not in t and " playstation 2 " not in t and " ps 2 " not in t:
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

def total_price(it):
    p = it.get("price") or {}
    if p.get("currency") != "EUR":
        return None
    ship = None
    for o in it.get("shippingOptions") or []:
        c = o.get("shippingCost") or {}
        if c.get("value") is not None and c.get("currency", "EUR") == "EUR":
            v = float(c["value"])
            ship = v if ship is None else min(ship, v)
    if ship is None:
        return None          # port inconnu : on ignore plutôt que de fausser le prix
    return round(float(p["value"]) + ship, 2)


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


def main():
    os.makedirs(DATA, exist_ok=True)
    cat = load(f"{DATA}/catalog.json")
    if not cat or (datetime.date.today() - datetime.date.fromisoformat(cat["date"])).days >= 7:
        cat = build_catalog()
        save(f"{DATA}/catalog.json", cat)
    games = cat["games"]
    if not (os.environ.get("EBAY_APP_ID") and os.environ.get("EBAY_CERT_ID")):
        print("Clés eBay absentes : seul le catalogue a été mis à jour.")
        return

    names = {g["id"]: norm(g["t"]) for g in games}
    supers = {gid: [n2 for g2, n2 in names.items() if g2 != gid and n in n2] for gid, n in names.items()}
    tok, calls, seen, rows, searched = ebay_token(), 0, set(), [], set()

    for g in games:
        gid, n = g["id"], names[g["id"]]
        if calls + len(MARKETS) > MAX_CALLS:
            print("Quota atteint : le reste sera traité demain.")
            break
        for m in MARKETS:
            calls += 1
            try:
                items = ebay_search(tok, m, f"{g['t']} ps2")
            except RuntimeError as e:
                print("Erreur :", e)
                continue
            for it in items:
                iid = it["itemId"]
                title = it.get("title", "")
                tn = norm(title)
                if iid in seen or n not in tn or has(tn, supers[gid]):
                    continue
                cond = classify(title, it.get("conditionId"))
                lang, sure = language(title, (it.get("itemLocation") or {}).get("country"))
                tot = total_price(it)
                if not cond or not lang or tot is None:
                    continue
                seen.add(iid)
                rows.append({"id": iid, "g": gid, "k": f"{lang}|{cond}", "p": tot, "u": it.get("itemWebUrl"), "s": sure})
        searched.add(gid)
    print(f"{calls} appels eBay, {len(rows)} annonces retenues")

    # Annonces disparues depuis hier = ventes estimées
    prev = load(f"{DATA}/snap.json", {})
    today_ids = {r["id"] for r in rows}
    gone = {}
    for iid, (gid, k) in prev.items():
        if iid not in today_ids and gid in searched:
            gone[(gid, k)] = gone.get((gid, k), 0) + 1
    save(f"{DATA}/snap.json", {r["id"]: [r["g"], r["k"]] for r in rows})

    # Agrégation du jour
    groups = {}
    for r in rows:
        groups.setdefault((r["g"], r["k"]), []).append(r)

    hist = load(f"{DATA}/history.json", {})
    for key in set(groups) | set(gone):
        gid, k = key
        lst = sorted(groups.get(key, []), key=lambda r: r["p"])
        ref = round(sum(r["p"] for r in lst[:3]) / len(lst[:3]), 2) if lst else None
        h = hist.setdefault(str(gid), {}).setdefault(k, {"s": []})
        if ref is not None:
            h["last"], h["date"] = ref, TODAY
        h["s"] = (h["s"] + [[TODAY, ref, len(lst), gone.get(key, 0)]])[-400:]
        if lst:
            h["now"] = {"n": len(lst), "ref": ref, "min": lst[0]["p"], "url": lst[0]["u"],
                        "sure": sum(1 for r in lst if r["s"])}
        else:
            h.pop("now", None)
    for gid, ks in hist.items():                       # jeux plus vus aujourd'hui
        for k, h in ks.items():
            if (int(gid), k) not in groups and "now" in h and int(gid) in searched:
                h.pop("now")
    save(f"{DATA}/history.json", hist)

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
            e["sold30"] = sum(s[3] for s in h["s"] if s[0] >= limit)
            e["since"] = h["s"][0][0]
            d[k] = e
        out.append({"id": g["id"], "t": g["t"], "cover": g["cover"], "k": d})
    save(f"{DATA}/latest.json", {"updated": TODAY, "console": "PS2", "catalog_total": len(games), "games": out})


if __name__ == "__main__":
    main()
