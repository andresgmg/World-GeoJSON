# Checklist de revisión

Repásalo antes de abrir un PR. Los revisores usan la misma lista.

## Licencias

- [ ] La fuente está en la [lista verde](sources.md#verde-usar-libremente), o
      sus términos se han revisado y aprobado explícitamente
- [ ] `source.name`, `source.url`, `source.license` y `source.retrieved` están
      todos rellenos
- [ ] `license` es un [identificador SPDX](https://spdx.org/licenses/) válido
- [ ] Los requisitos de atribución, si los hay, se pueden satisfacer desde la
      página del catálogo
- [ ] Los datos **no** vienen de GADM, de un proveedor propietario ni de una
      fuente sin licencia

## Nombres y estructura

- [ ] La ruta es `data/{body}/{CODE}/{CODE}_{LEVEL}.geojson`
- [ ] `CODE` es el ISO 3166-1 alpha-3 correcto, en mayúsculas
- [ ] La extensión es `.geojson`, y no hay un `.json` duplicado
- [ ] Los previews están en `preview/` con el nombre `{stem}.preview.geojson`
- [ ] Sin espacios, tildes ni caracteres no ASCII en ninguna ruta

## Contenido del archivo

- [ ] GeoJSON válido (`npx @mapbox/geojsonhint archivo.geojson`)
- [ ] `FeatureCollection` con `bbox` de nivel superior
- [ ] **Sin miembro `crs`** — prohibido por RFC 7946
- [ ] Coordenadas con longitud primero, EPSG:4326 / CRS84
- [ ] No más de 6 decimales de precisión
- [ ] Minificado, sin indentación
- [ ] Orientación según la regla de la mano derecha
- [ ] Cruces del antimeridiano cortados en 180°, si aplica
- [ ] Sin geometrías `null`

## Propiedades

- [ ] `shapeName`, `shapeISO`, `shapeGroup`, `shapeType` en cada feature
- [ ] `shapeISO` es una **cadena**, con ceros a la izquierda donde el código
      oficial los exija
- [ ] `shapeType` coincide con el nivel del archivo
- [ ] Atributos de origen preservados bajo `src_`
- [ ] Artefactos Esri eliminados (`objectid`, `st_area_sh`, `st_length_`,
      `shape_leng`)
- [ ] Los nombres llevan las tildes correctas y no muestran mojibake (`Ã`, `Â`,
      `â€`)
- [ ] Los nombres no están abreviados

## Anidamiento, si hay varios niveles

- [ ] Cada feature ADM*n* anida dentro de exactamente una feature ADM*n-1*
- [ ] `parentISO` está poblado y resuelve
- [ ] Todos los niveles vienen de la misma añada

## Manifiesto

- [ ] `manifest.json` existe en el directorio del país
- [ ] Campos escritos a mano completos: `body`, `iso_a3`, `iso_a2`,
      `m49_region`, `name`, `crs`, `source`, `status`
- [ ] `datasets` regenerado con `build_manifest.py`, no editado a mano
- [ ] El número de features coincide con el número oficial de unidades, o
      `notes` explica la discrepancia
- [ ] El bounding box está en el hemisferio correcto

## Previews

- [ ] Existe un preview para cada dataset
- [ ] Cada preview pesa menos de 2 MB (objetivo: menos de 800 KB)
- [ ] El número de features del preview es igual al del origen
- [ ] El preview renderizado se parece al país — sin islas perdidas, sin
      slivers

## Tamaño

- [ ] Cada `.geojson` pesa menos de 50 MB
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
