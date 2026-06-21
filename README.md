<!--
=============================================================================
                    ____        __
   ____ ___  __  __/ __ )__  __/ /____  _____
  / __ `__ \/ / / / __  / / / / __/ _ \/ ___/
 / / / / / / /_/ / /_/ / /_/ / /_/  __(__  )
/_/ /_/ /_/\__, /_____/\__, /\__/\___/____/
          /____/      /____/

 myBytes.com
 Copyright (c) 2026 myBytes GmbH. All rights reserved.
=============================================================================
-->

# fashion-size-fit-prediction

**Companion repository to the myBytes Research note on fashion returns
prevention — the size-recommendation lever, honestly measured.**

→ Methodology article (German): https://mybytes.com/research/fashion-returns-prevention

---

## Scope

A common vendor claim is that personalised size recommendation cuts returns by
25 %. We tested that mechanism on the **Data Mining Cup 2016** dataset (the same
2.3M real fashion order line items used in
[`fashion-returns-analysis`](https://github.com/myBytesResearch/fashion-returns-analysis)).

The mechanism is real but the lever is smaller than advertised. Customers order
the same article in several sizes ("size bracketing"), keep one, return the rest.
If you could tell them the right size up front, the extra returns vanish — **but
only for brackets where exactly one size is kept**. Brackets where nothing is
kept are a product or taste problem no size model can fix.

## What this repository reproduces

`scripts/01_size_recommendation.py` runs the full analysis on a **leak-free
temporal split** (the recommender learns each customer's typical kept size per
product group from past orders only, falls back to the article's most-kept size,
then a global default). It writes `results/size_metrics.json` and
`figures/size_recommender.png`. The headline numbers (test split):

| Finding | Value |
|---|---|
| Bracket keep distribution | 0 kept **50.5 %**, exactly 1 kept **40.5 %**, 2 kept 7.5 %, 3 kept 1.2 % |
| Addressable brackets (exactly 1 kept) | **17,352** |
| Hit rate, personalised recommender | **28.8 %** |
| Hit rate, article-only baseline | **19.1 %** |
| Addressable share of all returns (ceiling) | **6.9 %** |
| Returns realistically captured (personalised) | **~2.0 %** of all returns |
| Returns captured (baseline) | 1.3 % of all returns |

**The honest conclusion:** personalised size recommendation works — it beats the
article baseline clearly (28.8 % vs 19.1 % hit rate) — but it realistically
captures about **2 % of all returns**, with a hard ceiling near **6.9 %**. The
25 % claim is not reachable with size recommendation alone, because only ~40 % of
size brackets are a size problem at all, and half of all brackets (nothing kept)
are not.

## Quickstart

Prerequisite: Python 3.11 or 3.12, a fresh virtual environment.

```bash
git clone https://github.com/myBytesResearch/fashion-size-fit-prediction.git
cd fashion-size-fit-prediction
pip install -r requirements.txt

# derive your environment file (defaults work)
cp .env.example .env

# fetch the raw data yourself (NOT shipped — see DATA.md / LICENSES.md)
python -c "import kagglehub; print(kagglehub.dataset_download('oscarm524/predicting-returns-of-discounted-articles-sales'))"

# run the analysis
python scripts/01_size_recommendation.py
```

The script auto-discovers the data in the kagglehub cache or under `data/raw/`.

## What this repository does not contain

1. **No data.** Data Mining Cup 2016 is third-party competition data; treat it as
   non-redistributable. You fetch it via `kagglehub`. See
   [`LICENSES.md`](LICENSES.md) and [`DATA.md`](DATA.md).
2. **No body or fit measurements.** The recommender uses purchase and keep/return
   behaviour only, not garment measurements or customer body data. A production
   size-advisor with fit data could do better; this measures what is reachable
   from order data alone.
3. **No causal guarantee.** "If the kept size had been ordered alone, the extra
   returns vanish" is the bracketing logic, not a measured intervention effect.

## Repository layout

```
scripts/    The size-recommendation analysis (leak-free temporal split)
results/    size_metrics.json (committed; the article's numbers)
figures/    size_recommender.png (committed)
data/raw/   You place the fetched data here (gitignored)
DATA.md     Dataset identity, download command, bracket definition
LICENSES.md Code / data / library licensing
```

## Disclaimer

This is methodological research on a public dataset, not legal or business
advice. Rates and assumptions must be checked against your own numbers before any
operational decision.
