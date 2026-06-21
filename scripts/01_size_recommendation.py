"""Fashion size-fit — size recommendation for multi-size (bracketed) orders.

The mechanism, honestly:
  Many customers order the SAME article in several sizes ("size bracketing"),
  keep one, return the rest. If we could tell them the right size up front, they
  order one size -> the extra returns vanish. BUT only brackets where exactly ONE
  size is kept are a size problem; brackets where nothing is kept are a
  product/taste problem a size model cannot fix.

Leak-free TEMPORAL split. The recommender learns each customer's typical kept
size per product group from PAST orders only, falls back to the article's most-
kept size, then a global default. We measure:
  - hit rate: recommended size == the size actually kept (addressable brackets)
  - captured avoidable returns as a share of ALL returns (the honest reduction,
    not a vendor "25 %" claim).

Outputs: results/size_metrics.json, figures/size_recommender.png (DE canonical).
"""

from __future__ import annotations

import glob
import json
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
FIG = REPO / "figures"; RES = REPO / "results"
FIG.mkdir(exist_ok=True); RES.mkdir(exist_ok=True)


def find_orders() -> str:
    for pat in [str(REPO / "data/raw/*.txt"),
                str(Path.home() / ".cache/kagglehub/**/orders_train.txt")]:
        hits = sorted(glob.glob(pat, recursive=True))
        if hits:
            return hits[0]
    raise FileNotFoundError("orders_train.txt not found")


def modal_map(df, keys, val="sizeCode"):
    """Most frequent kept size per key-tuple (kept rows only)."""
    k = df.groupby(keys)[val].agg(lambda s: Counter(s).most_common(1)[0][0])
    return k.to_dict()


