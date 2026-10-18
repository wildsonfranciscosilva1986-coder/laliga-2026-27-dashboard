#!/usr/bin/env python3
"""Capture the official overall table and competition-zone labels from LALIGA."""
import csv,json,requests
from bs4 import BeautifulSoup
from pathlib import Path
ROOT=Path(__file__).resolve().parent
URL='https://www.laliga.com/laliga-easports/clasificacion'
r=requests.get(URL,timeout=30,headers={'User-Agent':'Mozilla/5.0 LaLigaDashboard/1.0'});r.raise_for_status()
s=BeautifulSoup(r.text,'html.parser'); node=s.find('script',id='__NEXT_DATA__')
if not node or not node.string: raise RuntimeError('No official table payload')
p=json.loads(node.string)['props']['pageProps']
rows=[]
for x in p['standings']:
 rows.append({'position':x['position'],'team':x['team']['nickname'],'played':x['played'],'won':x['won'],'drawn':x['drawn'],'lost':x['lost'],'goals_for':x['goals_for'],'goals_against':x['goals_against'],'goal_difference':x['goal_difference'],'points':x['points'],'competition_zone':(x.get('qualify') or {}).get('name','')})
with (ROOT/'laliga_2026_27_official_table_snapshot.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
# preserve exact zone metadata from page in a small JSON file
(ROOT/'laliga_2026_27_official_zones.json').write_text(json.dumps({'source':URL,'zones':p['standingsDefaultColors'],'teams':rows},ensure_ascii=False,indent=2),encoding='utf-8')
print('Saved',len(rows),'official table rows from',URL)
