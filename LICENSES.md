# Licenses - Code, Data, Libraries

This repository ships **code and result artifacts only**. The raw dataset is
**not** included and must be fetched by you from Kaggle. Reading this file is
part of the reproduction procedure.

## 1 · Repository code

**License:** MIT (see `LICENSE`).
You may use, modify, redistribute, and commercialise the code, provided you
preserve the copyright notice. There is no warranty.

## 2 · Data source — read this carefully

### 2.1 Data Mining Cup 2016 (online fashion)

- **Dataset:** Data Mining Cup 2016, originally run by prudsys / Operations
  Research. The version used here is the public Kaggle mirror, slug
  `oscarm524/predicting-returns-of-discounted-articles-sales`. This is the same
  dataset used in the companion repository
  [`fashion-returns-analysis`](https://github.com/myBytesResearch/fashion-returns-analysis).
- **Fetched via:** `kagglehub` (third-party Python package). See `DATA.md` for
  the exact download command and the verified schema.
- **Licensing of the data itself:** this is **third-party competition data**.
  The original Data Mining Cup terms restrict use to the competition context,
  and Kaggle's dataset terms apply on top. **Treat it as non-redistributable.**
  Check the Kaggle dataset page for the specific license the uploader declared
  before any use beyond local, personal research.
- **This repository's posture:** we ship **code only**, never a data snapshot
  (`data/raw/` is gitignored). You download the data yourself under your own
  terms and responsibility.
- **For commercial users:** do not assume a permissive data license. Verify the
  Kaggle dataset terms and the original Data Mining Cup conditions, or run the
  size recommender on your own order data — the method needs no third-party data
  license.

### 2.2 Result artifacts in this repository

The JSON under `results/` and the PNG under `figures/` are our **derived
results** (metrics and plots), not raw data. They are committed so the article's
numbers are inspectable without re-running the pipeline. Republishing your own
derived results is fine; republishing the raw data is not.

## 3 · Python libraries (third-party dependencies)

Each library retains its own license; all listed licenses are permissive and
allow commercial use:

| Library | License | Purpose |
|---|---|---|
| numpy, pandas | BSD-3-Clause | numerical and tabular foundation |
| matplotlib | PSF / BSD-3 | plotting |
| kagglehub | Apache-2.0 | dataset download (data terms apply, see §2.1) |
| python-dotenv | BSD-3 | environment loading |

## 4 · What this means for you, the reader

- **Personal, academic, methodological reproduction:** permitted under the MIT
  license for the code, subject to the Kaggle / Data Mining Cup data terms for
  the dataset (§2.1).
- **Commercial production use:** you may use the code freely; clear the data
  terms yourself or run the recommender on your own order data.
- **Republishing the data:** not permitted. Republishing your derived *results*
  (metrics, plots, articles) is permitted.

If any of this is unclear for your specific use case, consult your own legal
counsel. This file is documentation, not legal advice.
