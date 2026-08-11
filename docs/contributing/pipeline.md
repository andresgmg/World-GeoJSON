# Data pipeline

How raw source data becomes a file this repository will accept.

## 1. Convert to GeoJSON

Most authoritative boundary data ships as Esri shapefiles.

=== "ogr2ogr"

    ```bash
    ogr2ogr -f GeoJSON \
      -t_srs EPSG:4326 \
      -lco RFC7946=YES \
      -lco COORDINATE_PRECISION=6 \
      -lco WRITE_BBOX=YES \
      output.geojson input.shp
    ```

    `-lco RFC7946=YES` matters: without it GDAL writes the older 2008 draft
    dialect, which permits a `crs` member and uses different winding rules.

=== "mapshaper"

    ```bash
    npx mapshaper input.shp \
      -proj wgs84 \
      -o precision=0.000001 format=geojson output.geojson
    ```

## 2. Reproject to EPSG:4326

Handled by the flags above, but verify rather than assume — a shapefile with a
missing or wrong `.prj` will be passed through unchanged and land your country
in the Gulf of Guinea.

```bash
npx mapshaper -i output.geojson -info
```

Coordinates should be in the −180…180 / −90…90 range and in the right
hemisphere.

## 3. Rename properties

Map source fields onto the [standard schema](../reference/schema.md), preserve
the rest under `src_`, drop the export artifacts.

```bash
npx mapshaper output.geojson \
  -rename-fields shapeName=NOMBRE,src_codigo=CODIGO \
  -each 'shapeGroup="CHL", shapeType="ADM1", shapeISO=String(src_codigo).padStart(2,"0")' \
  -filter-fields shapeName,shapeISO,shapeGroup,shapeType,src_codigo \
  -o normalised.geojson
```

!!! danger "Zero-pad codes as strings"

    `shapeISO` must be a string. Official codes frequently have leading zeros
    that a JSON number cannot represent — Chile's Camiña is `01402`, not
    `1402`. Getting this wrong makes every downstream join fail silently.

## 4. Set coordinate precision

Six decimal places, roughly 11 cm. See
[CRS & precision](../reference/crs.md#coordinate-precision).

```bash
npx mapshaper normalised.geojson -o precision=0.000001 final.geojson
```

Source data often carries 14+ decimals. The extra digits are noise and occupy
real bytes.

## 5. Do not pretty-print

Write minified JSON. The current Chile files are indented with four spaces,
which is roughly 40% of their size for no benefit — nobody reads a 1.8
million-line file, and diffs on geometry are not human-reviewable regardless.

`ogr2ogr` and `mapshaper` both write compact JSON by default. If your tool
pretty-prints, minify before committing.

## 6. Fix winding and the antimeridian

RFC 7946 requires right-hand-rule winding and geometries cut at 180°. mapshaper
handles both when writing GeoJSON, but check any country with territory near
the antimeridian or the poles:

```bash
npx mapshaper final.geojson -info
```

## 7. Validate

```bash
npx @mapbox/geojsonhint final.geojson
```

Confirm by eye:

- [ ] `FeatureCollection` with a top-level `bbox`
- [ ] no `crs` member
- [ ] feature count matches the official number of units
- [ ] no `null` geometries
- [ ] `shapeName` values carry correct diacritics and are not mojibake

Mojibake is the common one: a shapefile whose `.cpg` is missing or wrong
decodes `Ñuble` as `Ã‘uble`. If you see `Ã` anywhere, the encoding was
misread — go back to step 1 and force UTF-8.

## 8. Size check

If the result exceeds 50 MB, GitHub warns; above 100 MB it refuses the push.
Before reaching for Git LFS — [don't](../about/versioning.md#why-not-git-lfs) —
confirm you have actually minified and trimmed precision. Those two steps alone
typically remove more than half the bytes.

## 9. Manifest and preview

```powershell
.\.venv\Scripts\python.exe scripts\build_manifest.py data\earth\XXX
node scripts\make_previews.mjs data/earth/XXX
```

See [Manifest format](../reference/manifest.md) and
[Simplification & previews](previews.md).

--8<-- "abbreviations.md"
