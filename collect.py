<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
    <title>Sondage Éclair - Rétro</title>
    <style>
        :root { --bg: #0d0f14; --fg: #f2f3f7; --mut: #a3a9bd; --card: #171a22; --line: #2a2f3d; --acc: #ffb020; --lbc: #ff6e14; --vinted: #09b1ba; }
        * { box-sizing: border-box; }
        body { background: var(--bg); color: var(--fg); font-family: system-ui, -apple-system, sans-serif; margin: 0; padding: 20px; }
        header { max-width: 900px; margin: 0 auto 20px auto; background: var(--card); padding: 20px; border-radius: 12px; border: 1px solid var(--line); }
        h1 { color: var(--acc); margin: 0 0 10px 0; font-size: 24px; }
        .controls { display: flex; gap: 20px; flex-wrap: wrap; align-items: center; margin-top: 15px; }
        .controls label { display: flex; flex-direction: column; gap: 5px; font-size: 14px; color: var(--mut); }
        .controls input, .controls select { background: var(--bg); color: var(--fg); border: 1px solid var(--mut); border-radius: 6px; padding: 6px 10px; font-size: 14px; }
        .container { max-width: 900px; margin: 0 auto; display: flex; flex-direction: column; gap: 10px; }
        .row { background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 12px 16px; display: flex; align-items: center; justify-content: space-between; gap: 15px; }
        .info { flex: 1; min-width: 0; }
        .game-title { font-weight: 700; font-size: 16px; margin: 0 0 4px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .game-meta { font-size: 13px; color: var(--mut); display: flex; gap: 10px; }
        .price-tag { font-weight: 800; color: var(--acc); font-size: 16px; white-space: nowrap; }
        .actions { display: flex; gap: 8px; flex-shrink: 0; }
        .btn { text-decoration: none; font-weight: 700; font-size: 13px; padding: 8px 12px; border-radius: 6px; color: #fff; white-space: nowrap; display: inline-block; }
        .btn-lbc { background: var(--lbc); }
        .btn-vinted { background: var(--vinted); }
        .empty { text-align: center; padding: 40px; color: var(--mut); }
    </style>
</head>
<body>

<header>
    <h1>⚡ Console de Sondage Rapide (LBC & Vinted)</h1>
    <div style="font-size: 13px; color: var(--mut);">Cible tes jeux de valeur. Les liens ouvrent directement les plateformes avec un <b>tri par nouveauté</b> et les vrais noms de consoles.</div>
    <div class="controls">
        <label>Valeur minimum de la cote (€) : 
            <input type="number" id="min-price" value="40" min="0" step="5" oninput="renderList()">
        </label>
        <label>Filtrer par console : 
            <select id="console-filter" onchange="renderList()">
                <option value="ALL">Toutes les consoles</option>
            </select>
        </label>
        <div style="margin-left: auto; font-size: 14px; color: var(--mut);">Jeux affichés : <b id="count" style="color:var(--fg)">0</b></div>
    </div>
</header>

<div class="container" id="list-container">
    <div class="empty">Chargement des données de ton catalogue...</div>
</div>

<script>
let allGames = [];
const consolesList = ["ps1", "ps2", "ps3", "ps4", "psp", "gc", "switch", "wii", "ds", "3ds", "xbox", "x360", "snes", "nes", "n64", "gb", "gba", "dc", "saturn", "md"];

// Correspondance propre pour éviter les diminutifs obscurs dans les moteurs de recherche
const CONSOLE_NAMES = {
    "PS1": "PlayStation 1",
    "PS2": "PlayStation 2",
    "PS3": "PlayStation 3",
    "PS4": "PlayStation 4",
    "PSP": "PSP",
    "GC": "Gamecube",
    "SWITCH": "Nintendo Switch",
    "WII": "Nintendo Wii",
    "DS": "Nintendo DS",
    "3DS": "Nintendo 3DS",
    "XBOX": "Xbox",
    "X360": "Xbox 360",
    "SNES": "Super Nintendo",
    "NES": "NES",
    "N64": "Nintendo 64",
    "GB": "Game Boy",
    "GBA": "Game Boy Advance",
    "DC": "Dreamcast",
    "SATURN": "Sega Saturn",
    "MD": "Mega Drive"
};

async function initSondage() {
    let select = document.getElementById('console-filter');
    let loadedData = [];

    for (let key of consolesList) {
        try {
            let res = await fetch(`data/${key}/latest.json`);
            if (!res.ok) continue;
            let data = await res.json();
            
            data.games.forEach(g => {
                if (!g.k) return;
                Object.entries(g.k).forEach(([vKey, info]) => {
                    if (vKey.includes("complet") && (info.ref || info.min)) {
                        loadedData.push({
                            id: g.id,
                            name: g.t,
                            consoleKey: key.toUpperCase(),
                            consoleName: CONSOLE_NAMES[key.toUpperCase()] || key.toUpperCase(),
                            price: info.ref || info.min
                        });
                    }
                });
            });
        } catch (e) {}
    }

    allGames = loadedData;
    
    let foundConsoles = [...new Set(allGames.map(g => g.consoleKey))].sort();
    foundConsoles.forEach(c => {
        let opt = document.createElement('option');
        opt.value = c;
        opt.textContent = CONSOLE_NAMES[c] || c;
        select.appendChild(opt);
    });

    renderList();
}

function renderList() {
    const minVal = parseFloat(document.getElementById('min-price').value) || 0;
    const selectedConsole = document.getElementById('console-filter').value;
    const container = document.getElementById('list-container');

    let filtered = allGames.filter(g => {
        if (g.price < minVal) return false;
        if (selectedConsole !== "ALL" && g.consoleKey !== selectedConsole) return false;
        return true;
    });

    filtered.sort((a, b) => b.price - a.price);
    document.getElementById('count').textContent = filtered.length;

    if (filtered.length === 0) {
        container.innerHTML = `<div class="empty">Aucun jeu ne correspond à ce seuil de prix. Baisse le filtre minimum !</div>`;
        return;
    }

    container.innerHTML = filtered.map(item => {
        // On combine le nom du jeu et le vrai nom de la console pour une recherche propre
        const searchQuery = `${item.name} ${item.consoleName}`;
        const queryEncoded = encodeURIComponent(searchQuery);

        // URLs optimisées : 
        // - Leboncoin : tri par date (sort=time)
        // - Vinted : recherche textuelle avec ordre des plus récents (order=newest_first) et filtres basiques pour limiter les prix absurdes ou le non-jeu si besoin
        const lbcUrl = `https://www.leboncoin.fr/recherche?text=${queryEncoded}&sort=time`;
        const vintedUrl = `https://www.vinted.fr/catalog?search_text=${queryEncoded}&order=newest_first`;

        return `
            <div class="row">
                <div class="info">
                    <div class="game-title" title="${item.name}">${item.name}</div>
                    <div class="game-meta">
                        <span>Console : <b>${item.consoleName}</b></span>
                    </div>
                </div>
                <div class="price-tag">~${Math.round(item.price)} €</div>
                <div class="actions">
                    <a href="${lbcUrl}" target="_blank" rel="noopener" class="btn btn-lbc" title="Rechercher sur Leboncoin (Plus récents)">LBC ↗</a>
                    <a href="${vintedUrl}" target="_blank" rel="noopener" class="btn btn-vinted" title="Rechercher sur Vinted (Plus récents)">Vinted ↗</a>
                </div>
            </div>
        `;
    }).join("");
}

initSondage();
</script>

</body>
</html>
