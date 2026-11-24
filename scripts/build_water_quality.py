"""Reproduce the June 2014 coursework analysis from authorized local inputs.

Run with ArcGIS Pro's Python environment. Nothing is uploaded or downloaded.
"""
import argparse
import json
from pathlib import Path

from prepare_samples import month_bounds, station_means


def rectangle(arcpy, x, y, width, height):
    return arcpy.Polygon(arcpy.Array([
        arcpy.Point(x, y), arcpy.Point(x + width, y),
        arcpy.Point(x + width, y + height), arcpy.Point(x, y + height),
    ]))


def create_layout(arcpy, project, map_, surface, bay_layer, points, output, author,
                  record_count, location_count):
    """Create a separate letter-landscape layout with a fixed 10 km bar."""
    for layout in project.listLayouts():
        project.deleteItem(layout)
    layout = project.createLayout(11, 8.5, 'INCH', 'June 2014 dissolved oxygen')

    def text(x, y, value, size=10, bold=False):
        element = project.createTextElement(
            layout, arcpy.Point(x, y), 'POINT', value, size, 'Arial',
            'Bold' if bold else 'Regular')
        element.setAnchor('TOP_LEFT_CORNER')
        element.elementPositionX, element.elementPositionY = x, y
        return element

    text(.45, 8.15, 'COROZAL BAY', 24, True)
    text(.45, 7.68, 'Dissolved oxygen | June 2014', 15)
    frame = layout.createMapFrame(rectangle(arcpy, .45, 1.0, 6.6, 6.25),
                                  map_, 'Bay map')
    frame.camera.setExtent(arcpy.Describe(bay_layer.dataSource).extent)
    frame.camera.scale *= 1.06
    arrow = layout.createMapSurroundElement(arcpy.Point(6.45, 6.8),
                                            'NORTH_ARROW', frame)
    arrow.elementHeight = .45

    # Ground metres = page inches * 0.0254 * map scale.
    bar_width = 10000 / (.0254 * frame.camera.scale)
    for index in range(2):
        graphic = project.createGraphicElement(
            layout, rectangle(arcpy, .8 + index * bar_width / 2, .6,
                               bar_width / 2, .07), name=f'10 km bar {index}')
        definition = graphic.getDefinition('V3')
        for symbol_layer in definition.graphic.symbol.symbol.symbolLayers:
            if hasattr(symbol_layer, 'color'):
                dark = index == 0 or 'Stroke' in type(symbol_layer).__name__
                symbol_layer.color.values = [0, 0, 0, 100] if dark else [255, 255, 255, 100]
        graphic.setDefinition(definition)
    for x, label in [(.8, '0'), (.8 + bar_width / 2, '5'), (.8 + bar_width, '10 km')]:
        text(x, .92, label, 9)

    legend = layout.createMapSurroundElement(
        rectangle(arcpy, 7.4, 4.6, 3.0, 2.6), 'LEGEND', frame)
    legend.syncNewLayer = False
    for item in list(legend.items):
        if item.name != surface.name:
            legend.removeItem(item)
    definition = legend.getDefinition('V3')
    definition.showTitle = False
    definition.fittingStrategy = 'AdjustFrame'
    for item in definition.items:
        item.showHeading = False
        item.showLayerName = True
        item.labelSymbol.symbol.height = 10
        item.layerNameSymbol.symbol.height = 12
    legend.setDefinition(definition)
    legend.elementPositionX, legend.elementPositionY = 7.4, 7.0

    text(7.4, 4.45, 'MONTHLY ESTIMATE', 11, True)
    text(7.4, 4.12, f'{record_count} valid June records\n{location_count} unique locations')
    text(7.4, 3.5, 'METHOD', 11, True)
    text(7.4, 3.17, 'IDW power 2; 12 nearest locations\n100 m cells; supplied bay mask')
    text(7.4, 2.55, 'Repeated locations averaged.\nAll sampled depths included.\nEstimates between observations.\nNo independent accuracy assessment.', 9)
    text(7.4, 1.35, f'Prepared by {author}', 11, True)
    text(.45, .3, 'Coursework teaching dataset; supplied project name and boundary. Geographic provenance is unverified.', 8)
    text(.45, .15, 'WGS 84 / UTM zone 16N | Not an independently validated monitoring product.', 8)
    project.defaultGeodatabase = str(output / 'June2014.gdb')
    project.saveACopy(str(output / 'Corozal_Bay_June2014.aprx'))
    layout.exportToPDF(str(output / 'Corozal_Bay_June2014.pdf'), resolution=300)
    layout.exportToPNG(str(output / 'Corozal_Bay_June2014.png'), resolution=160)
    return frame.camera.scale


