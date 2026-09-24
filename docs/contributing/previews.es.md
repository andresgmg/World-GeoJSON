# Simplificación y previews

Cada dataset incluye un archivo simplificado que acompaña al original y que se
usa para el mapa de su página de catálogo.

## Por qué existen los previews

Los datos de límites a resolución completa no se pueden mostrar en un
navegador. Los archivos de `data/` ya están simplificados a una tolerancia de
100 m y aun así pesan entre 5 y 15 MB — las comunas de Chile 7 MB, las
provincias de Canadá 14,9 MB. Cargar uno significa eso por la red, un múltiplo
en heap de JavaScript tras `JSON.parse`, y el hilo principal bloqueado mientras
parsea. En un móvil es una pestaña que revienta, no un mapa lento.

Aparte, **jsDelivr rechaza archivos de más de 20 MB** y puede rechazar un
repositorio de más de 150 MB, así que la ruta CDN no es algo de lo que un mapa
del catálogo pueda depender.

Y un mapa de 420 píxeles de alto no puede dibujar precisión de 11 centímetros
de todas formas. El detalle no se está perdiendo — nunca fue visible.

## Generar

```bash
node scripts/make_previews.mjs data/earth/CHL
npm run previews                              # todos los países
```

Ejecútalo **antes** que `build_manifest.py`: el manifiesto registra la ruta y
el tamaño de un preview solo si el archivo ya existe.

Para cada nivel el script ejecuta mapshaper, empezando por el 5% de los
vértices:

```bash
npx mapshaper data/earth/CHL/CHL_ADM3.geojson \
  -simplify percentage=5% keep-shapes \
  -filter-fields shapeName,shapeISO,shapeType \
  -o precision=0.0001 bbox format=geojson \
     data/earth/CHL/preview/CHL_ADM3.preview.geojson
```

y después, mientras el resultado supere 800 KB, reduce el porcentaje a la
mitad — 2,5%, 1,25%, 0,625% — hasta un mínimo del 0,2%. Un nivel partido se
construye desde su archivo combinado, o uniendo las partes cuando no lo hay
(Brasil ADM2), de modo que el preview cubre el país entero.

| Paso | Efecto |
|---|---|
| `-simplify percentage=5%` | Simplificación Visvalingam conservando el 5% de los vértices |
| `keep-shapes` | Evita que polígonos pequeños colapsen a nada |
| `-filter-fields` | Deja solo lo que necesita el tooltip |
| `precision=0.0001` | ~11 m, de sobra para un mapa pequeño |

Resultado típico: 7 MB → 425 KB para las 345 comunas de Chile; 4,8 MB →
226 KB para sus 16 regiones.

## Presupuesto de tamaño

| Umbral | Significado |
|---|---|
| menos de 800 KB | Objetivo — el script deja de reducir aquí |
| 800 KB – 2 MB | Aceptable para geometría inusualmente compleja que sigue por encima del objetivo al 0,2% |
| más de 2 MB | **Rechazado.** `make_previews.mjs` se niega a escribirlo, y `validate_data.py` hace fallar el CI |

Un preview que sigue por encima de 2 MB al 0,2% significa que la geometría de
origen es inusualmente densa; el arreglo está aguas arriba, en la tolerancia
de simplificación del archivo de origen, no en el preview.

## Revisa el resultado

La simplificación es con pérdida y sus modos de fallo son visuales, así que
míralo.

- **Islas que desaparecen.** `keep-shapes` evita que se esfumen polígonos
  enteros, pero un multipolígono puede perder miembros pequeños. El script
  compara el número de features con el origen y se niega a escribir un
  preview que haya perdido alguna — pero un miembro de un multipolígono no es
  una feature, así que mira.
- **Slivers y auto-intersecciones.** Una simplificación agresiva puede hacer
  que límites adyacentes se crucen, dejando huecos o solapes visibles entre
  unidades.
- **Costas desconectadas.** Busca unidades que ya no toquen a sus vecinas.

```bash
npx mapshaper data/earth/CHL/preview/CHL_ADM3.preview.geojson -info
```

## Los previews se commitean

Son artefactos de build pequeños, y commitearlos significa que el sitio de
documentación no necesita ningún paso de build sobre los datos. Son
deterministas siempre que las entradas se procesen en un orden fijo, que es lo
que hace el script — niveles y partes ordenados por nombre — así que regenerar
desde fuentes sin cambios produce bytes sin cambios.

Regenéralos cada vez que cambie el archivo de origen. `validate_data.py` trata
un dataset sin preview registrado como un aviso (el mapa del catálogo queda
vacío), y un preview registrado que falta o supera 2 MB como un error;
[`manifest.json`](../reference/manifest.md) registra la ruta y el tamaño.

## Miniaturas estáticas

mapshaper también puede emitir SVG:

```bash
npx mapshaper entrada.geojson -o format=svg width=800 salida.svg
```

Unos 20 KB, sin JavaScript, se ve tanto en el README de GitHub como en el sitio
de documentación. Útil como alternativa donde un mapa interactivo es excesivo.

--8<-- "abbreviations.md"
