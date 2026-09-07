#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Surface ablation as a percentage of precipitation over the Antarctic Ice Sheet.

Evolution over 1980-2100 of the three ablation terms, expressed relative to the
precipitation simulated without wind-driven snow (P = SF + RF), for grounded ice and
ice shelves separately:

    snow transport or wind-driven snow or drifting snow 100 * (P_nDS - (SF_DS + RF_DS - ER_DS)) / P_nDS
    runoff               100 * RU_DS / P_nDS
    surface sublimation  100 * SU_DS / P_nDS

Curves are the mean over four MAR simulations forced by UKESM1-0-LL, CNRM-CM6-1,
MPI-ESM1-2-HR and IPSL-CM6A-LR; shading is +/- 1.64 standard deviations.

Input files, read from DATA_DIR:
    MARcst-AN35km-176x148.cdf2
    year-MAR-nDS_{UKM,CNRM,MPI,IPL}-1980-2100.nc
    year-MAR-DS_{UKM,CNRM,MPI,IPL}-1980-2100.nc

Extracted from plot_multiproj.py (C. Amory).
"""

import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import xarray as xr
from matplotlib import ticker as mticker

DATA_DIR = Path(os.environ.get("MAR_DATA_DIR", "data"))
CST_FILE = DATA_DIR / "MARcst-AN35km-176x148.cdf2"
OUT_FILE = Path("ablation_mean.png")

MODELS = ["UKM", "CNRM", "MPI", "IPL"]
YEARS = pd.date_range("1980-01-01", "2100-01-01", freq="YS")
RESOLUTION = 35000  # m, MAR grid spacing

COMPONENTS = {
    "Snow transport": "lightsteelblue",
    "Runoff": "navy",
    "Surface sublimation": "slategrey",
}
REGIONS = {"grd": ("Grounded ice", (-7, 22.5)), "shelf": ("Ice shelves", (-70, 225))}


def preprocess(ds):
    """Select the ice-sheet sector (SECTOR=1)."""
    try:
        ds = ds.sel(SECTOR=1)
        ds = ds.sel(SECTOR1_1=1)
    except (KeyError, ValueError):
        pass
    try:
        ds = ds.sel(SECTOR1_1=1)
    except (KeyError, ValueError):
        pass
    try:
        ds = ds.rename_dims({"x": "X", "y": "Y"})
    except ValueError:
        pass
    return ds


def load_masks(path=CST_FILE):
    """Grounded-ice and ice-shelf masks, weighted by ice fraction."""
    cst = xr.open_dataset(path, decode_times=False, engine="netcdf4")
    ais = cst["AIS"].where(cst["AIS"] > 0)
    grd = cst["GROUND"].where(cst["GROUND"] > 30)
    shf = cst["ICE"].where((cst["ICE"] > 30) & (cst["GROUND"] < 50) & (cst["ROCK"] < 30))
    return {"grd": ais * grd * cst["AREA"] / 100, "shelf": shf * cst["AREA"] / 100}


def open_mar(run, model):
    """Open one annual MAR output file; run is 'nDS' (no drifting snow) or 'DS'."""
    path = DATA_DIR / f"year-MAR-{run}_{model}-1980-2100.nc"
    ds = xr.open_mfdataset(str(path), decode_times=False, preprocess=preprocess, engine="netcdf4")
    ds["TIME"] = YEARS
    return ds


def integrate(ds, variables, mask):
    """Spatially integrate SMB components over the masked area, in Gt yr-1."""
    factor = RESOLUTION**2 / 1e12
    return {
        var: ((ds[var] * mask.values).sum(dim=["X", "Y"]) * factor).to_series()
        for var in variables
    }


def relative_ablation(ref, drift, mask):
    """Ablation components of the drifting-snow run, in % of the no-drift precipitation."""
    nds = integrate(ref, ["SF", "RF"], mask)
    ds = integrate(drift, ["SF", "RF", "ER", "RU", "SU"], mask)
    precip = nds["SF"] + nds["RF"]
    return pd.DataFrame(
        {
            "Snow transport": (precip - (ds["SF"] + ds["RF"] - ds["ER"])) / precip * 100,
            "Runoff": ds["RU"] / precip * 100,
            "Surface sublimation": ds["SU"] / precip * 100,
        }
    )


def ensemble_stats(tables):
    """Multi-model mean and standard deviation of each ablation component."""
    stats = {}
    for component in COMPONENTS:
        df = pd.DataFrame({model: table[component] for model, table in tables.items()})
        stats[component] = (df.mean(axis=1), df.std(axis=1))
    return stats


def plot(stats, out_file=OUT_FILE):
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 4))

    for ax, (region, (title, ylim)) in zip(axes, REGIONS.items()):
        for component, color in COMPONENTS.items():
            mean, std = stats[region][component]
            mean.plot(ax=ax, color=color, label=component)
            ax.fill_between(YEARS, mean + 1.64 * std, mean - 1.64 * std, color=color, alpha=0.2)

        ax.set_title(title, fontsize=18)
        ax.set_ylim(*ylim)
        ax.set_xlabel("", fontsize=5)
        ax.axhline(color="black", alpha=1, lw=1)
        ax.tick_params(axis="x", labelsize=14)
        ax.tick_params(axis="y", labelsize=14)
        ax.yaxis.set_minor_locator(mticker.AutoMinorLocator(n=2))
        ax.tick_params(axis="y", which="major", direction="inout", left=True, right=False)
        ax.tick_params(axis="y", which="minor", direction="in", left=True, right=False)
        ax.tick_params(axis="x", which="major", direction="inout", top=False, bottom=True)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)

    axes[0].set_ylabel("Surface ablation (% of precip.)", fontsize=14)
    axes[1].set_ylabel("")
    axes[1].legend(frameon=False, prop={"size": 16}, loc="upper left")

    fig.tight_layout()
    fig.savefig(out_file, format="PNG", dpi=200)
    return fig


def main():
    masks = load_masks()
    runs = {run: {model: open_mar(run, model) for model in MODELS} for run in ("nDS", "DS")}

    stats = {}
    for region, mask in masks.items():
        tables = {
            model: relative_ablation(runs["nDS"][model], runs["DS"][model], mask)
            for model in MODELS
        }
        stats[region] = ensemble_stats(tables)

    plot(stats)
    plt.show()


if __name__ == "__main__":
    main()
