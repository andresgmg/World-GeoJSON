# Formato del manifiesto

Cada directorio de dataset contiene un `manifest.json`. Es la **única** entrada
de este sitio de documentación: todas las páginas del catálogo se generan a
partir de él.

## Por qué existe

El build de documentación no debe abrir nunca un archivo GeoJSON.

Parsear un archivo de 70 MB en cada build haría `mkdocs serve` inutilizable
para editar, ralentizaría notablemente el CI y obligaría al CI a descargar
datos que de otro modo no necesita. En su lugar, un script aparte escanea los
datos cuando cambian *los datos* y escribe unos pocos kilobytes de metadatos a
su lado. El build de docs lee solo eso.

Esto es lo que permite que el catálogo escale a cientos de países con coste de
build constante, y lo que permite que el CI haga checkout del repositorio *sin
ningún archivo `.geojson`*.

## Ejemplo

```json
{
  "schema_version": 1,
  "body": "earth",
  "iso_a3": "CHL",
  "iso_a2": "CL",
  "m49_region": "South America",
  "name": { "en": "Chile", "es": "Chile" },
  "crs": { "authority": "OGC", "code": "CRS84", "epsg": 4326 },
  "source": {
    "name": "Biblioteca del Congreso Nacional de Chile (BCN) / IDE Chile",
    "url": "https://www.bcn.cl/siit/mapas_vectoriales",
    "license": "CC-BY-3.0-CL",
    "retrieved": "2023-05-01"
  },
  "status": "review",
  "notes": "ADM2 (provincias) no disponible. 343 de 346 comunas presentes.",
  "datasets": [
    {
      "level": "ADM1",
      "path": "data/earth/CHL/CHL_ADM1.geojson",
      "preview": "data/earth/CHL/preview/CHL_ADM1.preview.geojson",
      "bytes": 3571959,
      "preview_bytes": 148320,
      "sha256": "…",
      "features": 16,
      "bbox": [-109.4548, -56.5333, -66.4177, -17.4983],
      "geometry_types": { "Polygon": 12, "MultiPolygon": 4 },
      "properties": ["shapeName", "shapeISO", "shapeGroup", "shapeType"]
    }
  ]
}
```

## Escrito a mano frente a generado

Esta separación es la parte importante del formato.

| Campo | Dueño | Notas |
|---|---|---|
| `schema_version` | mano | Se sube solo ante un cambio rompedor de formato |
| `body`, `iso_a3`, `iso_a2`, `m49_region` | mano | Identidad |
| `name` | mano | Nombres para mostrar, por idioma |
| `crs` | mano | Autoritativo — los archivos no pueden declararlo por sí mismos |
| `source` | mano | **Obligatorio.** Procedencia y licencia |
| `status` | mano | `ok`, `review` o `deprecated` |
| `notes` | mano | Huecos conocidos, rarezas, desajustes de añada |
| `datasets[]` | **máquina** | Regenerado por `build_manifest.py` |

`scripts/build_manifest.py` reemplaza el array `datasets` por completo y deja
intacta cualquier otra clave. Los metadatos curados sobreviven así a la
regeneración — que es lo que hace seguro reejecutar el escáner de forma
rutinaria.

## Regenerar

```bash
python scripts/build_manifest.py data/earth/CHL
```

El escáner streamea cada archivo con `ijson` en memoria constante, así que una
entrada de 70 MB cuesta unos segundos y unas decenas de megabytes de RAM en vez
de más de un gigabyte de objetos Python parseados.

Calcula `features`, `bbox`, `geometry_types`, `properties`, `bytes` y `sha256`
a partir del propio archivo. No edites esos campos a mano; el CI regenera el
manifiesto y falla el build si la versión commiteada no coincide.

## Checksums y finales de línea

`sha256` se calcula sobre los bytes crudos del archivo tal como se almacena,
con finales de línea **LF**.

Esto importa más de lo que parece. Git normaliza los finales de línea al hacer
checkout, así que el mismo archivo en Windows con CRLF es un byte por línea más
grande — 1,8 MB más, en el caso del archivo de comunas de Chile — y su hash es
completamente distinto.

El `.gitattributes` del repositorio fija `*.geojson` a `eol=lf` para que los
hashes calculados en Windows, en el CI de Linux y por
`raw.githubusercontent.com` coincidan todos. Si te da un desajuste, revisa tu
configuración de finales de línea de Git antes de sospechar de los datos.

## Validación

Un workflow de CI comprueba, en cada PR que toque `data/`:

- que el manifiesto commiteado coincide con una regeneración limpia;
- que `source.license` está en la
  [lista aprobada](../contributing/sources.md);
- que cada preview pesa menos de 2 MB;
- que cada `.geojson` pesa menos de 50 MB.

--8<-- "abbreviations.md"
