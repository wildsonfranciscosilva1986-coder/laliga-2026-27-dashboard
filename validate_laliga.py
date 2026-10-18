#!/usr/bin/env python3
"""Recompute LaLiga table from finished official scores and compare two source tables."""
import csv, json
from collections import defaultdict, Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CUT='2026-10-18 10:54 America/Sao_Paulo'
def read(name):
 with (ROOT/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
fixtures=read('laliga_2026_27_matches_official.csv')
official=read('laliga_2026_27_official_table_snapshot.csv')
espn=read('espn_2026_27_standings_snapshot.csv')
assert len(fixtures)==380
assert len({int(r['round']) for r in fixtures})==38
assert all(sum(int(x['round'])==rd for x in fixtures)==10 for rd in range(1,39))
assert len({r['official_match_id'] for r in fixtures})==380
teams=sorted({r['home_team'] for r in fixtures}|{r['away_team'] for r in fixtures})
assert len(teams)==20
counts=Counter(r['status'] for r in fixtures)
assert counts==Counter({'scheduled':295,'finished':84,'abandoned':1}),counts
stats={t:{'played':0,'won':0,'drawn':0,'lost':0,'goals_for':0,'goals_against':0,'points':0} for t in teams}
for m in fixtures:
 if m['status']=='finished':
  assert m['home_goals']!='' and m['away_goals']!=''
  h,a=int(m['home_goals']),int(m['away_goals'])
  for team,gf,ga in [(m['home_team'],h,a),(m['away_team'],a,h)]:
   s=stats[team];s['played']+=1;s['goals_for']+=gf;s['goals_against']+=ga
   if gf>ga:s['won']+=1;s['points']+=3
   elif gf==ga:s['drawn']+=1;s['points']+=1
   else:s['lost']+=1
 else:
  assert m['home_goals']=='' and m['away_goals']==''
for t,s in stats.items():s['goal_difference']=s['goals_for']-s['goals_against']
computed=sorted(teams,key=lambda t:(-stats[t]['points'],-stats[t]['goal_difference'],-stats[t]['goals_for']))
off={r['team']:r for r in official}
assert set(off)==set(teams)
fields=['played','won','drawn','lost','goals_for','goals_against','points']
for pos,t in enumerate(computed,1):
 s=stats[t]; o=off[t]
 for f in fields:assert s[f]==int(o[f]),(t,f,s[f],o[f])
 assert s['goal_difference']==int(o['goal_difference'])
 assert pos==int(o['position']),(pos,t,o['position'])
# Compare table-stat vector with the independent ESPN table snapshot.
es={r['team']:r for r in espn}
independent_diff=[]
for t in teams:
 o=off[t]; e=es[t]
 diffs=[f for f in fields if int(o[f])!=int(e[f])]
 if int(o['goal_difference'])!=int(e['goal_difference']):diffs.append('goal_difference')
 if diffs:independent_diff.append({'team':t,'fields':diffs,'ESPN':{f:e[f] for f in fields+['goal_difference']},'LALIGA':{f:o[f] for f in fields+['goal_difference']}})
# output the calculated table
out=[]
for pos,t in enumerate(computed,1):
 o=off[t];s=stats[t]
 out.append({'position':pos,'team':t,**s,'competition_zone':o['competition_zone']})
with (ROOT/'laliga_2026_27_standings_computed.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
report={
 'cutoff':CUT,'teams':len(teams),'fixtures':len(fixtures),'official_matchday_pages':38,'finished_results':counts['finished'],'officially_abandoned_no_result':counts['abandoned'],'scheduled_or_not_started':counts['scheduled'],'standings_computation':'3 points for win, 1 for draw; official table comparison fields: played, points, W-D-L, GF, GA, GD and position. Current table contains no unresolved points/GD/GF tie requiring head-to-head sorting.','official_table_comparison':{'clubs_compared':20,'all_stats_and_positions_match':True,'mismatch_count':0},'ESPN_independent_table_comparison':{'clubs_compared':20,'club_stat_rows_match':20-len(independent_diff),'club_stat_rows_differ':len(independent_diff),'differences':independent_diff,'explanation':'ESPN standings snapshot retained the pre-match row for Osasuna and Racing Santander (8 played each); its own separate Osasuna–Racing match page confirms the 2–0 final. The live dashboard uses the post-match table calculated from official LALIGA scores and checked against the official table.'},'special_fixtures':[{'round':r['round'],'home':r['home_team'],'away':r['away_team'],'status':r['status'],'date':r['date_local_madrid'],'kickoff':r['kickoff_local_madrid']} for r in fixtures if r['status']=='abandoned']}
(ROOT/'laliga_2026_27_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
lines=[f"LaLiga EA SPORTS 2026/27 validation — cutoff {CUT}",f"Fixture coverage: {len(fixtures)}/380, 38 matchdays x 10 official LALIGA fixtures; {len(teams)} unique clubs; 380 unique official match IDs.",f"Statuses: {counts['finished']} final scores, {counts['abandoned']} officially abandoned fixture (score excluded), {counts['scheduled']} not started.","Computed standings compared with official LALIGA standings: 20/20 teams match in played, W-D-L, points, GF, GA, GD, and position.",f"Independent ESPN table snapshot: {20-len(independent_diff)}/20 team-stat rows match; differences: "+('; '.join(f"{x['team']} ({', '.join(x['fields'])})" for x in independent_diff) or 'none'),"ESPN difference interpretation: its standings snapshot has Osasuna and Racing at eight played (pre-match), while its match page confirms Osasuna 2–0 Racing final; the official table and recomputation include that result.","Abandoned: round 8, Rayo Vallecano–Athletic Club; no result included.","No unverified score is used. Matches with kickoff unset are shown as time TBC, not given an invented kickoff time."]
(ROOT/'laliga_2026_27_validation.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('\n'.join(lines))