def run(args):
    import arcpy
    import numpy as np

    source, template, output = map(Path, (args.input_folder, args.template_project, args.output_folder))
    if not template.is_file() or template.suffix.lower() != '.aprx':
        raise ValueError('Supply an existing local .aprx template.')
    for name in ('DissolvedO2.shp', 'Bay.shp'):
        if not (source / name).is_file():
            raise ValueError(f'Missing authorized local input: {name}')
    if output.exists() and any(output.iterdir()):
        raise ValueError('Use a new or empty output folder; existing outputs will not be overwritten.')
    if arcpy.CheckExtension('Spatial') not in ('Available', 'CheckedOut'):
        raise RuntimeError('A Spatial Analyst licence is required.')

    output.mkdir(parents=True, exist_ok=True)
    arcpy.CheckOutExtension('Spatial')
    try:
        with arcpy.EnvManager(overwriteOutput=False):
            gdb = str(output / 'June2014.gdb')
            arcpy.management.CreateFileGDB(str(output), 'June2014.gdb')
            projection = arcpy.SpatialReference(32616)
            inputs = str(source / 'DissolvedO2.shp')
            required = {'SampleDate', 'MeasureVal', 'Unit'}
            if not required.issubset({field.name for field in arcpy.ListFields(inputs)}):
                raise ValueError('Sampling input lacks SampleDate, MeasureVal or Unit.')
            for feature in (inputs, str(source / 'Bay.shp')):
                if arcpy.Describe(feature).spatialReference.name == 'Unknown':
                    raise ValueError('Both inputs must have a known coordinate system.')
            bay = gdb + '/Bay'
            arcpy.management.Project(str(source / 'Bay.shp'), bay, projection)
            start, end = month_bounds(2014, 6)
            date_field = arcpy.AddFieldDelimiters(inputs, 'SampleDate')
            expression = f"{date_field} >= date '{start}' AND {date_field} < date '{end}'"
            selected = arcpy.management.MakeFeatureLayer(inputs, 'june_selection', expression)
            june = gdb + '/June_Records'
            arcpy.management.Project(selected, june, projection)
            units = {str(row[0]).strip().upper() for row in arcpy.da.SearchCursor(june, ['Unit'])}
            if units != {'MG/L'}:
                raise ValueError('Expected June observations in MG/L; do not mix or silently convert units.')
            with arcpy.da.SearchCursor(june, ['SampleDate', 'SHAPE@XY', 'MeasureVal']) as cursor:
                valid_count, means = station_means(cursor)
            if len(means) < 12:
                raise ValueError('At least 12 valid unique locations are required for this configuration.')
            stations = gdb + '/Station_Means'
            arcpy.management.CreateFeatureclass(gdb, 'Station_Means', 'POINT', spatial_reference=projection)
            arcpy.management.AddField(stations, 'Mean_DO', 'DOUBLE')
            arcpy.management.AddField(stations, 'N_samples', 'LONG')
            with arcpy.da.InsertCursor(stations, ['SHAPE@XY', 'Mean_DO', 'N_samples']) as cursor:
                for xy, (mean, count) in means.items():
                    cursor.insertRow((xy, mean, count))

            raster_path = gdb + '/June_IDW'
            with arcpy.EnvManager(outputCoordinateSystem=projection, extent=bay, cellSize=100):
                raw_surface = arcpy.sa.Idw(stations, 'Mean_DO', 100, 2,
                                           arcpy.sa.RadiusVariable(12))
                # Explicit extraction makes the polygon-only requirement testable.
                masked = arcpy.sa.ExtractByMask(raw_surface, bay)
                masked.save(raster_path)
            surface_raster = arcpy.Raster(raster_path)
            with arcpy.EnvManager(snapRaster=raster_path, extent=raster_path, cellSize=100):
                mask_grid = gdb + '/Mask_Check'
                arcpy.conversion.PolygonToRaster(bay, arcpy.Describe(bay).OIDFieldName,
                                                 mask_grid, 'CELL_CENTER', cellsize=100)
            pixels = arcpy.RasterToNumPyArray(surface_raster, nodata_to_value=-9999)
            mask = arcpy.RasterToNumPyArray(mask_grid, nodata_to_value=-9999)
            if pixels.shape != mask.shape:
                raise RuntimeError('Mask-check grid does not align with the interpolation grid.')
            outside = int(np.count_nonzero((pixels != -9999) & (mask == -9999)))
            if outside:
                raise RuntimeError(f'Found {outside} raster cells outside the supplied bay mask.')

            project = arcpy.mp.ArcGISProject(str(template))
            map_ = project.listMaps()[0] if project.listMaps() else project.createMap('June 2014')
            for layer in map_.listLayers():
                map_.removeLayer(layer)
            map_.name = 'Corozal coursework - June 2014'
            map_.spatialReference = projection
            surface = map_.addDataFromPath(raster_path)
            surface.name = 'Dissolved oxygen (mg/L)'
            sym = surface.symbology
            sym.updateColorizer('RasterClassifyColorizer')
            sym.colorizer.breakCount = 5
            ramps = project.listColorRamps('Yellow-Green-Blue*')
            if ramps:
                sym.colorizer.colorRamp = ramps[0]
            # Widen bounds on a different dataset so valid cells are not silently hidden.
            minimum = float(arcpy.management.GetRasterProperties(raster_path, 'MINIMUM')[0])
            maximum = float(arcpy.management.GetRasterProperties(raster_path, 'MAXIMUM')[0])
            lower, upper = min(2.0, minimum), max(10.0, maximum)
            sym.colorizer.lowerBound = lower
            for item, lo, hi in zip(sym.colorizer.classBreaks,
                                    [lower, 4, 5, 6, 7], [4, 5, 6, 7, upper]):
                item.upperBound = hi
                item.label = f'{lo:.1f} - {hi:.1f}'
            surface.symbology = sym
            bay_layer = map_.addDataFromPath(bay)
            bay_layer.name = 'Supplied bay boundary'
            sym = bay_layer.symbology
            sym.renderer.symbol.color = {'RGB': [255, 255, 255, 0]}
            sym.renderer.symbol.outlineColor = {'RGB': [62, 80, 91, 100]}
            sym.renderer.symbol.outlineWidth = .6
            bay_layer.symbology = sym
            points = map_.addDataFromPath(stations)
            points.name = 'Sampling locations'
            sym = points.symbology
            sym.renderer.symbol.color = {'RGB': [40, 40, 40, 100]}
            sym.renderer.symbol.size = 2.5
            points.symbology = sym
            scale = create_layout(arcpy, project, map_, surface, bay_layer, points,
                                  output, args.author, valid_count, len(means))
            summary = {
                'period': '2014-06', 'selected_records': int(arcpy.management.GetCount(june)[0]),
                'valid_records': valid_count, 'unique_locations': len(means),
                'all_depths_included': True, 'cell_size_m': 100, 'idw_power': 2,
                'nearest_locations': 12, 'cells_outside_mask': outside,
                'raster_min_mg_l': minimum, 'raster_max_mg_l': maximum,
                'broken_layers': [layer.name for layer in map_.listLayers() if layer.isBroken],
                'map_scale': scale,
            }
            if summary['broken_layers']:
                raise RuntimeError('The output map contains broken layer sources.')
            (output / 'validation_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
            print(json.dumps(summary, indent=2))
    finally:
        arcpy.CheckInExtension('Spatial')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-folder', required=True)
    parser.add_argument('--template-project', required=True)
    parser.add_argument('--output-folder', required=True)
    parser.add_argument('--author', default='Kyle Ali')
    run(parser.parse_args())
