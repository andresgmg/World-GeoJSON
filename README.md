# World GeoJSON

Open, versioned GeoJSON administrative boundaries — starting with Chile,
growing toward every country on Earth, and eventually the Moon and Mars.

**📖 Documentation: <https://andresgmg.github.io/World-GeoJSON/>**

*[Versión en español abajo.](#world-geojson-es)*

---

## Quick start

```js
const url =
  "https://raw.githubusercontent.com/andresgmg/World-GeoJSON/main/regiones.geojson";

const regions = await fetch(url).then((r) => r.json());
console.log(regions.features.length); // 16
```

## What is here

| File | Features | Size |
|---|---|---|
| `regiones.geojson` | 16 Chilean regions (ADM1) | 3.5 MB |
| `comunas.geojson` | 343 Chilean communes (ADM3) | 70 MB |

Source: Biblioteca del Congreso Nacional de Chile (BCN) / IDE Chile.

> [!WARNING]
> `comunas.geojson` is 70 MB. Do not load it directly in a browser — it will
> crash the tab on mobile. See
> [Get started](https://andresgmg.github.io/World-GeoJSON/get-started/) for
> simplification recipes.

> [!NOTE]
> `comunas.json` and `regiones.json` are byte-identical duplicates of the
> `.geojson` files and are **deprecated**. Use the `.geojson` paths.

## Where things are going

The repository is being restructured from a flat, Chile-only data drop into a
documented, multi-country catalog:

```
data/{body}/{ISO3}/{ISO3}_{LEVEL}.geojson
```

The conventions that make that possible — folder layout, administrative
levels, property schema, CRS policy, licensing rules — are written up in the
[Reference](https://andresgmg.github.io/World-GeoJSON/reference/) section
**before** the data grows, so that contributions arrive in a consistent shape.

The current root-level files stay where they are, unchanged, for one full
major version. Existing links will not break without notice. See
[Versioning](https://andresgmg.github.io/World-GeoJSON/about/versioning/).

## Contributing

Country contributions are welcome. **Check the licence of your source first** —
[Approved sources](https://andresgmg.github.io/World-GeoJSON/contributing/sources/)
lists what is usable and what is not. GADM, the most convenient global source,
is not.

Then follow
[Add a country](https://andresgmg.github.io/World-GeoJSON/contributing/add-a-country/).

## Licence

Code is [MIT](LICENSE). **Data is licensed per source** — see
[Licensing & attribution](https://andresgmg.github.io/World-GeoJSON/about/license/).

---

<a name="world-geojson-es"></a>

# World GeoJSON <sub>(español)</sub>

Límites administrativos en GeoJSON, abiertos y versionados — empezando por
Chile, con el objetivo de cubrir todos los países del mundo y, más adelante,
la Luna y Marte.

**📖 Documentación: <https://andresgmg.github.io/World-GeoJSON/es/>**

## Qué hay aquí

| Archivo | Features | Tamaño |
|---|---|---|
| `regiones.geojson` | 16 regiones de Chile (ADM1) | 3,5 MB |
| `comunas.geojson` | 343 comunas de Chile (ADM3) | 70 MB |

Fuente: Biblioteca del Congreso Nacional de Chile (BCN) / IDE Chile.

> [!WARNING]
> `comunas.geojson` pesa 70 MB. No lo cargues directamente en el navegador —
> en móvil revienta la pestaña.

> [!NOTE]
> `comunas.json` y `regiones.json` son duplicados byte a byte de los
> `.geojson` y están **obsoletos**. Usa las rutas `.geojson`.

## Hacia dónde va

El repositorio se está reestructurando desde un volcado plano de datos solo de
Chile hacia un catálogo documentado y multipaís. Las convenciones que lo hacen
posible — estructura de carpetas, niveles administrativos, esquema de
propiedades, política de CRS, reglas de licencias — se escriben **antes** de
que crezcan los datos, para que las contribuciones lleguen con una forma
consistente.

Los archivos actuales en la raíz se mantienen sin cambios durante una versión
mayor completa. Los enlaces existentes no se romperán sin aviso.

## Contribuir

**Verifica primero la licencia de tu fuente.** GADM, la fuente global más
cómoda, no es utilizable aquí.

## Licencia

El código es [MIT](LICENSE). **Los datos se licencian según su fuente.**
