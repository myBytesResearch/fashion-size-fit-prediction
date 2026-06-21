# Data — Fashion Size-Fit Prediction (verified)

The raw data is **not** committed (`data/raw/` is gitignored): the competition /
Kaggle terms forbid redistribution. The repository reproduces its results from
the data cached locally or via kagglehub. See `LICENSES.md` for the full terms.

This repository uses the **same dataset** as
[`fashion-returns-analysis`](https://github.com/myBytesResearch/fashion-returns-analysis).

## Dataset (verified 2026-06-20)

**Data Mining Cup 2016 — online fashion.** Kaggle slug
`oscarm524/predicting-returns-of-discounted-articles-sales`.

Download (do not commit; gitignored):

```bash
python -c "import kagglehub; print(kagglehub.dataset_download('oscarm524/predicting-returns-of-discounted-articles-sales'))"
```

Typical cache location (as of 2026-06-20):
`~/.cache/kagglehub/datasets/oscarm524/predicting-returns-of-discounted-articles-sales/versions/3`

## Schema (verified)

- File: `orders_train.txt` (176 MB, **`;`-separated**).
- **2,325,165 order line items**, 15 columns:
  `orderID, orderDate, articleID, colorCode, sizeCode, productGroup, quantity,
  price, rrp, voucherID, voucherAmount, customerID, deviceID, paymentMethod,
  returnQuantity`.
- Columns this analysis uses: `orderID, orderDate, articleID, productGroup,
  sizeCode, quantity, returnQuantity, customerID`.

## How a "size bracket" is defined

A **size bracket** is the same `orderID` + `articleID` ordered in **two or more
different `sizeCode` values** — i.e. the customer ordered the same article in
several sizes. A line item counts as *kept* when `returnQuantity < quantity`.
Only brackets where **exactly one** size is kept are a genuine size problem and
therefore addressable by a size recommendation; brackets where nothing is kept
are a product or taste problem a size model cannot fix.

## License note

The concrete dataset license (Data Mining Cup 2016 / Kaggle terms) is documented
in `LICENSES.md`. Treat the data as non-redistributable: it stays local; only the
code and the derived result artifacts are versioned here.
