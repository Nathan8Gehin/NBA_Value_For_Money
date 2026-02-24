import os
import subprocess
import sys
import webbrowser
from datetime import datetime
from threading import Timer

import pandas as pd
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

# Config
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "nba_data.xlsx")
STATS_FILE = os.path.join(BASE_DIR, "data", "NBA_Stat.xlsx")
SCRAPER_PATH = os.path.join(BASE_DIR, "Scrapers", "scrapers_stat.py")
MERGE_PATH = os.path.join(BASE_DIR, "Scripts", "merge_data.py")


def check_and_update_data():
    today = datetime.now().date()
    if (
        not os.path.exists(STATS_FILE)
        or datetime.fromtimestamp(os.path.getmtime(STATS_FILE)).date() < today
    ):
        try:
            py = sys.executable
            print("🚀 Update in progress...")
            subprocess.run([py, SCRAPER_PATH], check=True)
            subprocess.run([py, MERGE_PATH], check=True)
        except Exception as e:
            print(f"Update error: {e}")


check_and_update_data()


def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame()
    df = pd.read_excel(DATA_FILE, sheet_name="Analyse_NBA")
    df.columns = [str(c).strip() for c in df.columns]
    return df


DF = load_data()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>NBA Value For Money</title>
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@400;500;700&family=DM+Mono&display=swap" rel="stylesheet">
    <style>
        :root { --bg: #f5f6fa; --navy: #1a2a4a; --accent: #c8420a; --border: #e2e6f0; --green: #16a34a; --red: #dc2626; --yellow: #d97706; }
        body { font-family: 'DM Sans', sans-serif; background: var(--bg); margin: 0; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
        .topbar { background: var(--navy); color: white; padding: 10px 30px; display: flex; align-items: center; justify-content: space-between; flex-shrink: 0; }
        .search-box { position: relative; width: 450px; }
        #search { width: 100%; padding: 10px 15px; border-radius: 8px; border: none; outline: none; color: #333; }
        #suggestions { position: absolute; background: white; width: 100%; border-radius: 0 0 8px 8px; z-index: 1000; box-shadow: 0 4px 12px rgba(0,0,0,0.1); display: none; }
        .sug-item { padding: 10px; cursor: pointer; border-bottom: 1px solid #eee; color: #333; }
        .sug-item:hover { background: #f0f4ff; }
        .main { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 15px; }
        .dashboard-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }
        .card { background: white; border: 1px solid var(--border); border-radius: 12px; padding: 15px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); }
        .card-title { font-family: 'Bebas Neue'; font-size: 1.3rem; color: var(--navy); border-bottom: 2px solid var(--bg); margin-bottom: 12px; padding-bottom: 5px; }
        .stat-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }
        .stat-box { background: #fcfcfd; border: 1px solid #f1f1f1; padding: 8px; border-radius: 6px; }
        .stat-label { font-size: 0.65rem; color: #888; text-transform: uppercase; font-weight: 800; }
        .stat-value { font-family: 'DM Mono'; font-size: 0.95rem; color: #333; font-weight: 700; }
        .bar-container { margin-bottom: 10px; }
        .bar-label { display: flex; justify-content: space-between; font-size: 0.75rem; margin-bottom: 4px; }
        .bar-bg { background: #eee; height: 6px; border-radius: 3px; overflow: hidden; }
        .bar-fill { height: 100%; transition: width 0.8s ease; }
        .header-card { display: flex; justify-content: space-between; align-items: center; background: white; padding: 20px; border-radius: 12px; border: 1px solid var(--border); }
        .badge { padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.85rem; border: 1px solid transparent; }
        .badge-green { background: #f0fdf4; color: var(--green); border-color: #bbf7d0; }
        .badge-red { background: #fef2f2; color: var(--red); border-color: #fecaca; }
        .badge-yellow { background: #fffbeb; color: var(--yellow); border-color: #fbbf24; }
    </style>
</head>
<body>
<div class="topbar">
    <div style="font-family: 'Bebas Neue'; font-size: 1.6rem;">🏀 NBA VALUE FOR MONEY</div>
    <div class="search-box">
        <input type="text" id="search" placeholder="Search for a player..." autocomplete="off">
        <div id="suggestions"></div>
    </div>
</div>
<div class="main" id="content">
    <div style="text-align:center; margin-top:100px; color:#94a3b8;"><h2>Select a player to begin</h2></div>
</div>
<script>
const search = document.getElementById('search');
const suggestions = document.getElementById('suggestions');
const content = document.getElementById('content');

search.addEventListener('input', async () => {
    const q = search.value.trim();
    if (q.length < 2) { suggestions.style.display = 'none'; return; }
    const res = await fetch(`/api/players?q=${encodeURIComponent(q)}`);
    const players = await res.json();
    suggestions.innerHTML = "";
    players.forEach(p => {
        const div = document.createElement('div');
        div.className = 'sug-item'; div.textContent = p;
        div.onclick = () => loadPlayer(p);
        suggestions.appendChild(div);
    });
    suggestions.style.display = 'block';
});

async function loadPlayer(name) {
    suggestions.style.display = 'none'; search.value = name;
    const res = await fetch(`/api/player?name=${encodeURIComponent(name)}`);
    const p = await res.json();
    render(p);
}

function render(p) {
    let statusCls = 'badge-yellow'; let label = 'WELL PAID';
    if (p.Indicateur && p.Indicateur.includes('Underpaid')) { statusCls = 'badge-green'; label = 'UNDERPAID'; }
    else if (p.Indicateur && p.Indicateur.includes('Overpaid')) { statusCls = 'badge-red'; label = 'OVERPAID'; }

    content.innerHTML = `
        <div class="header-card">
            <div>
                <h1 style="font-family:'Bebas Neue'; font-size:2.8rem; margin:0; color:var(--navy);">${p.Player}</h1>
                <div style="color:#64748b;">${p.Team} • Age: ${p.Age} • ${p.Minutes} MPG</div>
            </div>
            <div style="text-align:right">
                <div class="badge ${statusCls}">${label}</div>
                <div style="margin-top:12px; font-family:'DM Mono'; font-weight:700;">
                    Real: <span style="color:var(--accent)">${p.Salary_Format}</span><br>
                    Projected: <span style="color:var(--navy)">${p.Salary_th_Format}</span>
                </div>
            </div>
        </div>

        <div class="dashboard-grid">
            <div class="card"><div class="card-title">Scoring Volume</div><div class="stat-grid">${sb('Points', p.Points)} ${sb('FGM', p.Field_Goals_Made)} ${sb('FGA', p.Field_Goals_Attempted)} ${sb('3PM', p.Three_PT_Made)}</div></div>
            <div class="card"><div class="card-title">Efficiency</div><div class="stat-grid">${sb('TS%', pct(p.TS_Percentage))} ${sb('FG%', pct(p.FG_Percentage))} ${sb('3P%', pct(p.Three_PT_Percentage))} ${sb('FT%', pct(p.FT_Percentage))}</div></div>
            <div class="card"><div class="card-title">Playmaking</div><div class="stat-grid">${sb('Assists', p.Assists)} ${sb('Turnovers', p.Turnovers)} ${sb('AST/TOV', p.AST_TOV_Ratio)} ${sb('Minutes', p.Minutes)}</div></div>
            <div class="card"><div class="card-title">Rebounding</div><div class="stat-grid">${sb('Off Reb', p.Offensive_Rebounds)} ${sb('Def Reb', p.Defensive_Rebounds)} ${sb('Total Reb', p.Total_Rebounds)} ${sb('Games', p.Games_Played)}</div></div>
            <div class="card"><div class="card-title">Defense</div><div class="stat-grid">${sb('Steals', p.Steals)} ${sb('Blocks', p.Blocks)} ${sb('Fouls', p.Personal_Fouls)} ${sb('Def Score', p.Defensive_Impact)}</div></div>
            <div class="card"><div class="card-title">Team Results</div><div class="stat-grid">${sb('Wins', p.Wins)} ${sb('Losses', p.Losses)} ${sb('Win %', pct(p.Win_Pct))} ${sb('+/-', p.Plus_Minus)}</div></div>

            <div class="card">
                <div class="card-title">League Ranking (#)</div>
                <div class="stat-grid">
                    ${sb('Points Rank', '#' + p.Rank_Points)} ${sb('Assists Rank', '#' + p.Rank_Assists)}
                    ${sb('Rebounds Rank', '#' + p.Rank_Rebounds)} ${sb('Defense Rank', '#' + p.Rank_Defense)}
                </div>
            </div>

            <div class="card">
                <div class="card-title">Impact Analytics</div>
                ${pb('Offensive Impact', p.Offensive_Impact/100, '#c8420a')}
                ${pb('Defensive Impact', p.Defensive_Impact/100, '#2563eb')}
                ${pb('Global Performance', p.Performance_Score, '#16a34a')}
            </div>

            <div class="card">
                <div class="card-title">Contract Value</div>
                <div class="stat-grid">
                    <div class="stat-box" style="grid-column: span 2;"><div class="stat-label">Contract Type</div><div class="stat-value">${p.Contract_Type || 'Standard'}</div></div>
                    ${sb('Current Salary', p.Salary_Format)} ${sb('Value Projection', p.Salary_th_Format)}
                </div>
            </div>
        </div>`;
}

function sb(l, v) { return `<div class="stat-box"><div class="stat-label">${l}</div><div class="stat-value">${v ?? '—'}</div></div>`; }
function pb(l, v, c) {
    const w = Math.min((parseFloat(v) || 0) * 100, 100).toFixed(1);
    return `<div class="bar-container"><div class="bar-label"><span>${l}</span><span>${w}%</span></div><div class="bar-bg"><div class="bar-fill" style="width:${w}%; background:${c}"></div></div></div>`;
}
function pct(v) { return v ? (v * 100).toFixed(1) + '%' : '0%'; }
</script>
</body>
</html>
"""


@app.route("/api/players")
def get_players():
    q = request.args.get("q", "").lower()
    return jsonify(
        DF[DF["Player"].str.lower().str.contains(q, na=False)]["Player"]
        .unique()
        .tolist()[:10]
    )


@app.route("/api/player")
def get_player():
    name = request.args.get("name")
    match = DF[DF["Player"] == name]
    if match.empty:
        return jsonify({"error": "Not found"})
    return jsonify(match.iloc[0].where(pd.notna(match.iloc[0]), None).to_dict())


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


if __name__ == "__main__":
    Timer(1.5, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    app.run(debug=False, port=5000, use_reloader=False)
