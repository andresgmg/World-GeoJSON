# Simplificación y previews

Cada dataset incluye un archivo simplificado que acompaña al original y que se
usa para el mapa de su página de catálogo.

## Por qué existen los previews

Los datos de límites a resolución completa no se pueden mostrar en un
navegador. El archivo de comunas de Chile pesa 70 MB; cargarlo significa 70 MB
por la red, varios cientos de megabytes de heap de JavaScript tras
`JSON.parse`, y decenas de segundos de hilo principal bloqueado. En un móvil es
una pestaña que revienta, no un mapa lento.

Aparte, **jsDelivr rechaza archivos de más de 20 MB**, así que para archivos
grandes la ruta CDN sencillamente no existe.

Y un mapa de 420 píxeles de alto no puede dibujar precisión de 11 centímetros
de todas formas. El detalle no se está perdiendo — nunca fue visible.

## Generar

```powershell
node scripts\make_previews.mjs data/earth/CHL
```

Que ejecuta, por dataset:

```bash
npx mapshaper data/earth/CHL/CHL_ADM3.geojson \
  -simplify percentage=2% keep-shapes \
  -filter-fields shapeName,shapeISO,shapeType \
  -o precision=0.0001 format=geojson \
     data/earth/CHL/preview/CHL_ADM3.preview.geojson
```

Tres reducciones que se componen:

| Paso | Efecto |
|---|---|
| `-simplify percentage=2%` | Simplificación Visvalingam conservando el 2% de los vértices |
| `keep-shapes` | Evita que polígonos pequeños colapsen a nada |
| `-filter-fields` | Deja solo lo que necesita el tooltip |
| `precision=0.0001` | ~11 m, de sobra para un mapa pequeño |

Resultado típico: 70 MB → 300-800 KB.

## Presupuesto de tamaño

| Umbral | Significado |
|---|---|
| menos de 800 KB | Objetivo |
| 800 KB – 2 MB | Aceptable para geometría inusualmente compleja |
| más de 2 MB | **El CI falla.** Simplifica más |

Si un preview no baja del presupuesto al 2%, baja al 1% o al 0,5%. Las costas
complejas — Chile, Noruega, Indonesia, Grecia — necesitan ajustes más agresivos
que los países compactos.

## Revisa el resultado

La simplificación es con pérdida y sus modos de fallo son visuales, así que
míralo.

- **Islas que desaparecen.** `keep-shapes` evita que se esfumen polígonos
  enteros, pero un multipolígono puede perder miembros pequeños. Compara el
  número de features antes y después: debe coincidir exactamente.
- **Slivers y auto-intersecciones.** Una simplificación agresiva puede hacer
  que límites adyacentes se crucen, dejando huecos o solapes visibles entre
  unidades.
- **Costas desconectadas.** Busca unidades que ya no toquen a sus vecinas.

```bash
npx mapshaper data/earth/CHL/preview/CHL_ADM3.preview.geojson -info
```

El número de features debe ser igual al del origen. Si no lo es, la
simplificación descartó geometría y los ajustes son demasiado agresivos.

## Los previews se commitean

Son artefactos de build pequeños y deterministas, y commitearlos significa que
el sitio de documentación no necesita ningún paso de build sobre los datos.
Regenéralos cada vez que cambie el archivo de origen — el CI comprueba que
existen y que están dentro del presupuesto, y
[`manifest.json`](../reference/manifest.md) registra su tamaño.

## Miniaturas estáticas

mapshaper también puede emitir SVG:

```bash
npx mapshaper entrada.geojson -o format=svg width=800 salida.svg
```

Unos 20 KB, sin JavaScript, se ve tanto en el README de GitHub como en el sitio
de documentación. Útil como alternativa donde un mapa interactivo es excesivo.

--8<-- "abbreviations.md"
