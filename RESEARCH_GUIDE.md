# TellTag V3 — Research & decision guide

**Status: exploratory scientific software, not a validated food-quality indicator or digital twin.** Every model prediction is conditional on assumptions. Do not use predicted colour as a food-consumption decision, and do not test or expose substances or deteriorating food outside a qualified supervised laboratory.

## 1. What the program calculates

1. The user supplies *one* hypothetical gas-phase basic vapour concentration profile, or optionally uploads laboratory-measured **headspace gas (ppm by volume) versus time (hours)**.
2. The code adds series gas transport resistances through two sensing layers and, in outside-package mode, an illustrative package barrier.
3. The code calculates reversible gas uptake by a lumped single-gas model.
4. It applies a simplified, **unvalidated** gas uptake → apparent pH proxy.
5. It applies an ideal acid/base dye fraction equation to estimate how the chemical form changes.
6. The preview blends two RGB colours; it does **not** predict real colour spectra, print permanence, UV ageing or consumer interpretation.

The current design is **not** a chemistry-formulation engine. It cannot predict arbitrary dye/polymer combinations or the food microbiome from a picture.

## 2. The key questions, in their correct order

**A. What is the product claim?** "Tracks a *quality marker* associated with deterioration under specified storage conditions" is a much narrower and more scientifically feasible claim than "detects dangerous food." Pathogens can occur without a detectable spoilage signal.

**B. What food is targeted?** Specify species, form (whole/ground), initial microbial load and processing, package gas composition, packaging barrier, initial freshness, temperature history and consumer use setting.

**C. What independent quality endpoint defines a true warning?** A university food scientist should specify an accepted, food-specific and method-specific quality endpoint, combining sensory, chemical and/or microbiological measurements as appropriate. Do not choose the simulator's 50%-dye crossing as a food cutoff.

**D. What *measured gas-phase marker* tracks that endpoint?** For example, the relationship between headspace amine concentration and the actual measured food-quality endpoint must be established for that food/package configuration. Solution mg/L, fish TVB-N mg nitrogen/100g, and gas ppm are *different quantities* and may not be substituted.

**E. Can the sticker recognize that marker selectively?** Assess response to other naturally occurring food volatiles, humidity, temperature, film ageing, package leakage, and printing/adhesive variations.

**F. Is the response interpretable?** The observable film colour transition must be unambiguous under normal viewing conditions, lighting and colour-vision variations; define a measurement protocol and metric such as ΔE00 using actual optical measurements, not blended hex codes.

## 3. Time requirements: no universal number

- **Food quality time:** elapsed time when an *independently measured* quality limit is met. Depends on food, processing, packaging, conditions and definition.
- **Marker appearance:** time when a specified gas-phase marker crosses a *measured* concentration; can occur before or after other quality changes.
- **Sticker response time:** time from a defined change in actual gas exposure to a measurable film response under matched conditions. Different tests may specify t50 or t90 (fraction of *actual measured* optical change).
- **Warning time:** when a consumer could consistently identify the agreed warning colour.
- **Allowable delay:** should be chosen after distributions of actual food-quality times and sensor response times have been measured. Include a margin for variance and uncertainty, and quantify missed detections.

**Warning example (arithmetic only):** If a separately measured quality endpoint were at hour 48 and a research team wanted a 6-hour lead, an illustrative warning objective would be hour 42. This is not a genuine TellTag requirement. V3's Food reality tab performs this arithmetic and explicitly does NOT infer when food spoils.

## 4. Different meanings of 'cutoff'

| Term | Unit | What it means | Can V3 establish it? |
|---|---|---|---|
| Food-quality criterion | Food-specific, e.g. mg nitrogen/100g fish | Independently justified accept/reject *quality* criterion | No |
| Headspace gas level | ppm(v), ppb(v) | Gas exposure in package | Only user-supplied; not inferred from meat |
| Sensor detection limit | ppm(v) with noise definition | Smallest gas concentration distinguishable from blank in a specified test | No |
| Film colour criterion | Measured ΔE00 or calibrated category | When a human/device can distinguish the warning | No; V3's colour is illustrative |
| Model 50% dye threshold | % basic chemical form | Arbitrary midpoint of mathematical dye equilibrium | Yes, but NOT a freshness decision |
| Prediction uncertainty | Value and confidence/coverage | How well forecasts match new experiments | No, until held-out tests |

## 5. Contextual facts you CAN cite

