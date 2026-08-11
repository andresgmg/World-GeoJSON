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
    "name": "IDE Chile / SUBDERE — División Política Administrativa 2023",
    "url": "https://www.geoportal.cl/",
    "license": "CC-BY-4.0",
    "retrieved": "2026-08-11"
  },
  "status": "ok",
  "notes": "345 comunas, no las 346 del registro oficial: falta Antártica (12202) porque el paquete DPA excluye la reclamación antártica chilena.",
  "datasets": [
    {
      "level": "ADM1",
      "path": "data/earth/CHL/CHL_ADM1.geojson",
      "preview": "data/earth/CHL/preview/CHL_ADM1.preview.geojson",
      "bytes": 4814221,
      "preview_bytes": 226499,
      "sha256": "5cf4e9d8d34822d4…",
      "features": 16,
      "bbox": [-109.449861, -56.525107, -66.416176, -17.498399],
      "geometry_types": { "MultiPolygon": 10, "Polygon": 6 },
      "properties": ["shapeName", "shapeISO", "shapeGroup", "shapeType"],
      "simplification": { "method": "visvalingam", "tolerance_m": 100 }
    }
  ]
}
```

## Niveles partidos

El nivel municipal va partido por padre ADM1, así que su entrada lleva un array
`parts` en vez de apoyarse en un único archivo:

```json
{
  "level": "ADM3",
  "split_by": "ADM1",
  "features": 345,
  "path": "data/earth/CHL/CHL_ADM3.geojson",
  "parts": [
    {
      "code": "CL-RM",
      "path": "data/earth/CHL/ADM3/CL-RM.geojson",
      "features": 52,
      "bytes": 164329,
      "sha256": "…",
      "bbox": [-71.72, -34.30, -70.02, -32.92]
    }
  ]
}
```

- `features` en la entrada es el **nivel completo**, para que el catálogo pueda
  dar siempre un total exista o no un archivo combinado.
- `path` es el archivo de país completo, opcional, presente solo cuando cabe por
  debajo de 20 MB. Su ausencia es normal y el catálogo lo indica.
- `code` es el ISO 3166-2 del padre ADM1, o un slug del nombre cuando no se
  conoce código ISO.

El CI comprueba que las partes sumen exactamente el número de features del
nivel — así es como se detecta una partición que perdió o duplicó un municipio.

## Simplificación

Cada dataset registra qué se le hizo:

```json
"simplification": { "method": "visvalingam", "tolerance_m": 100 }
```

`tolerance_m` es una **distancia sobre el terreno**, no un porcentaje. Es
deliberado: un porcentaje conserva una fracción fija de los vértices de cada
archivo, así que la resolución resultante depende de lo densamente que se
hubiera digitalizado la fuente y dos países vecinos acaban con fidelidades
distintas. Una distancia da a todo el repositorio una única resolución real
consistente.

La tolerancia estándar son **100 m**. Las 16 regiones de Chile — una de las
costas más complejas del mundo — miden 49,7 MB a 10 m, 10,0 MB a 50 m, 4,6 MB a
100 m y 1,6 MB a 250 m. Un dataset que aun así superara el techo de tamaño con
la tolerancia estándar recibe una más gruesa, y el valor registrado aquí es
siempre el aplicado realmente.

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
