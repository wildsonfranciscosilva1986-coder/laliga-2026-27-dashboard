#!/usr/bin/env python3
"""Fetch the official LALIGA EA SPORTS 2026/27 gameweek pages into a CSV."""
from __future__ import annotations
import csv, json, requests
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = 'https://www.laliga.com/laliga-easports/resultados/2026-27/jornada-{}'
MADRID = ZoneInfo('Europe/Madrid')
OUT = ROOT / 'laliga_2026_27_matches_official.csv'

rows = []
for rnd in range(1, 39):
    url = BASE.format(rnd)
    response = requests.get(url, timeout=30, headers={'User-Agent':'Mozilla/5.0 LaLigaDashboard/1.0'})
    response.raise_for_status()
    page = BeautifulSoup(response.text, 'html.parser')
    node = page.find('script', id='__NEXT_DATA__')
    if not node or not node.string:
        raise RuntimeError(f'No official match data on round {rnd}: {url}')
    props = json.loads(node.string)['props']['pageProps']
    matches = props.get('matches') or []
    if len(matches) != 10:
        raise RuntimeError(f'Expected 10 official fixtures in round {rnd}; got {len(matches)}')
    for m in matches:
        dt = datetime.fromisoformat(m['date']) if m.get('date') else None
        local_date = dt.astimezone(MADRID).strftime('%Y-%m-%d') if dt else ''
        t = datetime.fromisoformat(m['time']).astimezone(MADRID).strftime('%H:%M') if m.get('time') else ''
        status_map = {'FullTime':'finished','Abandoned':'abandoned','PreMatch':'scheduled'}
        status = status_map.get(m.get('status'), 'in_progress' if m.get('status') in ('Live','InPlay','FirstHalf','SecondHalf','HalfTime','ExtraTime','PenaltyShootout') else str(m.get('status') or 'unknown').lower())
        fulltime = status == 'finished'
        rows.append({
            'round': rnd,
            'official_match_id': m.get('id',''),
            'date_local_madrid': local_date,
            'kickoff_local_madrid': t,
            'home_team': m['home_team']['nickname'],
            'home_goals': m.get('home_score') if fulltime else '',
            'away_goals': m.get('away_score') if fulltime else '',
            'away_team': m['away_team']['nickname'],
            'status': status,
            'official_match_slug': m.get('slug',''),
            'official_round_url': url,
        })
rows.sort(key=lambda r:(r['round'],r['date_local_madrid'],r['kickoff_local_madrid'],r['official_match_id']))
fields=list(rows[0])
with OUT.open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
print(f'Wrote {len(rows)} official fixtures from {BASE.format(1)} … {BASE.format(38)} to {OUT}')
