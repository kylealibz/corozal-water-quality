# Data sources and reuse

## Supplied coursework material

The local WaterQuality folder contains `Corozal_WaterQuality.ppkx`, the `DissolvedO2` point shapefile, the `Bay` polygon shapefile, symbology and an Esri task. These were supplied for a University of Belize GIS exercise. They are inputs to the project, not observations collected by the portfolio author.

The dissolved-oxygen fields used were `SampleDate`, `MeasureVal`, `Unit` and point geometry. `Depth` was reviewed, but the requested monthly analysis applied no depth threshold.

## What the saved metadata says

- The shapefiles declare WGS 84 / UTM zone 18N (EPSG:32618). The local analysis projected them to WGS 84 / UTM zone 16N (EPSG:32616).
- The dissolved-oxygen metadata retains processing references to a `Chesapeake_WaterQuality` package. It does not provide a clear redistribution licence for the point dataset.
- The bay metadata retains descriptions of U.S. counties and other source products. It contains Esri Data and Maps redistribution language permitting certain uses with source attribution, but its relation to this adapted bay geometry is unclear.
- Those records do not establish an independently verified geographic or licensing history for the complete teaching dataset.

No claim is made here that the original monitoring locations, dates, measurements or coastline have been independently validated for Corozal Bay.

## Public-repository scope

This repository includes original processing code, a GitHub-rendered workflow, documentation, selected numerical summaries, synthetic test cases and static map previews. It does **not** distribute:

- Original or filtered sampling records and station coordinates.
- Shapefiles, file geodatabases, raster surfaces or derived GeoJSON polygons.
- The supplied project package, symbology, task files or teaching instructions.
- Editable data-bearing ArcGIS projects or PDF map files.
- Local computer paths, account identifiers, credentials or private ArcGIS item links.

The README's PNG preview shows the completed dissolved-oxygen coursework product using the supplied data, with a source caption. No separate flood-analysis artifact is included in this water-quality repository.

This rendered preview does not establish permission to redistribute the underlying datasets. Its inclusion does not resolve the mixed metadata described above, or grant a new licence to the geographic content. The repository's MIT licence does not cover third-party data depicted in the preview. Do not extract, repackage or treat the map as independently verified monitoring data.

The earlier standalone workflow illustration is retained in `docs/workflow-illustration.svg` as a documentation asset. It is no longer used as the README banner.

## Software and code

The analysis uses Esri ArcGIS Pro and ArcPy. Spatial Analyst is required for IDW and raster masking. This repository's MIT licence covers its original code and documentation only; Esri software and excluded third-party material retain their respective terms.
