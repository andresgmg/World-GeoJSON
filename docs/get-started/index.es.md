# Empezar

Usar este proyecto son tres pasos.

1. **Encuentra tu dataset** en el [Catálogo](../catalog/index.md). Cada página
   lista los niveles administrativos disponibles para ese país, cuántas
   features tiene cada uno y su bounding box.
2. **Copia una URL.** Cada página de dataset ofrece una URL de CDN, una de raw
   GitHub y un comando `curl`. [Descarga y CDN](download.md) explica cuál usar
   en cada caso — la respuesta no siempre es el CDN.
3. **Cárgalo.** [Inicio rápido](quickstart.md) tiene ejemplos funcionando para
   Leaflet, MapLibre, Python y QGIS.

## Antes de empezar: tamaños de archivo

Los datos de límites administrativos son grandes, y este proyecto los guarda
sin comprimir para que sigan siendo diffeables y consumibles directamente.
Concretamente, el archivo de comunas de Chile pesa **70 MB**.

Eso tiene consecuencias que conviene saber de entrada:

- **No cargues un archivo a resolución completa en el navegador.** 70 MB por la
  red se convierten en varios cientos de megabytes de heap de JavaScript tras
  `JSON.parse`, más decenas de segundos de hilo principal bloqueado. En móvil
  es una pestaña que revienta, no un mapa lento. Usa los archivos de preview
  simplificados, o simplifica a tu propia tolerancia — ver
  [Recetas](recipes.md#simplificar-para-la-web).
- **No clones el repositorio entero** solo para obtener un país. Usa un sparse
  checkout; [Descarga y CDN](download.md#git) muestra cómo.
- **El CDN tiene un techo de 20 MB.** Los archivos por encima deben venir de
  raw GitHub.

## ¿Qué nivel administrativo necesitas?

| Quieres | Nivel | En Chile |
|---|---|---|
| El contorno del país | ADM0 | Chile |
| Divisiones de primer nivel | ADM1 | 16 regiones |
| Divisiones de segundo nivel | ADM2 | provincias — no existe archivo abierto |
| Divisiones de tercer nivel | ADM3 | 343 comunas |

Los números de nivel son estructurales, no semánticos: el ADM1 de un país es
como se llame su primera división. Ver
[Niveles administrativos](../reference/admin-levels.md).

--8<-- "abbreviations.md"
