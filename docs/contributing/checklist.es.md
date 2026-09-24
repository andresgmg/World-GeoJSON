# Checklist de revisión

Repásalo antes de abrir un PR. Los revisores usan la misma lista.

Los puntos marcados **CI** se comprueban automáticamente en cada pull request
que toca `data/`, `schemas/` o `scripts/` — con `scripts/validate_data.py`
(ejecutado con `--checksums`), `finalize_geojson.py --check` y
`build_index.py --check`. Ejecútalos antes en local:

```bash
python scripts/validate_data.py --checksums data/earth/XXX
python scripts/finalize_geojson.py --check data/earth/XXX
python scripts/build_index.py --check
```

Todo lo demás necesita una persona.

## Licencias

- [ ] **CI** — `source.name`, `source.url`, `source.license` y
      `source.retrieved` están todos rellenos
- [ ] **CI** — `source.license` y cada `datasets[].license` están en la lista
      blanca permisiva — el enum `license` de `schemas/manifest.schema.json`:
      `CC0-1.0`, `CC-BY-2.5`, `CC-BY-3.0`, `CC-BY-3.0-IGO`, `CC-BY-4.0`,
      `Etalab-2.0`, `OGL-Canada-2.0`, `public-domain`. Cualquier otra cosa —
      incluida toda variante ODbL y CC-BY-SA — se rechaza
- [ ] **CI** — si `source.license` es `mixed`, `source.licenses` lista las
      licencias reales
