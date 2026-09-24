# Fuentes aprobadas y licencias

**Lee esto antes de hacer cualquier otro trabajo en una contribución de datos.**

Un archivo de límites con una licencia incompatible no se puede mergear, por
buena que sea la geometría. Y una vez que está en la historia de git es
genuinamente difícil de quitar — reescribir la historia rompe todos los clones y
forks existentes. Así que la verificación se hace en la puerta, y la aplica el
CI mediante `scripts/validate_data.py`.

## La cuestión de la compatibilidad

Este repositorio distribuye datos públicamente, gratis, para cualquier uso
incluido el comercial. Una fuente solo es utilizable aquí si su licencia permite
exactamente eso.

Hay dos modos de fallo:

- **Restricciones de redistribución** — la licencia prohíbe transmitir los
  datos, o prohíbe el uso comercial. Inutilizable, sin más.
- **Obligaciones de share-alike (copyleft)** — la licencia permite redistribuir
  pero exige que los derivados lleven la misma licencia. ODbL en particular
  define una *Base de Datos Derivada*, y mezclar una en esta colección
  arrastraría discutiblemente el conjunto entero a ODbL, cambiando los términos
  para todo el que ya la esté usando. **Este proyecto excluye datos copyleft.**

## La lista blanca

`source.license` debe ser uno de estos identificadores SPDX. El CI rechaza
cualquier otro:

| Id SPDX | Fuente típica |
|---|---|
| `public-domain` | Natural Earth |
| `CC0-1.0` | Algunos portales nacionales de datos abiertos |
| `CC-BY-4.0` | Trabajo propio de geoBoundaries, IDE Chile |
| `CC-BY-3.0`, `CC-BY-3.0-IGO` | Límites de país de OCHA / HDX |
| `CC-BY-2.5` | Publicaciones nacionales antiguas |
| `Etalab-2.0` | Francia y sus departamentos de ultramar |
| `OGL-Canada-2.0` | Canadá |

## Verde — usar libremente

| Fuente | Licencia | Notas |
|---|---|---|
| [Natural Earth](https://www.naturalearthdata.com/) | Dominio público | **La opción correcta para ADM0.** Un archivo global de 12,7 MB cubre todos los países a 1:10m, incluidos territorios que geoBoundaries omite por completo. *"No hace falta permiso para usar Natural Earth."* |
| [IDE Chile / SUBDERE](https://www.geoportal.cl/) | CC BY | Cartografía oficial chilena. Aquí se usa para los tres niveles de Chile — ver la nota sobre DIFROL más abajo. |
| SDIs nacionales con licencias abiertas | Varía | Revisa los términos concretos; "datos de gobierno" no significa automáticamente "abiertos". |
| [HDX / OCHA COD-AB](https://data.humdata.org/) | Frecuentemente CC BY 3.0 IGO | La fuente aguas arriba que alimenta los mejores archivos de geoBoundaries. Ir directo da datos más frescos y una página de licencia por país más clara. |

## Ámbar — verificar la licencia archivo por archivo

| Fuente | Licencia | El problema |
|---|---|---|
| [geoBoundaries](https://www.geoboundaries.org/) `gbOpen` | **Por archivo** | Ver abajo — no es la fuente CC BY 4.0 simple que aparenta ser. |
| Wikidata / Wikimedia | CC0 para datos, varía para geometría | Los datos estructurados son CC0, pero la geometría importada puede arrastrar la licencia original. Rastrea la procedencia real. |

!!! warning "geoBoundaries no es CC BY 4.0 de forma uniforme"

    El *código y las obras derivadas propias* de geoBoundaries son CC BY 4.0, y
    el proyecto es excelente. Pero `gbOpen` es un **contenedor de licencias
    heterogéneas**, y su propio archivo de citación lo dice directamente:

    > Quien use archivos individuales de geoBoundaries debe además asegurarse
    > de citar las fuentes indicadas en los metadatos de cada archivo.

    Medido sobre las 129 entradas de América en `gbOpen`, **43 (33%) son
    copyleft** — 35 ODbL y 8 CC-BY-SA, casi todas derivadas de OpenStreetMap.
    Esas no se pueden usar aquí.

    Lee siempre el campo `boundaryLicense` de la respuesta de la API para el
    país **y el nivel** concretos que vayas a tomar. Chile es un buen ejemplo
    de por qué: su ADM1 y su ADM3 son CC BY 3.0 IGO, pero su ADM2 es ODbL.

    Usa únicamente la release `gbOpen`. `gbAuthoritative` es explícitamente no
    comercial, y `gbHumanitarian` tiene licencias por archivo no verificables.

## Rojo — no usar

| Fuente | Licencia | El problema |
|---|---|---|
| [GADM](https://gadm.org/license.html) | Propia, no comercial | **El error más común.** Los términos de GADM prohíben la redistribución y el uso comercial sin permiso previo. Es la fuente global más cómoda y el primer sitio donde mira un contribuidor bienintencionado — que es exactamente por qué hay que nombrarla explícitamente. |
| [OpenStreetMap](https://www.openstreetmap.org/) | ODbL 1.0 | Share-alike. Es lo que hace inutilizable aquí un tercio de geoBoundaries. Datos excelentes, términos incompatibles. |
| Capas base de Esri / ArcGIS Online | Propietaria | Licenciadas para uso dentro de productos Esri. No redistribuibles. |
| Geometría de Google Maps | Propietaria | La extracción está prohibida por los términos del servicio. |
| Proveedores comerciales (HERE, TomTom, …) | Propietaria | Nunca redistribuibles. |
| Cualquier dataset sin licencia declarada | — | La ausencia de licencia significa **todos los derechos reservados**, no dominio público. |

!!! danger "GADM es la trampa"

    GADM es completo, está bien mantenido, es gratis de descargar y **no es
    utilizable aquí**. Descargarlo para tu propio análisis está bien. Aportarlo
    a un repositorio público es una violación de licencia.

## Los huecos de cobertura son aceptables; las violaciones de licencia no

Excluir copyleft deja agujeros visibles — 15 países de América no tienen ADM1
aquí porque su ADM1 de geoBoundaries es copyleft (13 ODbL, 2 CC-BY-SA) y aún
no se ha encontrado una alternativa permisiva. Es el intercambio correcto.

Los huecos se registran en la [Hoja de ruta](../about/roadmap.md) como
"pendiente de fuente permisiva", y la forma de cerrar uno es encontrar un SDI
nacional o una publicación de HDX con términos aceptables, no relajar la regla.

## Registrar la fuente

Cada `manifest.json` debe llevar un bloque `source` completo:

```json
"source": {
  "name": "geoBoundaries",
  "url": "https://www.geoboundaries.org/countryDownloads.html",
  "license": "CC-BY-4.0",
  "retrieved": "2026-08-11"
}
```

- `license` **debe** ser un identificador SPDX de la lista blanca de arriba.
- `retrieved` importa: los límites cambian, y conocer la añada es como un
  consumidor decide si dos datasets se pueden combinar con seguridad.
- El campo `notes` del manifest (una sola línea) es donde van las condiciones
  que acompañan a una concesión — por ejemplo, la cartografía oficial chilena
  circula bajo la Resolución N°50 de 2019 de DIFROL, que pide que los
  productos derivados sean revisados igualmente. (No existe un campo
  `license_note` aparte.)

## Si tienes dudas

Abre un issue y pregunta antes de hacer el trabajo. Una duda de licencia
resuelta en diez minutos sale mucho más barata que una contribución que no se
puede mergear — o peor, una que se mergea y luego hay que retirar.

--8<-- "abbreviations.md"
