### MAR simulations
MAR v3.11 at 35 km over the AIS, run with wind-driven snow scheme switched on and off. 
Forced by CNRM-CM6-1, IPSL-CM6A-LR, MPI-ESM1-2-HR and UKESM1-0-LL (under SSP5-8.5).
Simulations ran by Ch.A.

Model description:
(Amory et al., 2021)
https://doi.org/10.5194/gmd-14-3487-2021

### CMIP6 ensemble
Near-surface air temperature are downloaded from ESGF node (wget scripts for loading from the node live in the open repository called 'drifting_snow'
Scenarios loaded: SSP1-2.6, SSP2-4.5, SSP3-7.0, SSP5-8.5. 
Outputs are not in this repository, therefore some scripts run on cache (description inside the notebook)
Acknowledgment: I thank M.Ménégoz, M.Santolaria-Otín and M.Chekki for providing me this data

### Drainage basins
IMBIE2 basin definitions v1.6 (`ANT_Basins_IMBIE2_v1.6`).
loaded from https://imbie.org/

### MAR grid
`MARcst-AN35km-176x148.cdf2`

### Scripts
Each notebook contains comments before each cell on how to run it and what is reproduced.

- `plot_multiproj` — the main script written by Charles Amory. Defines dictionaries, opens files, and plots time series (SMB, SU, relative ablation, surface ablation components, ablation area, runoff area, melt area, erosion area). The following calculations in other notebooks are adapted from this script. 
- `main` - figures used in the main and extended data
- `exceedance` - runs on cache not to load ssp data
 
### Environment
channels: [conda-forge]
dependencies:
  - python=3.11
  - numpy
  - pandas
  - matplotlib
  - scipy
  - xarray
  - netcdf4
  - geopandas
  - shapely
  - pyproj
  - jupyterlab

### Authors
Charles Amory, Vincent Favier, María Santolaria-Otín, Daria Kan 