- [ ] La fuente está en la [lista verde](sources.md#verde-usar-libremente), o
      sus términos se han revisado y aprobado explícitamente
- [ ] Los requisitos de atribución, si los hay, se pueden satisfacer desde la
      página del catálogo
- [ ] Los datos **no** vienen de GADM, de un proveedor propietario ni de una
      fuente sin licencia

## Nombres y estructura

- [ ] La ruta es `data/{body}/{CODE}/{CODE}_{LEVEL}.geojson`
- [ ] `CODE` es el ISO 3166-1 alpha-3 correcto, en mayúsculas
- [ ] La extensión es `.geojson`, y no hay un `.json` duplicado
- [ ] Las partes de un nivel partido, si las hay, están en
      `{LEVEL}/{código}.geojson`
- [ ] Los previews están en `preview/` con el nombre `{stem}.preview.geojson`
- [ ] Sin espacios, tildes ni caracteres no ASCII en ninguna ruta
- [ ] El país tiene una entrada en `scripts/countries.json`

## Contenido del archivo

- [ ] **CI** — JSON válido, y un `FeatureCollection`
- [ ] **CI** — `bbox` de nivel superior presente
- [ ] **CI** — **sin miembro `crs`** — prohibido por RFC 7946
- [ ] **CI** — al menos una feature, y sin geometrías `null`
- [ ] **CI** — menos de 50 MB
- [ ] **CI** — formato canónico: una feature por línea, compacto, coordenadas
      con como máximo 6 decimales — `finalize_geojson.py --check` pasa
- [ ] **CI** — `bbox` igual a la extensión de las coordenadas
- [ ] Coordenadas con longitud primero, EPSG:4326 / CRS84
- [ ] Orientación según la regla de la mano derecha
- [ ] Cruces del antimeridiano cortados en 180°, si aplica
- [ ] `npx @mapbox/geojsonhint archivo.geojson` no reporta nada

## Propiedades

- [ ] **CI** — cada feature valida contra
      `schemas/feature-properties.schema.json`: `shapeName`, `shapeISO`,
      `shapeGroup`, `shapeType` presentes, solo las claves opcionales
      conocidas, `src_*` para todo lo demás
- [ ] **CI** — `shapeISO` es una **cadena** en cada feature; `""` donde la
      fuente no tiene código, nunca un id opaco; único dentro del nivel donde
      no está vacío
- [ ] **CI** — cada feature tiene un `id` con la forma
      `{ISO3}:{LEVEL}:{clave}`, único dentro del archivo
- [ ] `shapeISO` lleva ceros a la izquierda donde el código oficial los exija
- [ ] `shapeType` coincide con el nivel del archivo
- [ ] Atributos de origen preservados bajo `src_`
- [ ] Artefactos Esri eliminados (`objectid`, `st_area_sh`, `st_length_`,
      `shape_leng`)
- [ ] Los nombres llevan las tildes correctas y no muestran mojibake (`Ã`, `Â`,
      `â€`)
- [ ] Los nombres no están abreviados

## Anidamiento, si hay varios niveles

- [ ] Cada feature ADM*n* anida dentro de exactamente una feature ADM*n-1*
- [ ] **CI** — cada `parentID` resuelve a una feature que existe en el país
- [ ] Cada feature por debajo de ADM1 lleva `adm1ISO` (o `"unassigned"`), y
      cada feature con nivel padre publicado lleva `parentISO` y `parentID` —
      los escribe `finalize_geojson.py`; un recuento `unassigned` se explica
      en `notes`
- [ ] Todos los niveles vienen de la misma añada

## Manifiesto

- [ ] **CI** — `manifest.json` existe en el directorio del país y valida
      contra `schemas/manifest.schema.json`
- [ ] **CI** — `body`, `name`, `crs`, `source` y `status` están presentes
- [ ] **CI** — cada entrada de dataset tiene número de features y `license`
- [ ] **CI** — los recuentos de features coinciden con los archivos, y en los
      niveles partidos `parts[].features` suman el `features` del nivel
- [ ] **CI** — los `bytes` y el `sha256` de cada archivo coinciden
      (`--checksums`)
- [ ] **CI** — `data/index.json` se regeneró (`build_index.py --check`)
- [ ] **CI** — `notes`, si existe, es una sola línea
- [ ] `iso_a3`, `iso_a2` y `m49_region` coinciden con el registro
- [ ] `datasets` regenerado con `build_manifest.py`, no editado a mano
- [ ] El número de features coincide con el número oficial de unidades, o
      `notes` explica la discrepancia
- [ ] El bounding box está en el hemisferio correcto

## Previews

- [ ] **CI** — cada preview registrado en el manifiesto existe y pesa menos
      de 2 MB. Un dataset sin preview registrado es un aviso, no un error —
      pero el mapa del catálogo queda vacío, así que arréglalo
- [ ] Los previews se generaron **antes** que `build_manifest.py`, para que
      el manifiesto registre su ruta y tamaño
- [ ] El número de features del preview es igual al del origen
      (`make_previews.mjs` se niega a escribir uno que no lo cumpla)
- [ ] El preview renderizado se parece al país — sin islas perdidas, sin
      slivers

## Tamaño

- [ ] **CI** — cada `.geojson` pesa menos de 50 MB
- [ ] Sin Git LFS

## Registros

- [ ] Una entrada nueva en `scripts/shapeiso_fixes.json` corrige un error
      documentado de la fuente al código ISO 3166-2 real de la unidad, y el
      PR dice dónde está documentado el error — el archivo no sirve para
      inventar códigos
- [ ] Una entrada nueva en `scripts/id_overrides.json` se explica en el PR
- [ ] Si se corrigió un código ADM1, las partes municipales se volvieron a
      derivar (`build_data.py --resplit XXX`, y después
      `finalize_geojson.py`) y la parte con el código antiguo ya no existe

## Documentación

- [ ] Si el país tiene rarezas — niveles ausentes, zonas disputadas, códigos
      inusuales — están en `notes`
- [ ] Si hizo falta una convención nueva,
      [Referencia](../reference/index.md) se actualiza en el mismo PR

## Build

- [ ] `mkdocs build --strict` pasa
- [ ] Las páginas nuevas se ven bien con `mkdocs serve`

--8<-- "abbreviations.md"
