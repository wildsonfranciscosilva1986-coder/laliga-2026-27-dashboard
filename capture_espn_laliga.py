#!/usr/bin/env python3
"""Independently cross-check all official LALIGA finals and recompute an ESPN table.

Only ESPN STATUS_FULL_TIME events are used. Any missing or different official final
stops the refresh before the dashboard can be built or committed.
"""
from __future__ import annotations
import csv, json, re, unicodedata
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parent
FIXTURES=ROOT/'laliga_2026_27_matches_official.csv'
SCORES=ROOT/'laliga_2026_27_espn_result_crosscheck.csv'
TABLE=ROOT/'espn_2026_27_standings_snapshot.csv'
REPORT=ROOT/'laliga_2026_27_espn_crosscheck.json'
ENDPOINT='https://site.api.espn.com/apis/site/v2/sports/soccer/esp.1/scoreboard'

def norm(value):
    value=unicodedata.normalize('NFKD',value or '').encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+',' ',value).strip()

def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

fixtures=read_csv(FIXTURES)
clubs=sorted({r['home_team'] for r in fixtures}|{r['away_team'] for r in fixtures})
alias={norm(t):t for t in clubs}
for provider,official in {
    'atletico madrid':'Atlético de Madrid','atletico de madrid':'Atlético de Madrid',
    'osasuna':'CA Osasuna','celta vigo':'Celta','deportivo alaves':'Deportivo Alavés','alaves':'Deportivo Alavés',
    'elche':'Elche CF','barcelona':'FC Barcelona','getafe':'Getafe CF','levante':'Levante UD','malaga':'Málaga CF',
    'racing santander':'R. Racing Club','racing de santander':'R. Racing Club','real racing club':'R. Racing Club',
    'deportivo la coruna':'RC Deportivo','deportivo de la coruna':'RC Deportivo','deportivo':'RC Deportivo','espanyol':'RCD Espanyol de Barcelona',
    'espanyol barcelona':'RCD Espanyol de Barcelona','rayo vallecano':'Rayo Vallecano','real betis':'Real Betis',
    'real madrid':'Real Madrid','real sociedad':'Real Sociedad','sevilla':'Sevilla FC','valencia':'Valencia CF','villarreal':'Villarreal CF',
}.items():
    if official in clubs:alias[norm(provider)]=official

dates=set()
for row in fixtures:
    if row['status']=='finished':
        day=datetime.strptime(row['date_local_madrid'],'%Y-%m-%d').date()
        for delta in (-1,0,1):dates.add((day+timedelta(days=delta)).strftime('%Y%m%d'))

events={};queried=[]
for day in sorted(dates):
    url=ENDPOINT+'?'+urlencode({'dates':day})
    req=Request(url,headers={'User-Agent':'Mozilla/5.0 DINMercadoDashboardRefresh/1.0','Accept':'application/json'})
    with urlopen(req,timeout=35) as response:payload=json.loads(response.read())
    queried.append(url)
    for event in payload.get('events',[]):
        comp=event.get('competitions',[{}])[0]
        teams={x.get('homeAway'):x for x in comp.get('competitors',[])}
        home,away=teams.get('home',{}),teams.get('away',{})
        hn=alias.get(norm(home.get('team',{}).get('displayName','')))
        an=alias.get(norm(away.get('team',{}).get('displayName','')))
        if not hn or not an:continue
        key=(hn,an)
        rec={'event_id':event.get('id',''),'status':comp.get('status',{}).get('type',{}).get('name',''),
             'home_goals':str(home.get('score','')),'away_goals':str(away.get('score','')),'url':url}
        if key not in events or (rec['status']=='STATUS_FULL_TIME' and events[key]['status']!='STATUS_FULL_TIME'):
            events[key]=rec

cross=[];missing=[];mismatches=[]
for row in fixtures:
    if row['status']!='finished':continue
    event=events.get((row['home_team'],row['away_team']))
    if not event:
        missing.append({'round':row['round'],'home':row['home_team'],'away':row['away_team'],'date':row['date_local_madrid']})
        continue
    same=(event['status']=='STATUS_FULL_TIME' and str(event['home_goals'])==str(row['home_goals']) and str(event['away_goals'])==str(row['away_goals']))
    result={'official_match_id':row['official_match_id'],'round':row['round'],'date_local_madrid':row['date_local_madrid'],
            'home_team':row['home_team'],'official_home_goals':row['home_goals'],'espn_home_goals':event['home_goals'],
            'away_team':row['away_team'],'official_away_goals':row['away_goals'],'espn_away_goals':event['away_goals'],
            'espn_status':event['status'],'result_match':str(same),'espn_event_id':event['event_id'],'espn_source_url':event['url']}
    cross.append(result)
    if not same:mismatches.append(result)
if missing or mismatches:
    raise RuntimeError(json.dumps({'missing':missing,'mismatches':mismatches},ensure_ascii=False,indent=2))
fields=list(cross[0]) if cross else ['official_match_id','round','date_local_madrid','home_team','official_home_goals','espn_home_goals','away_team','official_away_goals','espn_away_goals','espn_status','result_match','espn_event_id','espn_source_url']
with SCORES.open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(cross)

# Recompute a table from ESPN's own independently confirmed scores.
stats={t:{'played':0,'won':0,'drawn':0,'lost':0,'goals_for':0,'goals_against':0,'goal_difference':0,'points':0} for t in clubs}
for row in cross:
    hg,ag=int(row['espn_home_goals']),int(row['espn_away_goals'])
    for team,gf,ga in ((row['home_team'],hg,ag),(row['away_team'],ag,hg)):
        s=stats[team];s['played']+=1;s['goals_for']+=gf;s['goals_against']+=ga
        if gf>ga:s['won']+=1;s['points']+=3
        elif gf==ga:s['drawn']+=1;s['points']+=1
        else:s['lost']+=1
for s in stats.values():s['goal_difference']=s['goals_for']-s['goals_against']
ordered=sorted(clubs,key=lambda t:(-stats[t]['points'],-stats[t]['goal_difference'],-stats[t]['goals_for'],t))
with TABLE.open('w',encoding='utf-8-sig',newline='') as f:
    cols=['position','team','played','won','drawn','lost','goals_for','goals_against','goal_difference','points']
    w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
    for pos,team in enumerate(ordered,1):w.writerow({'position':pos,'team':team,**stats[team]})
report={'source':'ESPN independent soccer scoreboard API','endpoint':ENDPOINT,'official_final_scores':len(cross),
        'exact_STATUS_FULL_TIME_matches':sum(r['result_match']=='True' for r in cross),'missing':missing,'mismatches':mismatches,
        'queried_scoreboard_urls':len(queried),'espn_table_recomputed_for_clubs':len(ordered),'result':'PASS'}
REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
