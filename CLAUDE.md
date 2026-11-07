# South Dakota Eats (sd-eats) — notes for Claude Code sessions

Built 2026-11-06 by a side session for Nick's "build the 17 states left" (group: MN, IA, NE, ND, SD), ported from `../mn-eats/` (one
city's open inspection scores and on-sale licenses, as Minneapolis's are there) with every fix through 11-05 (the exact-outline county
lookup, the out-of-county truck rule, the per-state ZIP check, the delivery-only brands, the website blocklist and `link_blocklist.py`,
the Share link `Links.site + explore/#p=<id>`, OTA data, the adult-venue rules) and this group's own (the Rusty Nail rule, the site
merge that kept the latest score, the port-leftover QA checks). Local only: git-ignored data, no repo, no remote, nothing published.
Sources: `playbook/12-sources.md`. Brand: `playbook/05-naming.md` — **final**, Nick's decision of 2026-11-07, as built ("South Dakota Eats:
Restaurants", Home Screen "SD Eats"; the chislic icon; Black Hills pine #1E4D3B, Badlands clay #A4472E, sun gold #F2B51C fill only; thin
Badlands strata as the header).

## South Dakota is different
- **No Google data at all**: the UCSD snapshot is never downloaded; `listings.py` builds an empty Google table and the keep rule is the
  family's (Meta 0.95, or 0.90 with a website), calibrated against the City of Sioux Falls' list.
- **Two inspection systems, never blended.** The City of Sioux Falls inspects inside city limits and publishes each site's two most
  recent scores (0-100) as open data, CC BY 4.0 (`fetch_official.py`, `official.py`: "Restaurant Sites", MapServer/17, never OwnerName).
  Sioux Falls places show the City's own scores, dated, not labeled routine or follow-up (the layer doesn't say), with the City's list
  linked. The Department of Health inspects the rest of the state; its reports are search-only, so every other place links its search.
  No grade of ours, scores are never the default order, and inspections are one page among the guides.
- **Alcohol:** only Sioux Falls' "Alcohol and Video Lottery Licensing" layer (on-sale or on- and off-sale, joined to the food site at its
  address when the names agree); elsewhere "Serves alcohol" is "—", never "no". License codes are shown as the City writes them.
- **Counties and regions:** 66 counties; six detail files (Sioux Falls, Southeast, Northeast, Central & Missouri River, Black Hills, West
  River & Badlands). `fetch_overture.py` checks the border towns (Sioux Falls, North Sioux City, Brandon, Elk Point, Yankton, Lemmon,
  Spearfish, Belle Fourche and Rapid City in; Sioux City and Akron IA, Pipestone and Luverne MN, Hankinson ND, Sundance WY, Valentine and
  South Sioux City NE out). The app's outline (`LocationService.swift`) cuts the neighbours' land back out.
