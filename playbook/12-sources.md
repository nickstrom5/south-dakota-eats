# South Dakota sources and calibration (checked 2026-11-06)

## Official sources
| Source | What it has | Can a script read it? | Used |
|---|---|---|---|
| City of Sioux Falls "Restaurant Sites" (gis.siouxfalls.gov/arcgis/rest/services/Data/Safety/MapServer/17; ArcGIS item 67d60bc7760a4b3988f18685fd9898f6) | 1,046 food-service sites inside city limits (restaurants, bars, food facilities, schools, casinos, groceries, mobile stands), each with the City's two most recent inspection scores (SCORE1/2, 0-100) and dates; monthly | yes; CC BY 4.0 ("City of Sioux Falls open data") | yes: 489 places show the City's own two most recent scores, dated, inspections through 2026-10-29; the layer doesn't say which visit was routine and which a follow-up, so neither is labeled |
| City of Sioux Falls "Alcohol and Video Lottery Licensing" (Data/Community/MapServer/20; item f60df5268f3241e691789a6a33fe406b) | 1,015 licenses: license code (RB, RW, RL, PL, PD, RR, CL, A-RL), on- or off-sale, status | yes; CC BY 4.0 | yes: 204 Sioux Falls places show "Serves alcohol" (an on-sale or on- and off-sale license joined to the food site at its address when the names agree). Owner names are never read. The codes are shown as the City writes them, not decoded |
| City of Sioux Falls inspection list (sweepsdata.siouxfalls.gov/Restaurants.aspx) | the same sites, with each inspection's violations | pages | linked from every Sioux Falls place with a score |
| South Dakota Department of Health inspection search (sddoh.safefoodinspection.com/Inspection/publicinspectionsearch.aspx) | every inspection outside Sioux Falls, one PDF each, two years | search-only (an ASP.NET postback) | linked from every other place; no PDF harvesting, and an export request or records request is Nick's call |
| Sioux Falls "Grocery Sites" (MapServer/18) | groceries | yes | no: not restaurants |
| Statewide alcohol licenses | none: cities and counties license retailers, and dor.sd.gov has no list | — | "Serves alcohol" is unknown (never "no") outside Sioux Falls |

- Two inspection systems, each scoring out of 100. They are never blended, and no grade of ours is computed. Rapid City's restaurants
  look state-inspected (per the prompt; rcgov.org answers scripts with 403), so they link the Department of Health's search.
- Places on tribal lands may be under a tribal food program; the app and site say so where they explain inspections, and never call a
  place "unlicensed".
- Calibration (pipeline/calibrate.py, against the City of Sioux Falls' list, 981 listings in the city): Meta high-confidence listings
  matched the City's list 83% of the time, Meta middling ones with a website 61%, the rest 17-50%. The keep rule is the family's (Meta
  0.95, or 0.90 with a website). No Google data is read anywhere.

## Honors
- No MICHELIN Guide covers South Dakota (guide.michelin.com/us/en/south-dakota/restaurants answered 404 in September 2026).
- James Beard Foundation (jamesbeard.org): America's Classics 2024, The Pheasant Restaurant and Lounge, Brookings (opened 1949 as a gas
  station café, per the Foundation); semifinalists Hjem A.M. (Camillia and Erik Hjortnaes, Best Chef: Midwest 2026) and Skogen Kitchen
  (Joseph Raney, Best Chef: Midwest 2025) in Custer, BibiSol (Marcela Salas, Emerging Chef 2025) and CH Patisserie (Chris Hanmer,
  Outstanding Pastry Chef or Baker 2025) in Sioux Falls. Older honors (Sanaa's 2023 nominee, M.B. Haskett 2022) are left out, as in the
  family's other states (2025-26 finalists and semifinalists only).

## Guide sources
- South Dakota Codified Laws § 1-6-16.10 (SL 2018, ch 7): "Chislic is hereby designated as the official nosh of South Dakota"
  (sdlegislature.gov, read 2026-11-06): the app's "the state nosh".
- Experience Sioux Falls, "Where to get the best chislic" (published 2020-06-19, updated 2026-02-26): The Alibi, The Barrel House, The
  Attic Bar & Grill, Gateway Lounge (3408 Gateway Blvd; Overture's "Gateway Casino & Lounge"), Ode to Food & Drinks, Tinner's Public
  House (449 W 69th St, not Tinner's Northstar). Addresses from the bureau's own listings.
- Visit Rapid City, "Popular South Dakota foods you have to try and where to find them" (published 2024-10-29, updated 2025-05-22):
  chislic, bison and walleye places; The Wine Cellar (513 6th Street), Enigma at the Rushmore Hotel (445 Mount Rushmore Road) and
  Thirsty's (819 Main Street) checked on the bureau's own listings.
- The James Beard Foundation's 2024 America's Classics announcement (The Pheasant's chislic, lamb from a local ranch).
- Leads (Chislic Circle, kuchen, frybread, Wall Drug's café) wait for a dated 2025-26 source: data/research/app/LEADS.md.

## Counts
- App: 2,276 places, 2,132 restaurants in 234 towns; 21 hand-checked guide places (13 chislic, 14 bison and walleye), 5 honorees.
- Pipeline web export (site/): 3,022 places, 2,852 restaurants.
- Overture: 4,302 eating and drinking listings, 181 of them marked closed.
- Casey's, the grocery counters and the casinos' food stands are hidden with the non-restaurants. Whether they appear is Nick's call.

## Research hosts (check_sources.py)
- **Usable (robots.txt allows Claude):** experiencesiouxfalls.com, visitrapidcity.com, visitbrookingssd.com, blackhillsbadlands.com,
  southdakotamagazine.com, siouxfalls.business, tastingtable.com, jamesbeard.org; rapidcityjournal.com too, though nothing here cites
  it.
- **Blocked by robots.txt:** argusleader.com, keloland.com, dakotanewsnow.com, sdpb.org, southdakotasearchlight.com,
  mitchellrepublic.com, yankton.net, aberdeennews.com, brookingsregister.com, capjournal.com.
- **Other:** travelsouthdakota.com answers with a bot check. The visitor bureaus' listing pages draw their text in the browser; each
  listing's own fields sit in the page's embedded data, read by script.
