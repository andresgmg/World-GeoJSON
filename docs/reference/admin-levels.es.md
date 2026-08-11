# Niveles administrativos

## Definiciones

| Nivel | Significado |
|---|---|
| **ADM0** | El contorno del país o cuerpo |
| **ADM1** | Divisiones de primer nivel |
| **ADM2** | Divisiones de segundo nivel |
| **ADM3** | Divisiones de tercer nivel |

Siguen la semántica de [geoBoundaries](https://www.geoboundaries.org/) y GADM,
para que los datasets de este proyecto puedan cruzarse con los suyos sin paso
de traducción.

## Los números son estructurales, no semánticos

Es la regla que más confusión causa, así que conviene decirla claro: **ADM1 no
significa "provincia".** Significa "el primer nivel de subdivisión que tenga
este país, se llame como se llame". El término local se registra aparte, en el
manifiesto.

| País | ADM1 | ADM2 | ADM3 |
|---|---|---|---|
| Chile | Región | Provincia | Comuna |
| Argentina | Provincia | Departamento | Municipio |
| Francia | Región | Departamento | Comuna |
| Estados Unidos | Estado | Condado | — |
| Japón | Prefectura | Municipio | — |

Chile ilustra bien por qué la numeración tiene que ser estructural. Las comunas
son el nivel con el que todo el mundo trabaja en la práctica — son la unidad
del censo, de las elecciones y del gobierno local — pero son **ADM3**, no ADM2,
porque entre ellas y las regiones hay un nivel de provincia. Numerarlas como
ADM2 por ser el nivel más prominente haría que los niveles de Chile no
concordaran con los de ningún otro país, y rompería cualquier consulta
multipaís que agrupe por nivel.

!!! info "Cuando los niveles de un país no encajan limpiamente"

    Pasa a menudo. Algunos países tienen jerarquías solapadas, ciudades con
    estatus especial que se saltan un nivel, o divisiones que cambiaron hace
    poco. Registra lo que modela la fuente, describe el desajuste en el campo
    `notes` del manifiesto, y no reorganices la jerarquía en silencio para que
    parezca ordenada.

## Expectativas de cobertura

- **ADM0 y ADM1 son la prioridad.** Son los niveles que más consumidores
  necesitan y los que están disponibles con licencia abierta de forma más
  fiable.
- **ADM2 donde exista una buena fuente.**
- **ADM3 es oportunista.** Muy pocos países lo publican abiertamente, y los
  tamaños de archivo crecen rápido.

Una entrada de país con solo ADM1 es bienvenida. La cobertura parcial es normal
y el catálogo muestra exactamente qué niveles existen para cada entrada.

## El anidamiento debe ser consistente

Cuando se aportan varios niveles de un país:

- Cada feature ADM2 **debe** anidar dentro de exactamente una feature ADM1.
- La unión de las features ADM1 **debería** igualar el contorno ADM0, dentro de
  la tolerancia de la geometría de origen.
- Las features **deben** llevar una referencia a su padre — ver
  [Esquema de propiedades](schema.md).

No mezcles añadas. Los límites cambian: un archivo ADM1 de 2019 combinado con
uno ADM2 de 2024 no anidará, y el desajuste es difícil de detectar a simple
vista. Registra la añada en el manifiesto.

## El hueco de Chile

Los datos actuales de Chile tienen un agujero documentado que conviene conocer:

- Hay 343 comunas; oficialmente existen **346**. Las tres que faltan son las
  omisiones habituales de esta fuente — Antártica, Isla de Pascua y Juan
  Fernández.
- **Falta ADM2 por completo.** La propiedad `Provincia` está poblada en cada
  feature de comuna, así que el nivel intermedio se puede *leer*, pero no
  existe archivo de límites provinciales y por tanto no se puede dibujar. Chile
  salta hoy de ADM1 directamente a ADM3.

Ambos están en la [Hoja de ruta](../about/roadmap.md).

--8<-- "abbreviations.md"