- **Venues:** the Sioux Falls and Rapid City airports, the Denny Sanford PREMIER Center and the W.H. Lyon Fairgrounds (Sioux Falls),
  The Monument (Rapid City); stores with food counters (Casey's, 7-Eleven, Hy-Vee, Sunshine Foods, Lewis Drug, Get-N-Go and others) are
  hidden with the non-restaurants.
- **Adult venues:** standalone clubs by address in `data/research/adult_venues.json` (Belle Starr, Kongo Klub, Scarlett O'Hara's, South
  Fork Lounge); Yankton's Cockatoo Club shares blocks with restaurants, so it's left to the 150 m name rule. not_adult: "Heavy Metal
  Strippers and Body Shop" (Aberdeen), a paint-stripping and body shop.
- **Guides** (tags in `southdakota.py` TAGS; bits 1, 2, 4): chislic (13, Sioux Falls, Rapid City and Brookings), bison and walleye (14,
  Rapid City), oldest (founded at the address by 1960; only The Pheasant, 1949, so its card and page wait for three/four). Sources in
  `pipeline/build_research.py` (Experience Sioux Falls, Visit Rapid City, the James Beard Foundation), each note checked against what its
  page says (2026-11-06); a street number pins a place where the source's own listing gives one. Leads in `data/research/app/LEADS.md`
  (Chislic Circle, kuchen, frybread, Wall Drug's café).
- **Honors:** no MICHELIN Guide covers South Dakota. James Beard: America's Classic The Pheasant (2024); semifinalists Hjem A.M. (2026)
  and Skogen Kitchen (2025) in Custer, BibiSol and CH Patisserie (2025) in Sioux Falls.

## Rebuild
```bash
cd pipeline
../.venv/bin/python check_sources.py URL...   # a new host first
../.venv/bin/python fetch_overture.py && ../.venv/bin/python fetch_extras.py && ../.venv/bin/python fetch_official.py
../.venv/bin/python geocode_official.py && ../.venv/bin/python geocode_census.py && ../.venv/bin/python listings.py
../.venv/bin/python calibrate.py && ../.venv/bin/python southdakota.py && ../.venv/bin/python build_research.py && ../.venv/bin/python southdakota.py
SD_APP=1 ../.venv/bin/python southdakota.py && cd .. && cp data/app/places.json data/app/detail-*.json SouthDakotaEats/Resources/
.venv/bin/python pipeline/check_websites.py && .venv/bin/python pipeline/check_websites.py --retry-transient   # then re-export
.venv/bin/python scripts/make-site.py && .venv/bin/python scripts/publish_app_data.py && .venv/bin/python scripts/publish_app_data.py --check
.venv/bin/python scripts/qa-site.py --static
```
`data/chain_auv.json` is a copy of wy-eats'. The `.venv` is on the python.org framework Python 3.12 with the family's versions.

## App, site, screenshots
- App: `SouthDakotaEats/` (XcodeGen `project.yml`, bundle `com.southdakotaeats.ios`, display "SD Eats"), tests in
  `SouthDakotaEatsTests/` (a 13-place South Dakota fixture; data guards: adult venues, blocklisted and multi-URL websites, bad and legal
  names, non-restaurants, listed twice, no Google data, Sioux Falls-only scores and on-sale licenses, The Rusty Nail kept) and
  `SouthDakotaEatsUITests/`. Build and test only with Xcode 1.app (27.2, 27B52); Xcode.app is a beta. Run `xcodegen generate` whenever
  `Resources/*.json` changes.
- Site: `scripts/make-site.py` writes `docs/` and `playbook/site-numbers.json`; `scripts/explore.js` is the web app; `scripts/qa-site.py`
  the QA. Site URL for now: nickstrom5.github.io/south-dakota-eats (no CNAME). City pages: Sioux Falls, Rapid City (MIN_LISTED 3).
- Screenshots: `scripts/capture-screenshots.sh <sim>` (ScreenshotMode pins downtown Sioux Falls; downtown Rapid City for bison and
  walleye, Brookings for The Pheasant's detail), then `scripts/site-images.sh`, then make-site + qa-site. App Store frames:
  `scripts/appstore-screenshots.py`. Listing: `playbook/app-store/listing.json`. Icons: `scripts/icon-concepts.swift`,
  `scripts/make-brand.swift`.

## Status
See the end of this file (written when the build finished).

### Status (2026-11-07 02:30)
- **Ready to publish; nothing public.** No repo, commit, push, Pages, App Store Connect record or
  build upload; all of those wait for Nick's yes.
- Data: 2,132 restaurants (2,276 places) in 234 towns; 21 hand-checked guide places (13 chislic, 14 bison and walleye), 5 James Beard
  honorees; 489 places with the City of Sioux Falls' own scores (inspections through 2026-10-29); 204 with a Sioux Falls on-sale license;
  every website link checked (1,724 links; 1,096 places keep one in the app).
- Tests (Xcode 1.app 27.2, iOS 27.0): iPad 13" (M5) 49 unit + 6 UI tests passed (the launch-time test skips itself under load).
  iPhone 17 Pro Max: UI tests passed; 2 unit tests first failed on fixture expectations (a fixture place in a region with no fixture
  detail file; search lists name matches before street matches), both fixed, and all 49 then passed on iPhone (2026-11-07 02:07) as on
  iPad. The iPad home shot was retaken after the title learned to shrink to fit ("SOUTH DAKOTA EA…" before).
- Site: `docs/` generated; `qa-site.py --static` and the full headless-Chrome run both OK. `publish_app_data.py --check` OK.
- App Store: 7 iPhone and 5 iPad frames in `playbook/app-store/`; `listing.json` (South Dakota Eats: Restaurants; Chislic, Bison &
  Walleye; support and privacy on nickstrom5.github.io/south-dakota-eats/).
- Brand final (Nick, 2026-11-07): name, chislic icon and palette, as built. A Department of Health records request is being drafted by
  the parent session.
