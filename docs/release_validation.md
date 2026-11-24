# Release validation

Checked on 24 November 2026.

## Tests without the teaching data

Seven Python standard-library unit tests passed. They cover the June date boundaries, time of day, repeated coordinates, nearby-but-unequal coordinates, invalid dates, null/nonfinite/negative observations, other years and month rollover. All test records are synthetic.

Python source files compiled successfully. The repository's JSON files and SVG workflow illustration parsed successfully.

## Local end-to-end reproduction

The public `build_water_quality.py` script was executed with the original authorized local coursework inputs in a licensed ArcGIS Pro 3.7 environment with Spatial Analyst. The generated spatial data, project and maps remain local.

| Check | Result |
|---|---:|
| Selected June records | 170 |
| Valid records used | 170 |
| Unique projected locations | 114 |
| Raster cells outside the bay mask | 0 |
| Broken map layers | 0 |
| Raster minimum | 2.66302847862244 mg/L |
| Raster maximum | 9.81248474121094 mg/L |

The record and location counts match the completed coursework run. The raster range also matches the saved original raster statistics. The public script produced a separate project, PNG, PDF and validation summary without modifying the source project or publishing an online layer.

These are workflow and output-integrity checks. They do not establish the accuracy, ecological meaning or geographic provenance of the supplied observations.

## Publication check

The tracked files were reviewed for supplied datasets, derived geographic data, private account links, machine-specific paths and credentials. None is included. The GitHub Actions workflow runs the synthetic checks only; it cannot run ArcPy on the hosted Ubuntu runner.
