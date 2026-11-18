# Material evidence, limitations and source audit

This is a **research candidate catalog**, not a list of pre-approved TellTag ingredients. Nothing in the catalog demonstrates low migration of the completed indicator, or a safe-to-eat claim for the food it accompanies.

## Commercially observed examples

| Candidate | Film examples represented in the app | Evidence |
|---|---|---|
| PET polyester (HOSTAPHAN) | 12–75 µm across listed grades; 23 µm starting example | [Mitsubishi PET films](https://www.m-petfilm.de/en/film-types/surface-modified-films/matt-and-rough-hostaphan-polyester-films/) |
| BOPP (Jindal Bicor HND) | 20, 25, 30 µm | [Jindal BOPP grade](https://www.jindalfilms.com/product-detail/?jpid=1023&jpsomid=1) |
| Regenerated cellulose (NatureFlex NP) | 21, 23, 25, 28, 35, 42 µm | [NatureFlex NP product datasheet](https://stomniumnorengros.blob.core.windows.net/products/P303855/303856_productsheet.pdf) |
| PLA packaging film | 15–40 µm | [Celplast PLA film](https://www.celplast.com/product/enviromet-pla/) |
| LLDPE (DOWLEX 2035 testing) | One test specimen of 30 µm (not minimum) | [DOWLEX 2035 description](https://www.matweb.com/search/datasheettext.aspx?matguid=354f44c4163e4bd981fb5a706a7b25cd) |
| EVOH coextruded barrier | 3–4 µm EVOH sublayer in ~100 µm coextruded structure | [Coextruded EVOH datasheet](https://www.dm-tapes.com/ewExternalFiles/TDS%20-%20DMT-ZGM%20EVOH-100.pdf) |
| Starch, pectin, alginate, carrageenan lab films | Single examples of about 45–55 µm from a research review | [Food film review](https://ift.onlinelibrary.wiley.com/doi/full/10.1111/1750-3841.70737) |
| Acrylic PSA label grade | A supplier describes specific food-label uses; micron thickness *not established* | [HERMA adhesive/label example](https://shop.material.herma.com/product-details/HH17575/) |

The numerical entries above mean **sourced examples**, not universally recommended values, and do not guarantee availability for the specific exact grade. Their suitability to the gas indicator is untested. More literature-backed polymer identities, with unknown thickness, also appear in `materials_catalog.csv`.

## What is NOT verified

- No named polymer has a verified *ammonia or trimethylamine* permeability value here at the stated film conditions. Manufacturer oxygen permeability or water-vapour transmission is NOT interchangeable with it.
- No real gas uptake capacity, humidity-dependent indicator buffering, reaction kinetics, lifetime, calibrated CIE Lab colour, package leakage or chemical migration for the exact TellTag multilayer sticker.
- No evidence that bromocresol purple or any other listed dye is approved for use with food in the proposed position and full construction.
- No universal material 'minimum thickness' or 'standard thickness' across use conditions.
- No sensor response target independent of a specified target food, packaging and independently measured quality endpoint.

## What to take to a laboratory

Export `telltag_v4_material_design.json`, `telltag_v4_material_library.csv`, a simulation curve CSV, your source/uncertainty notes and the original vendor grade datasheets. Ask researchers what grade-specific permeabilities, film chemistry, optical data and regulatory/migration evidence would be needed to construct and validate a legitimate physical/digital twin.