def main() -> None:
    cols = ["orderID", "orderDate", "articleID", "productGroup", "sizeCode",
            "quantity", "returnQuantity", "customerID"]
    df = pd.read_csv(find_orders(), sep=";", usecols=cols)
    df["orderDate"] = pd.to_datetime(df["orderDate"], errors="coerce")
    df = df.dropna(subset=["orderDate"]).sort_values("orderDate").reset_index(drop=True)
    df["kept"] = (df["returnQuantity"] < df["quantity"]).astype(int)
    df["ret"] = (df["returnQuantity"] > 0).astype(int)

    cut = int(len(df) * 0.75)
    tr, te = df.iloc[:cut], df.iloc[cut:]

    # learn recommenders from TRAIN (kept rows only) -> leak-free
    kept_tr = tr[tr["kept"] == 1]
    cust_pg = modal_map(kept_tr, ["customerID", "productGroup"])
    art_mode = modal_map(kept_tr, ["articleID"])
    global_mode = Counter(kept_tr["sizeCode"]).most_common(1)[0][0]

    def recommend(cust, pg, art, personalized=True):
        if personalized and (cust, pg) in cust_pg:
            return cust_pg[(cust, pg)]
        return art_mode.get(art, global_mode)

    # TEST brackets: same order + article, >=2 sizes
    te_b = te.groupby(["orderID", "articleID"])
    total_test_returns = int(te["ret"].sum())

    rows = []
    for (oid, art), grp in te_b:
        if grp["sizeCode"].nunique() < 2:
            continue
        kept_sizes = grp.loc[grp["kept"] == 1, "sizeCode"].tolist()
        n_items = len(grp)
        ret_items = int(grp["ret"].sum())
        cust = grp["customerID"].iloc[0]; pg = grp["productGroup"].iloc[0]
        rows.append({
            "n_items": n_items, "ret_items": ret_items,
            "n_kept": len(kept_sizes),
            "kept_size": kept_sizes[0] if len(kept_sizes) == 1 else None,
            "rec_pers": recommend(cust, pg, art, True),
            "rec_base": recommend(cust, pg, art, False),
            "has_hist": (cust, pg) in cust_pg,
        })
    b = pd.DataFrame(rows)
    n_brack = len(b)
    addr = b[b["n_kept"] == 1].copy()                      # keep-exactly-1 = addressable
    addr["hit_pers"] = (addr["rec_pers"] == addr["kept_size"]).astype(int)
    addr["hit_base"] = (addr["rec_base"] == addr["kept_size"]).astype(int)

    # avoidable returns = extra ordered sizes in addressable brackets (ret_items - 0,
    # since if only the kept size were ordered the returned extras vanish)
    addr_avoidable = int(addr["ret_items"].sum())
    captured_pers = int(addr.loc[addr["hit_pers"] == 1, "ret_items"].sum())
    captured_base = int(addr.loc[addr["hit_base"] == 1, "ret_items"].sum())

    m = {
        "dataset": "DMC 2016", "test_returns_total": total_test_returns,
        "test_brackets": int(n_brack),
        "bracket_keep_dist": {int(k): round(v, 3) for k, v in
                              b["n_kept"].value_counts(normalize=True).sort_index().head(4).items()},
        "addressable_brackets_keep1": int(len(addr)),
        "coverage_customer_history": round(float(addr["has_hist"].mean()), 3),
        "hit_rate_personalized": round(float(addr["hit_pers"].mean()), 3),
        "hit_rate_article_baseline": round(float(addr["hit_base"].mean()), 3),
        "addressable_returns": addr_avoidable,
        "addressable_share_of_all_returns": round(addr_avoidable / total_test_returns, 4),
        "captured_personalized": captured_pers,
        "reduction_personalized_pct_of_all_returns": round(captured_pers / total_test_returns, 4),
        "reduction_baseline_pct_of_all_returns": round(captured_base / total_test_returns, 4),
    }
    (RES / "size_metrics.json").write_text(json.dumps(m, indent=2))
    print(json.dumps(m, indent=2))

    # ---- figure: mechanism + proof -------------------------------------------
    INK, C1, C2, HI, GREY = "#0a1e2e", "#1f77b4", "#8eb600", "#d63031", "#A6B5C2"
    fig, ax = plt.subplots(1, 3, figsize=(16, 5.2))

    # panel 1: bracket decomposition (why only part is addressable)
    kd = b["n_kept"].value_counts(normalize=True).sort_index()
    labels = {0: "0 behalten\n(kein Größen-\nproblem)", 1: "genau 1 behalten\n(adressierbar)",
              2: "2+ behalten"}
    keys = [k for k in [0, 1, 2] if k in kd.index]
    vals = [kd.get(0, 0), kd.get(1, 0), kd[[k for k in kd.index if k >= 2]].sum()]
    cols_ = [GREY, C2, C1]
    ax[0].bar(range(3), [v * 100 for v in vals], color=cols_)
    ax[0].set_xticks(range(3)); ax[0].set_xticklabels(["0", "genau 1", "2+"])
    for i, v in enumerate(vals):
        ax[0].text(i, v * 100 + 1, f"{v:.0%}", ha="center", fontweight="bold", color=INK)
    ax[0].set_title("Was im Größen-Bracket behalten wird", fontweight="bold", color=INK)
    ax[0].set_ylabel("Anteil der Brackets (%)")
    ax[0].text(0.5, 0.92, "nur „genau 1“ ist per Größe lösbar", transform=ax[0].transAxes,
               ha="center", fontsize=9, color=HI, style="italic")

    # panel 2: hit rate personalized vs baseline
    hp, hb = m["hit_rate_personalized"], m["hit_rate_article_baseline"]
    ax[1].bar(["Artikel-\nBaseline", "personalisiert\n(Kundenhistorie)"], [hb * 100, hp * 100],
              color=[GREY, C2])
    for i, v in enumerate([hb, hp]):
        ax[1].text(i, v * 100 + 1, f"{v:.0%}", ha="center", fontweight="bold", color=INK)
    ax[1].set_title("Trifft die Empfehlung die behaltene Größe?", fontweight="bold", color=INK)
    ax[1].set_ylabel("Trefferquote (%)"); ax[1].set_ylim(0, max(hp, hb) * 130)

    # panel 3: funnel all returns -> addressable -> captured
    tot = m["test_returns_total"]
    fr = [1.0, m["addressable_share_of_all_returns"], m["reduction_personalized_pct_of_all_returns"]]
    flab = ["alle Retouren", "adressierbar\n(Größen-Bracket,\ngenau 1 behalten)",
            "vom Empfehler\neingefangen"]
    ax[2].barh(range(3), [f * 100 for f in fr][::-1], color=[C2, C1, GREY][::-1])
    ax[2].set_yticks(range(3)); ax[2].set_yticklabels(flab[::-1], fontsize=9)
    for i, f in enumerate(fr[::-1]):
        ax[2].text(f * 100 + 1, i, f"{f:.1%}", va="center", fontweight="bold", color=INK)
    ax[2].set_title("Realistische Retouren-Reduktion (Anteil ALLER Retouren)",
                    fontweight="bold", color=INK)
    ax[2].set_xlabel("% aller Retouren"); ax[2].set_xlim(0, 105)
    for a in ax:
        for sp in ("top", "right"):
            a.spines[sp].set_visible(False)

    fig.suptitle("Größen-Empfehlung bei Mehrfachbestellungen — was wirklich drin ist (DMC 2016)",
                 fontsize=13.5, fontweight="bold", color=INK, x=0.02, ha="left")
    fig.text(0.01, 0.005, f"Quelle: DMC 2016, zeitlicher Holdout · {m['addressable_brackets_keep1']:,} "
             f"adressierbare Brackets · Kundenhistorie-Abdeckung {m['coverage_customer_history']:.0%} · "
             f"myBytes", fontsize=8, color="#888")
    fig.tight_layout(rect=(0, 0.04, 1, 0.95))
    fig.savefig(FIG / "size_recommender.png", dpi=150, bbox_inches="tight")
    print("Saved", FIG / "size_recommender.png")


if __name__ == "__main__":
    main()
