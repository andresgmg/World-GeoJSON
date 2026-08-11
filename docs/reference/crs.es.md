# Sistemas de referencia de coordenadas

## La regla

Todos los datos terrestres de este repositorio están en **OGC:CRS84** —
longitud y latitud en grados decimales sobre el datum WGS 84. Es numéricamente
idéntico a EPSG:4326 con el orden de ejes que exige GeoJSON.

```json
"coordinates": [-70.6483, -33.4569]
```

**Longitud primero.** EPSG:4326 define formalmente la latitud primero; GeoJSON
lo sobrescribe. Invertir el par es el error más común en GeoJSON editado a
mano, y falla en silencio — la geometría se dibuja, solo que en el hemisferio
equivocado.

## El miembro `crs` está prohibido

RFC 7946 §4 establece que todas las coordenadas GeoJSON están en WGS 84, y la
especificación **eliminó** el miembro `crs` que permitía el borrador de 2008.
Un archivo conforme no puede declarar su sistema de coordenadas, porque solo
hay una respuesta permitida.

Por tanto: ningún archivo de este repositorio contiene un miembro `crs`. La
declaración autoritativa vive fuera de banda, en el
[`manifest.json`](manifest.md) del dataset:

```json
"crs": { "authority": "OGC", "code": "CRS84", "epsg": 4326 }
```

Ese campo existe porque es genuinamente esencial para los datos planetarios,
donde las coordenadas *no* son WGS 84 y el archivo no puede decirlo. Ver
[Cuerpos planetarios](planetary.md).

## Precisión de coordenadas

Las coordenadas **no deben** exceder los **6 decimales** — unos 11 cm en el
ecuador.

Los archivos actuales de Chile guardan unos **14** decimales
(`-68.95020116247055`). Eso es precisión de nanómetro sobre límites
levantados, en el mejor de los casos, con exactitud métrica. No es más exacto;
es la misma exactitud con ocho dígitos de ruido pegados, y esos dígitos ocupan
bytes reales en un archivo de 70 MB.

| Decimales | Precisión en el ecuador |
|---|---|
| 3 | 110 m |
| 4 | 11 m |
| 5 | 1,1 m |
| 6 | 11 cm |

Seis es generoso para límites administrativos. Los previews usan cuatro.

## El miembro `bbox`

Cada `FeatureCollection` **debería** llevar un `bbox` de nivel superior:

```json
"bbox": [-109.4548, -56.5333, -66.4177, -17.4983]
```

El orden es `[oeste, sur, este, norte]`. Permite a un consumidor decidir si
descargar el archivo siquiera, y a un mapa ajustar su vista sin parsear toda la
geometría.

Ninguno de los archivos actuales de Chile lo tiene. Añadirlos es parte de la
migración.

## Sentido de giro

RFC 7946 §3.1.6 exige la regla de la mano derecha: anillos exteriores en
sentido antihorario, anillos interiores (huecos) en horario. Muchas
herramientas lo ignoran al leer, pero algunas — en particular varios pipelines
de vector tiles y los índices geoespaciales de MongoDB — no, y tratarán un
polígono mal orientado como si cubriera el planeta entero menos tu forma.

`mapshaper` corrige la orientación al escribir. Verifica en vez de suponer.

## El antimeridiano

RFC 7946 §3.1.9: las geometrías que cruzan los 180° de longitud **deberían**
cortarse en dos en el antimeridiano, en lugar de usar coordenadas fuera del
rango −180…180.

Esto no es hipotético para Chile:

- **Isla de Pascua** está a unos 109°O — dentro de rango, pero lo bastante
  lejos del continente como para que un bounding box ingenuo abarque un tercio
  del planeta.
- **El Territorio Antártico Chileno** se extiende hasta el Polo Sur. Los
  polígonos que incluyen un polo son un modo de fallo conocido para
  renderizadores y para pruebas de punto-en-polígono, con total independencia
  de la cuestión del antimeridiano.

Cualquier dataset que incluya geometría polar o que cruce el antimeridiano
**debe** indicarlo en el manifiesto, para que no sorprenda a los consumidores.

## Reproyección

No calcules áreas ni distancias en grados. Un grado de longitud son 111 km en
el ecuador y 0 en los polos; el área en "grados cuadrados" no es una magnitud.

Reproyecta primero a algo adecuado a tu zona de interés — para Chile,
EPSG:5361 (SIRGAS-Chile). Ver
[Recetas](../get-started/recipes.md#calcular-el-area-correctamente).

Los datos **deben** almacenarse en CRS84 igualmente. La reproyección es trabajo
del consumidor; guardar cualquier otra cosa haría los archivos no conformes.

--8<-- "abbreviations.md"