- **Health Canada** gives general refrigerator-storage recommendations at 4°C or below: raw beef and pork ~2–4 days, ground meat ~1–2, poultry pieces ~2–3 and raw finfish such as cod/salmon ~3–4. These are broad storage recommendations, not measured spoilage onset times and not a guaranteed package lifespan. See https://www.canada.ca/en/health-canada/services/general-food-safety-tips/safe-food-storage.html
- **EU Regulation 2019/627** includes TVB-N categories of **25, 30, 35 mg nitrogen per 100g of fish flesh** for certain defined fish groups, alongside organoleptic freshness concerns. Different species groups have different limits. These are NOT gas-phase ppm cutoffs or universal meat standards. See https://eur-lex.europa.eu/legal-content/en/TXT/?uri=CELEX:32019R0627
- **FAO** cautions that TVB-N may be more useful later in spoilage and can fail as an early freshness marker in some seafood. See https://www.fao.org/4/v7180e/v7180e09.htm
- **A 2024 meat spoilage review** found no single chemical indicator that reliably measures deterioration for all meats/conditions. See https://pmc.ncbi.nlm.nih.gov/articles/PMC11394942/
- **Kim, Park & Shin 2023** measured colour response of a different fish indicator system. Its *aqueous ammonia standard solution mg/L* exposure cannot be read as headspace ppm and is not directly a TellTag calibration. https://doi.org/10.3390/foods12091801
- **Health Canada packaging** explains food-contact material safety obligations and voluntary assessment routes; performance alone is insufficient for product readiness. https://www.canada.ca/en/health-canada/services/food-nutrition/food-safety/packaging-materials.html

## 6. Exact meaning of each V3 result

| On screen | Correct interpretation | Incorrect interpretation |
|---|---|---|
| Basic dye fraction, 90% | Simplified model fraction of one idealized dye form | 90% of meat is spoiled |
| 50% crossing at 17 h | Time mathematical curve crosses arbitrary 50% reference under user-provided gas | Meat is unsafe at 17 h |
| Apparent pH | Model's assumed gas uptake proxy, not a measured film pH | Actual polymer's true pH |
| Colour swatch | RGB illustration determined by modeled dye fraction | Proof of visible lab colour |
| Packaging placement | Adds hypothetical series transport resistance | Correct sealed packaging permeability |
| Food image | Drawing only | Genuine fish/chicken/beef spoilage simulation |
| ±25% sensitivity | Hypothetical change of one model parameter | 95% confidence interval |
| Lab MAE/RMSE | Error when comparing *truly measured same-quantity* matched values | Proof of validation unless the data were independent |

## 7. What must be in a university laboratory dataset

- Study ID, date, researcher, specimen description, sample and batch ID, material identity and construction, package type and conditions.
- For each recorded point: time since packaging, environmental temperature and relative humidity, actual measured headspace identity and concentration (unit specified), sensor's measured optical response (same instrument/setup), independently measured food quality information (lab-chosen method), and measurement uncertainty.
- Independent batches and a held-out experiment set for validation. Include negative controls and cases likely to generate false alerts or missed warnings as designed by qualified researchers.
- Protocol, instrument calibration notes, lab ethics and safety compliance. No uncontrolled at-home chemical/food deterioration experiments.

**Practical limitation:** V3's direct basic-dye-fraction comparison only works if a lab can actually measure that quantity. Most optical measurements are **ΔE**, not chemically derived fractions; do not upload ΔE as a basic-fraction measurement. A proper spectrum-to-speciation model must be calibrated first.

## 8. Priority development phases

1. **Now:** Learn to interpret the simulator; vary one parameter at a time; export design and curves; identify which unmeasured parameters dominate.
2. **With university:** Narrow to one food/product, select quality endpoint, gather paired gas/food-quality/film data with supervised facilities.
3. **Next software phase:** Fit and validate temperature/humidity-aware transport and calibrated film optical response using independent data (units and identifiability checked).
4. **Later:** Expand to multigas interactions only if evidence supports it; evaluate film drift, selectivity, packaging conditions, manufacturing variability, durability and consumer interpretation.
5. **Before product launch:** Assess food-contact migration, claims, applicable standards, label interpretation, false-negative risk and regulatory review.

## 9. Known scientific weaknesses that cannot be fixed by extra UI

- Effective film permeabilities and sorption coefficients are default **illustrative** numbers, not measured properties of a specified gas/material pair.
- The gas-to-pH step is an arbitrary monotonic proxy; no full acid/base balance, water absorption or chemical binding model.
- No temperature, humidity, microbial growth, multigas or actual degradation kinetics.
- The colour swatch is not colorimetry; no film spectra or sensor visual detection threshold.
- External sealed-package permeability is a placeholder and may be the dominant obstacle.
- Published paper uses different formulations and exposure methods. Its curves cannot validate this TellTag model.
- No independent test set, calibration, false-negative/false-positive statistics or product stability evidence.

**Strongest recommended first target:** a research-grade indicator for one clearly specified food/package system, not a universal food-safety sticker. The selection of that food and endpoint should be made with a qualified food scientist based on available measurement capability and actual market needs.

---

## 10. V3.1 research update — published deterioration measurements

