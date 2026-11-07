# South Dakota Eats: name, icon and palette

**Final: Nick's decision of 2026-11-07 ("Yes, as proposed" on the 17-state review page).**
Name, icon A (chislic) and palette exactly as built.

## Name
- **South Dakota Eats**:
  - App Store name "South Dakota Eats: Restaurants" (30 characters, the limit).
  - Subtitle "Chislic, Bison & Walleye" (24).
  - Home Screen name "SD Eats": "South Dakota Eats" is cut off under the icon.
- Why, per the prompt: it has the best search fit, no App Store app has the name, and the .com was unregistered (the prompt's check, not
  repeated here; check TSDR before filing).
- Alternatives (from the prompt):
  - "SoDak Eats": short, a weaker search fit; the .com was unregistered.
  - "SoDak Table": the .com was unregistered, and no app has it.
- Avoided:
  - "Great Faces. Great Places." (the state slogan) and anything Rushmore (the App Store has "Rushmore: Restaurant Discovery").
  - "…Plates" (southdakotaplates.com sells license plates) and "Dakota Eats" (North Dakota's prompt's pick).
  - Jackrabbits and Coyotes (SDSU, USD), Sturgis Rally marks, Wall Drug.

## Icon (state-prompts/ICON-STYLE.md; all three pass state-prompts/icon-style/check.swift)
- **A, chosen (final): chislic**, four seared cubes in two rows with a toothpick standing in each top one, side elevation. It
  matches the lead guide, and at 60 px it still reads as cubes on toothpicks.
- B: a slice of kuchen (the state dessert): sweet dough, custard and three plum halves. At 60 px it reads as a dessert bar.
- C: an Indian taco on frybread. At 60 px it reads as a layered taco, but frybread isn't a guide yet (see LEADS.md).
- No Mount Rushmore faces, no team or school marks.
- `scripts/icon-concepts.swift` draws all three (playbook/brand/concept-{a,b,c}-1024.png). `scripts/make-brand.swift` makes the app
  icon, favicons, touch icons and og.png from A; make-site.py's LOGO is the same drawing as an inline SVG.

## Palette (the prompt's second palette; North Dakota Eats is blue and red, so the two apps read apart)
| Role | Hex | Contrast |
|---|---|---|
| Titles, tint, honors and oldest cards, icon background | Black Hills pine #1E4D3B | 9.6:1 on white |
| Hand-checked guide cards, chips | Badlands clay #A4472E | white on it 6.0:1 |
| Pins, the title shadow, a header stratum (fill only) | sun gold #F2B51C | #1A1A1A on it 9.5:1; never text on white (1.8:1) |
| Pages | cream #F6F0E4 | |

The prompt's other choice was the flag: sky blue #1F5AA6 on cream with sun gold. SDSU (blue and yellow) and USD (red) are left out.

## Header
One element: thin Badlands strata (clay, sun gold, pale clay, clay, dark clay), each edge dipping a little. North Dakota's header has its
prairie horizon. It appears as Theme.swift's Stripes, make-site.py's RAYS and the band on og.png.
