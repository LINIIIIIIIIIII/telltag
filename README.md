# TellTag V7 — Multi-food Research + Cost Simulator

**This is a scientific research aid, not a calibrated digital twin, a food-safety test, a chemical fabrication recipe, or a quote for manufacturing.**

V7 keeps the detailed V6 design controls and adds scientifically distinct **beef, vacuum-packed chicken, and salmon** study references, food-specific indicator evidence, a visual food-and-sticker playback, and an editable **CAD cost-per-label model**.

## Run on a Mac

1. Extract the ZIP, open the `telltag_simulator_v7` folder in VS Code.
2. Open **Terminal → New Terminal** and enter:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open http://localhost:8501. If an older version is already running, stop it with Control+C before starting V7.

## What to do

1. **01 Live simulator:** Select Beef, Chicken, or Salmon in the left sidebar; select an indicator in the layer builder; adjust film thicknesses, effective gas transport, indicator assumptions, package barrier, humidity scenario, and dry formulation. Watch the study timeline and illustrative sticker colour. The 2025 salmon-specific probe and dual-dye systems **do not receive false one-pKa colour curves**.
2. **02 Price per sticker:** Input your actual material prices and manufacturing costs, if you have supplier quotations. All starter prices are DEMONSTRATION assumptions. Compare costs for batches of 1,000 to 1,000,000 labels. Film price is assumed proportional to thickness around your user-specified quoted-gauge anchor; real supplier prices may differ. Inspect dye loading, costs, and a retailer shrink break-even *scenario*.
3. **03 Compare:** Save settings, change one value and compare the calculated response curves.
4. **04 Evidence:** See study-measured food endpoints, their sources, and which indicator studies actually match each food type.
5. **05 Export:** Download a PDF research summary, a plain-English explanation, machine-readable CSV/JSON, or the complete package.

## What is measured vs estimated

| Quantity | Evidence status |
|---|---|
| Beef TVB-N and bacterial counts | Measured study points, 4°C; between points interpolated |
| Vacuum-packed chicken TVB-N and tissue pH | Measured study points, 4°C; separate sensory study endpoint at day 13 |
| Salmon TVB-N | **Only day 0 and day 10** endpoints in this dataset; any connecting line is illustrative |
| Salmon-specific methylglyoxal, benzyl alcohol and acetic acid | Recent published *candidate* biomarkers; not measured by the default amine-film model |
| Chicken bromocresol purple response | Direct studies exist, but not for TellTag's exact material or packaging |
| Fish bromocresol purple / cresol red | Study evidence for fish; not calibration for the selected salmon package |
| Package headspace gas ppm | **User-assumed hypothetical bridge** from measured food TVB-N (or bacterial trend for beef) |
| Sticker colour over time | **Uncalibrated** single-pKa what-if calculation for simple dyes; visual blending only |
| Sticker chemistry for dual dye / natural pigment / selective probe | Study reference only, **no quantitative V7 predicted response** |
| CAD manufacturing cost | Scenario based on entered area, thickness, prices, pigment fraction, yield, labour, QC and batch size; **not a vendor quote** |

Do not treat the simulator's apparent dye midpoint as a spoilage or safety threshold. Neither a positive nor a negative colour reading would prove pathogens absent.

## Cost formula (editable and auditable)

- Membrane film CAD = sticker area m² × specified film CAD/m² at a reference thickness × (chosen thickness / reference thickness). This last factor is a **simplified procurement assumption**.
- Coating dry mass (g) = sticker area m² × coating thickness m × assumed dry density kg/m³ × 1000.
- Pigment mass (g) = dry mass × entered pigment fraction. Polymer and plasticizer masses are calculated from entered dry mixture fractions.
- Variable cost includes membrane, viewing film, edge adhesive, polymer, plasticizer, dye, printing, assembly and individual packaging. Divide by `(1 - scrap_fraction)` for expected cost per good label.
- Fixed batch setup and QA costs are divided by finished batch size. The sum yields the scenario CAD per finished label.
- Retail shrink model estimates the *fraction of currently wasted packs* that would need to be recovered for break-even **if** each recovery earns only gross margin. It is not a prediction of recovered packs, and cannot bypass date-label laws.

## Safety / IP / regulatory notes

- Food-contact status is specific to the complete finished product, production process, migration exposure and intended regulatory jurisdiction. Do not interpret a listed polymer or natural pigment as automatically safe for the finished sticker.
- Do not use the simulation to decide whether perishable foods are safe to eat or extend use-by dates.
- Lab experiments involving reagents, food spoilage, microbiology or gas atmospheres should be performed only in a qualified, supervised lab.
- No manufacturing price has been verified; get vendor quotes before using a projected sticker cost as an investment thesis.

## Sources

**Food studies**

- Beef loin at 4°C: https://www.mdpi.com/2304-8158/14/23/4017
- Vacuum chicken breast at 4°C: https://pmc.ncbi.nlm.nih.gov/articles/PMC13298445/
- Salmon TVB-N endpoints: https://pmc.ncbi.nlm.nih.gov/articles/PMC5756197/
- Salmon volatile biomarker research: https://pubmed.ncbi.nlm.nih.gov/41267257/

**Indicator research**

- Fish BCP + cresol red: https://pmc.ncbi.nlm.nih.gov/articles/PMC10177749/
- Chicken BCP: https://pmc.ncbi.nlm.nih.gov/articles/PMC6049484/
- Chicken BCP + methyl red: https://www.mdpi.com/2304-8158/11/21/3533
- Salmon amine probe: https://www.sciencedirect.com/science/article/pii/S0003267025009195

**Project market research**

- Telltag original Google Drive research: https://docs.google.com/document/d/1v-j2m8XzQJ_ZYsamB4C42fHiN5FoeD3-knU2Pbxo2c4/edit
- Market data in that report are dated by source, have assumptions about pack weights and margins, and must not be treated as current supplier quotes. In particular, its 2008 and 2016 manufacturing estimates are **not** a verified 2026 production price for TellTag.

## Run tests

```bash
python -m unittest discover -p 'test_*.py'
```