The new **Food datasets** tab contains **actual published food measurements**, not fabricated food-spoilage curves. Values are recorded in CSV with a source URL, measurement type, units, storage temperature and package context.

### A. Beef loin in a sealed polyethylene-film tray, 4°C

Source: Lim et al., *Foods* (2025), Table 3–4: https://www.mdpi.com/2304-8158/14/23/4017

- Total bacterial count rose from **3.00 log CFU/g (day 0)** to **6.92 (day 6)** and **8.64 (day 10)**.
- TVB-N in the beef rose from **7.00 mg/100g (day 0)** to **14.40 mg/100g (day 6)** and **23.80 mg/100g (day 10)**.
- In the study, reaching **7 log CFU/g** by interpolation occurred near **day 6.11**, while reaching **20 mg/100g TVB-N** occurred near **day 8.64**. These are *study-specific research benchmarks*, not universal safety law or proof meat is pathogen-free until that time.
- **Dimethylamine** was reported in the headspace-related analysis by day 2; **methylamine** and **trimethylamine** were reported later, on day 8 and day 10. The paper's values are **µg/kg**, not gas-phase ppm(v). Non-detects are **not zero**.
- The study drew from one carcass and particular package design; performance cannot be generalized to food types or TellTag as a physical sticker.

### B. Vacuum-packaged chicken breast, 4°C

Source: *Foods* (2026), Table 1 and sensory findings: https://www.mdpi.com/2304-8158/15/12/2162

- TVB-N was **10.65 mg N/100 g at day 0**, **15.80 at day 7**, **20.80 at day 13**, **23.20 at day 15**.
- Authors reported sensory rejection under **their experimental vacuum-packaging conditions** around day 13, with a total count around **6.79 log CFU/g**. **This is not a safe-storage recommendation.** Health Canada’s consumer recommendation for raw poultry at 4°C or colder is generally **2–3 days**. Do not substitute study conditions for consumer guidance.

### C. Salmon fillets stored at 4°C

Source: *Food and Bioprocess Technology* (2017): https://pmc.ncbi.nlm.nih.gov/articles/PMC5756197/

- The paper explicitly reports a starting TVB-N around **14.32 mg/100g** and a value **45.99 mg/100g at day 10** at 4°C. The data tab includes only these exact reported numbers; it does not invent intermediate measurements.
- Salmon deteriorated more rapidly at 4°C than 0°C according to the study’s sensory and physicochemical comparisons.

### D. Another research film on beef and fish

Source: *Open Veterinary Journal* (2025), Tables 2–3: https://pmc.ncbi.nlm.nih.gov/articles/PMC12124793/

- A different indicator film was measured at days 3, 6, 9 and 12 at 4°C. Its measured colour difference (ΔE) did not always increase smoothly. The CSV preserves that behaviour.
- Film colour ΔE is NOT the percentage of basic-form dye, and cannot be fed into the lab-compare basic fraction tool as if these were the same units.

### E. General recommended storage and regulated limits

- Health Canada chart: https://www.canada.ca/en/health-canada/services/general-food-safety-tips/safe-food-storage.html — raw beef/pork 2–4 d; ground meat 1–2 d; poultry 2–3 d; cod/salmon 3–4 d at 4°C or colder. **Guidance is not spoilage kinetics.**
- European Commission Implementing Regulation (EU) 2019/627: https://eur-lex.europa.eu/eli/reg_impl/2019/627/oj — TVB-N limits of 25/30/35 mg nitrogen per 100g flesh apply to named *fishery categories* in the specified official-control setting. **These are not universal thresholds for every species, meat product or headspace gas.**
- Meat spoilage chemical overview: https://pmc.ncbi.nlm.nih.gov/articles/PMC11394942/ — spoilage markers differ by food, storage atmosphere, microorganism population and temperature.

### F. What is still missing, and why we are not faking it

Published meat TVB-N and microbial counts **do not give your chosen individual sticker film its correct local gas concentration**. The missing chain is **food quality ⇢ measured gas species in package ⇢ measured permeability and uptake in specified TellTag films ⇢ actual calibrated colour response**. Those links must be established with appropriately supervised analytical and materials testing. Do not use the V3.1 model’s 50% dye fraction as a food safety cutoff.

## 11. How to compare one simulated formulation with another

- Save an initial run in **Compare runs**.
- Change only one setting in **Sticker builder**. Return to **Compare runs**.
- Read both the changed-setting list and the explanation of the direction of the model difference.
- Export the comparison and the current run’s configuration + curves. Save all supporting experimental inputs separately.

A saved experiment persists only during the current Streamlit browser session. It is not a permanent laboratory log. **Changing the food illustration cannot create a meat-spoilage calculation**, and choosing multiple changes prevents a clear causal interpretation of the simulation results.
