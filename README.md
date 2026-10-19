# LaLiga EA SPORTS 2026/27 — DIN Mercado dashboard

Standalone mobile-responsive dashboard for Spain's first division. The GitHub Pages site remains in this repository and at the same URL.

## Current verified cut

The dashboard header and validation report are regenerated with the exact cutoff and current final-score counts on each successful run. The season has 380 official fixtures, 38 matchdays and 20 clubs. The LALIGA-declared Rayo Vallecano–Athletic Club abandonment stays scoreless and outside all calculations. Each official final is independently checked against ESPN `STATUS_FULL_TIME`; the official table and the independently recomputed ESPN table must both reconcile to all 20 clubs before publication. Unset official kickoff times stay unset and display as time to be confirmed.

## Sources and validation

- Official matchdays 1–38: [LALIGA results](https://www.laliga.com/laliga-easports/resultados/2026-27/jornada-1).
- Official standings and competition zones: [LALIGA classification](https://www.laliga.com/laliga-easports/clasificacion).
- Independent score feed: [ESPN soccer scoreboard API](https://site.api.espn.com/apis/site/v2/sports/soccer/esp.1/scoreboard).
- `validate_laliga.py` checks 380 unique official fixtures, 10 per round, confirmed-final-only scores, the official standings for all 20 clubs, all final scores against ESPN, and an independently recomputed ESPN table. Any missing result or discrepancy stops the run.

## Automatic refresh

GitHub Actions runs the refresh daily at **06:10 America/Sao_Paulo (09:10 UTC)** and supports manual dispatch. It fetches official fixtures and the official table, independently verifies every finished score and the ESPN-derived table, validates, rebuilds the page with a dynamic cutoff/count, and commits only if every check passes. A failed check leaves the published page unchanged. Deployment updates the existing repository root `index.html`, preserving the current Pages URL.

Equivalent local sequence:

```sh
python3 fetch_official_laliga.py
python3 capture_official_standings.py
python3 capture_espn_laliga.py
LALIGA_CUTOFF="$(TZ=America/Sao_Paulo date '+%Y-%m-%d %H:%M America/Sao_Paulo')" python3 validate_laliga.py
python3 build_laliga_dashboard.py
```

## Deployment target

- Repository: `wildsonfranciscosilva1986-coder/laliga-2026-27-dashboard`
- Branch and path: `main` / repository root `index.html`
- Existing live URL: https://wildsonfranciscosilva1986-coder.github.io/laliga-2026-27-dashboard/

The 1-X-2 projection is descriptive and based on a small early-season home/away sample; it is not a calibrated forecast or betting recommendation.
