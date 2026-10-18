# LaLiga EA SPORTS 2026/27 — DIN Mercado dashboard

Standalone, mobile-responsive dashboard for the Spanish first division only. Public GitHub repository and Pages site are separate from every other league project.

## Sources

- **Official LALIGA fixtures/results:** [Round 1](https://www.laliga.com/laliga-easports/resultados/2026-27/jornada-1) through [Round 38](https://www.laliga.com/laliga-easports/resultados/2026-27/jornada-38). The feed provides 380 official match IDs and match status.
- **Official LALIGA classification and zone legend:** [Official table](https://www.laliga.com/laliga-easports/clasificacion).
- **Independent standings check:** [ESPN Spanish LALIGA table 2026/27](https://www.espn.com/soccer/standings/_/league/esp.1), captured at 10:56 BRT on 18 October. The embedded standings table still had Osasuna and Racing at eight played. ESPN's separate [Osasuna–Racing match report](https://www.espn.com/soccer/match/_/gameId/401882840) confirms the 2–0 final. Both the recomputed table and the LALIGA table include that result; its effect is the only two-team row difference in the ESPN standings snapshot.

## Cutoff and coverage

Cutoff requested: **18 October 2026, 10:54 America/Sao_Paulo**. The dashboard contains all 380 official schedule slots across 38 matchdays and 20 clubs: 84 finished fixtures with confirmed scores, 295 not started, and one official abandonment. `Rayo Vallecano–Athletic Club` (matchday 8) is identified as abandoned by LALIGA; it has no score in the data and is excluded from every calculation. Officially unset kickoffs are shown as time to be confirmed. The `laliga_2026_27_matches_official.csv` file includes the round source URL and official fixture ID for each entry.

## Validation and update path

The public site is deployed from **`main` branch / repository root** via GitHub Pages. A daily/manual refresh, when separately authorized and after the matches are over, should update only these LaLiga files and publish by committing them to the same repository:

```sh
python3 fetch_official_laliga.py
python3 capture_official_standings.py
python3 validate_laliga.py
python3 build_laliga_dashboard.py
```

Then commit the changed LaLiga CSV/validation snapshot and rebuilt `index.html` to `main` at the repository root; GitHub Pages automatically redeploys that root. **No cron or scheduled job has been created.** Do not update any other league's repository/files as part of this path. Check that the LALIGA result/table pages have closed matches and refreshed standings before publishing.

`validate_laliga.py` recomputes the table only from `finished` scores and validates the result against the official table. At the cutoff all 20 clubs match the LALIGA table in played, W-D-L, points, goals for/against, goal difference and position. Compared with the independent ESPN table snapshot, 18/20 club-stat rows match; the two exceptions are Osasuna and Racing because ESPN's table had not yet included their independently confirmed 2–0 result. No unverified or inferred score is used.

Install `requirements.txt` only if the official-source fetch scripts need dependencies; the dashboard build and validation scripts use the Python standard library. The refresh process should also preserve the `laliga_2026_27_matches_official.csv` file and update the validation snapshots/notes before rebuilding.

**Exact deployment/update target:** `wildsonfranciscosilva1986-coder/laliga-2026-27-dashboard` → branch `main` → root `index.html` → GitHub Pages.
**Live site:** https://wildsonfranciscosilva1986-coder.github.io/laliga-2026-27-dashboard/

## Dashboard features

- Overview KPIs: 20 clubs; 84 confirmed finals / 380 official fixtures; goals and per-final average; BTTS and over-2.5 counts, denominators and rates; home wins/draws/away wins; leader and next fixture.
- Full 380-slot fixture register with round selector, club/jornada search, status and result labels, and direct LALIGA round-source links. The abandoned fixture is retained as a no-score status and excluded from calculations.
- Table with the current official LALIGA Europe/relegation legend: places 1–5 Champions League, 6 Europa League, 7 Conference League, 18–20 relegation.
- Team selector: last five finals, full home/away split, next officially scheduled fixture.
- Selectable home/away matchup: season head-to-head, transparent simple 1-X-2 and score projection, expected goals, modal score, BTTS and over 2.5.
- Top five by points, goals for, goals conceded (best defence), wins, draws, losses, BTTS and over 2.5; overall/home/away cuts and rate denominators.
- Source notes, cutoff, calculation rules and limitations.

The projection is a small-sample descriptive model based on team home/away scoring and conceding averages with independent Poisson goal counts. It is not a calibrated forecast or betting recommendation. No injuries, lineup, opponent-strength, market odds or squad adjustment is used.
