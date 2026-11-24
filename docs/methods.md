# Methods and reproducibility

## Completed coursework analysis

1. Open the extracted `Corozal_WaterQuality` project and inspect its point and polygon inputs.
2. Select records with `SampleDate >= 2014-06-01` and `SampleDate < 2014-07-01`. The requested month takes precedence over the different summer period in the supplied task.
3. Project the observations and bay polygon to WGS 84 / UTM zone 16N, so distance and cell-size settings use metres.
4. Group observations by identical projected x/y coordinate pairs. Compute the arithmetic mean of the valid `MeasureVal` values at each location and retain the number of contributing records.
5. Interpolate station means with IDW: power 2, a variable search radius using 12 nearest locations, and 100 m raster cells. Restrict the surface to the supplied bay polygon.
6. Display the masked surface using five classes, add station locations and the bay outline, and create a layout with a title, legend, north arrow, scale bar, author and source note.
7. Save the project and export PNG and PDF layouts. A separate viewing copy was also created in ArcGIS Online during the coursework; its private account links are not published here.

The completed run contained 170 June records at 114 unique locations. Its saved raster minimum and maximum were approximately 2.663 and 9.812 mg/L. These are raster-cell estimates, not the minimum and maximum of the raw observations.

## Choices that affect interpretation

**Depth:** all depths were retained. A station mean can therefore combine records from different depths. It is not a surface-water-only estimate.

**Time:** all valid June observations contribute equally at their station. Sampling frequency and time intervals are not used as weights.

**Location:** grouping uses exact coordinate equality after projection. Nearby but unequal coordinate pairs are separate locations. No tolerance-based clustering or station-ID reconciliation is performed.

**Distance:** IDW uses projected straight-line distance. It does not model currents, shoreline barriers, mixing, travel time or water-column structure.

**Grid:** a 100 m cell size controls raster representation. It does not imply observations every 100 m or 100 m predictive accuracy.

**Display:** the five class intervals are presentation choices. They were not evaluated as ecological thresholds or regulatory categories.

## Public reproduction code

`scripts/prepare_samples.py` contains standard-library filtering and station-mean logic. It rejects invalid dates, null or nonfinite coordinates, and null, nonfinite or negative values. It includes the first day of the month and excludes the first day of the following month.

`scripts/build_water_quality.py` uses that logic in an ArcPy workflow. It requires local authorized inputs and an existing `.aprx` template, validates mg/L units, makes an explicit polygon-mask extraction, and writes results to a new output directory. It saves a separate project rather than modifying the input template. It also checks for raster cells outside the mask and records counts and raster statistics in a JSON summary.

The public version consolidates the original local processing and layout steps. It adds input checks, configurable paths and explicit mask verification. These safeguards can cause it to stop on inputs that the original coursework run did not separately reject. An authorized rerun is required before claiming identical numeric results for another dataset or environment.

## Validation status

The original local analysis and layout were executed in ArcGIS Pro 3.7, and its map was visually inspected. The public reproduction workflow is checked separately before publication; see the repository's release validation note for the executed checks. The standard-library unit tests use synthetic records only. They do not validate the scientific accuracy of IDW, the source data's provenance or the prediction surface.

No withheld-station validation, cross-validation, sensitivity analysis, uncertainty surface or formal ecological classification was completed. These would be useful next steps once the provenance and sampling design are confirmed.
