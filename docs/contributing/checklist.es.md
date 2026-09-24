# Checklist de revisión

Repásalo antes de abrir un PR. Los revisores usan la misma lista.

Los puntos marcados **CI** los comprueba `scripts/validate_data.py`, que se
ejecuta en cada pull request que toca `data/`. Ejecútalo antes en local:

```bash
python scripts/validate_data.py data/earth/XXX
```

Todo lo demás necesita una persona.

## Licencias

- [ ] **CI** — `source.name`, `source.url`, `source.license` y
      `source.retrieved` están todos rellenos
- [ ] **CI** — `source.license` y cada `datasets[].license` están en la lista
      blanca permisiva: `CC0-1.0`, `CC-BY-2.5`, `CC-BY-3.0`, `CC-BY-3.0-IGO`,
      `CC-BY-4.0`, `Etalab-2.0`, `OGL-Canada-2.0`, `public-domain`. Cualquier
      otra cosa — incluida toda variante ODbL y CC-BY-SA — se rechaza
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
- [ ] **CI, solo aviso** — no más de 6 decimales de precisión en las
      coordenadas
- [ ] Coordenadas con longitud primero, EPSG:4326 / CRS84
- [ ] Una feature por línea, sin indentación
- [ ] Orientación según la regla de la mano derecha
- [ ] Cruces del antimeridiano cortados en 180°, si aplica
- [ ] `npx @mapbox/geojsonhint archivo.geojson` no reporta nada

## Propiedades

- [ ] **CI** — `shapeName`, `shapeISO`, `shapeGroup`, `shapeType` en cada
      feature
- [ ] **CI** — `shapeISO` es una **cadena** en cada feature
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
- [ ] Las partes de un nivel partido llevan `adm1ISO`, y `parentISO` resuelve
      donde exista (hoy solo lo lleva Chile; v1.0.0 lo añade en todos)
- [ ] Todos los niveles vienen de la misma añada

## Manifiesto

- [ ] **CI** — `manifest.json` existe en el directorio del país y es un
      objeto JSON
- [ ] **CI** — `body`, `name`, `crs`, `source` y `status` están presentes
- [ ] **CI** — cada entrada de dataset tiene número de features y `license`
- [ ] **CI** — en los niveles partidos, `parts[].features` suman el
      `features` del nivel
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

## Documentación

- [ ] Si el país tiene rarezas — niveles ausentes, zonas disputadas, códigos
      inusuales — están en `notes`
- [ ] Si hizo falta una convención nueva,
      [Referencia](../reference/index.md) se actualiza en el mismo PR

## Build

- [ ] `mkdocs build --strict` pasa
- [ ] Las páginas nuevas se ven bien con `mkdocs serve`

--8<-- "abbreviations.md"
