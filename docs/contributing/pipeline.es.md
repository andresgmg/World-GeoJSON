# Pipeline de datos

Cómo los datos de origen se convierten en un archivo que este repositorio
acepta.

## 1. Convertir a GeoJSON

La mayoría de los datos oficiales de límites vienen como shapefiles de Esri.

=== "ogr2ogr"

    ```bash
    ogr2ogr -f GeoJSON \
      -t_srs EPSG:4326 \
      -lco RFC7946=YES \
      -lco COORDINATE_PRECISION=6 \
      -lco WRITE_BBOX=YES \
      salida.geojson entrada.shp
    ```

    `-lco RFC7946=YES` importa: sin él, GDAL escribe el dialecto del borrador
    de 2008, que permite un miembro `crs` y usa reglas de orientación
    distintas.

=== "mapshaper"

    ```bash
    npx mapshaper entrada.shp \
      -proj wgs84 \
      -o precision=0.000001 format=geojson salida.geojson
    ```

## 2. Reproyectar a EPSG:4326

Lo cubren los flags de arriba, pero verifica en vez de suponer — un shapefile
con un `.prj` ausente o incorrecto pasará sin cambios y dejará tu país en el
Golfo de Guinea.

```bash
npx mapshaper -i salida.geojson -info
```

Las coordenadas deben estar en el rango −180…180 / −90…90 y en el hemisferio
correcto.

## 3. Renombrar propiedades

Mapea los campos de origen al [esquema estándar](../reference/schema.md),
preserva el resto bajo `src_` y descarta los artefactos de exportación.

```bash
npx mapshaper salida.geojson \
  -rename-fields shapeName=NOMBRE,src_codigo=CODIGO \
  -each 'shapeGroup="CHL", shapeType="ADM1", shapeISO=String(src_codigo).padStart(2,"0")' \
  -filter-fields shapeName,shapeISO,shapeGroup,shapeType,src_codigo \
  -o normalizado.geojson
```

!!! danger "Rellena los códigos con ceros, como cadenas"

    `shapeISO` debe ser una cadena. Los códigos oficiales llevan con
    frecuencia ceros a la izquierda que un número JSON no puede representar —
    Camiña, en Chile, es `01402`, no `1402`. Equivocarse aquí hace que todos
    los joins posteriores fallen en silencio.

## 4. Fijar la precisión

Seis decimales, unos 11 cm. Ver
[CRS y precisión](../reference/crs.md#precision-de-coordenadas).

```bash
npx mapshaper normalizado.geojson -o precision=0.000001 final.geojson
```

Los datos de origen suelen traer 14 o más decimales. Los dígitos extra son
ruido y ocupan bytes reales.

## 5. No formatear con indentación

Escribe JSON minificado. Los archivos actuales de Chile están indentados con
cuatro espacios, lo que supone alrededor del 40% de su tamaño sin ningún
beneficio — nadie lee un archivo de 1,8 millones de líneas, y los diffs de
geometría no son revisables por humanos de todos modos.

`ogr2ogr` y `mapshaper` escriben JSON compacto por defecto. Si tu herramienta
indenta, minifica antes de commitear.

## 6. Corregir orientación y antimeridiano

RFC 7946 exige orientación según la regla de la mano derecha y geometrías
cortadas en los 180°. mapshaper hace ambas al escribir GeoJSON, pero
comprueba cualquier país con territorio cerca del antimeridiano o de los polos:

```bash
npx mapshaper final.geojson -info
```

## 7. Validar

```bash
npx @mapbox/geojsonhint final.geojson
```

Confirma a ojo:

- [ ] `FeatureCollection` con `bbox` de nivel superior
- [ ] sin miembro `crs`
- [ ] el número de features coincide con el número oficial de unidades
- [ ] sin geometrías `null`
- [ ] los valores de `shapeName` llevan las tildes correctas y no hay mojibake

El mojibake es lo habitual: un shapefile con `.cpg` ausente o incorrecto
decodifica `Ñuble` como `Ã‘uble`. Si ves una `Ã` en cualquier sitio, la
codificación se leyó mal — vuelve al paso 1 y fuerza UTF-8.

## 8. Comprobar tamaño

Si el resultado supera 50 MB, GitHub avisa; por encima de 100 MB rechaza el
push. Antes de recurrir a Git LFS —
[no lo hagas](../about/versioning.md#por-que-no-git-lfs) — confirma que
realmente has minificado y recortado la precisión. Esos dos pasos por sí solos
suelen eliminar más de la mitad de los bytes.

## 9. Manifiesto y preview

```powershell
.\.venv\Scripts\python.exe scripts\build_manifest.py data\earth\XXX
node scripts\make_previews.mjs data/earth/XXX
```

Ver [Formato del manifiesto](../reference/manifest.md) y
[Simplificación y previews](previews.md).

--8<-- "abbreviations.md"
