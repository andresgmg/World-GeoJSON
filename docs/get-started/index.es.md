# Empezar

Usar este proyecto son tres pasos.

1. **Encuentra tu dataset** en el [Catálogo](../catalog/index.md). Cada página
   lista los niveles administrativos disponibles para ese país, cuántas
   features tiene cada uno y su bounding box.
2. **Copia una URL.** Cada página de dataset ofrece una URL de CDN, una de raw
   GitHub y un comando `curl`; las partes de un nivel partido enlazan solo al
   CDN. [Descarga y CDN](download.md) explica cuál usar en cada caso — la
   respuesta no siempre es el CDN.
3. **Cárgalo.** [Inicio rápido](quickstart.md) tiene ejemplos funcionando para
   Leaflet, MapLibre, Python y QGIS.

## Antes de empezar: tamaños de archivo

Los datos de límites administrativos son grandes, y este proyecto los guarda
sin comprimir para que sigan siendo diffeables y consumibles directamente.
Todos los archivos bajo `data/` están simplificados a una tolerancia de 100 m
sobre el terreno, lo que deja el más grande — el ADM1 de Canadá — en 14,9 MB
y ninguno por encima de 20 MB. Las 345 comunas de Chile pesan 7 MB.

Eso tiene consecuencias que conviene saber de entrada:

- **No cargues un archivo a resolución completa en el navegador.** Quince
  megabytes por la red se convierten en un múltiplo de eso en heap de
  JavaScript tras `JSON.parse`, con el hilo principal bloqueado mientras
  parsea. En móvil es una pestaña que revienta, no un mapa lento. Usa los
  previews simplificados: cada dataset tiene uno en
  `data/earth/{ISO3}/preview/{ISO3}_{LEVEL}.preview.geojson` — como máximo
  2 MB, coordenadas con cuatro decimales y solo `shapeName`, `shapeISO` y
  `shapeType` — y se pueden cargar en el navegador sin problema. O simplifica
  a tu propia tolerancia — ver [Recetas](recipes.md#simplificar-para-la-web).
- **No clones el repositorio entero** solo para obtener un país. Usa un sparse
  checkout; [Descarga y CDN](download.md#git) muestra cómo.
- **El CDN no está garantizado.** jsDelivr limita los archivos a 20 MB — todos
  los de `data/` están por debajo — pero también documenta un límite de 150 MB
  por repositorio, que este supera actualmente, así que puede negarse a
  servirlo. Las URLs raw de GitHub siempre funcionan.

!!! note "Los archivos heredados de la raíz son la excepción"

    `comunas.geojson`, en la raíz del repositorio, es un dataset antiguo de
    72 MB que se conserva solo para que los enlaces existentes sigan
    funcionando. Su reemplazo es `data/earth/CHL/CHL_ADM3.geojson`.

## ¿Qué nivel administrativo necesitas?

| Quieres | Nivel | En Chile |
|---|---|---|
| Divisiones de primer nivel | ADM1 | 16 regiones |
| Divisiones de segundo nivel | ADM2 | 56 provincias |
| El tier municipal | ADM3 | 345 comunas |

Los números de nivel son estructurales, no semánticos: el ADM1 de un país es
como se llame su primera división. Ver
[Niveles administrativos](../reference/admin-levels.md).

--8<-- "abbreviations.md"
