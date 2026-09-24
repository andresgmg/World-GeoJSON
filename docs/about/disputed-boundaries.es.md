# Política de fronteras disputadas

Cualquier repositorio de fronteras nacionales acabará recibiendo un pull
request que en realidad va de soberanía. Esta página existe para que la
respuesta esté escrita antes de que llegue el primero, en vez de improvisarse
bajo presión.

## La política

**Las fronteras siguen a la fuente declarada en la página de cada dataset. Este
proyecto no toma posición sobre soberanía.**

Cuatro consecuencias:

1. **La fuente siempre se declara.** Cada página de dataset y cada
   `manifest.json` dice de dónde vino la geometría y cuándo. Una frontera en
   este repositorio es una afirmación sobre esa fuente, no sobre quién tiene
   razón.
2. **La geometría no se edita para reflejar una reclamación.** Ni la de quien
   mantiene el proyecto, ni la de quien contribuye, ni la de un gobierno. Si la
   fuente traza una línea en cierto sitio, ahí está la línea.
3. **Los desacuerdos se documentan, no se resuelven.** Donde una frontera está
   en disputa, el campo `notes` del manifiesto lo registra e identifica las
   reclamaciones en conflicto. Se avisa a quien usa los datos de que hay una
   disputa; no se le dice quién gana.
4. **Las reclamaciones alternativas pueden publicarse en paralelo.** Cuando
   existe una delimitación alternativa bien documentada, puede añadirse como un
   dataset aparte con su propia atribución — nunca sobrescribiendo la
   existente.

## Por qué no simplemente "usar la posición de la ONU"

Es una sugerencia razonable y no funciona. La propia ONU no publica geometría
autoritativa de límites para zonas disputadas; sus productos cartográficos
llevan descargos de responsabilidad precisamente porque los estados miembros no
se ponen de acuerdo. Adoptar "la posición de la ONU" significaría elegir una
interpretación y llamarla neutral.

Remitirse a una fuente declarada, fechada y verificable es una afirmación más
débil, y ese es justamente el punto. Es una que este proyecto sí puede cumplir.

## Qué significa para quien contribuye

**Aceptable:**

- "Esta frontera no coincide con la fuente citada en el manifiesto." — una
  afirmación factual sobre los datos, verificable, y si es correcta, un bug.
- "La fuente X ha publicado una revisión con fecha Y." — una actualización.
- "Esta zona está disputada y el manifiesto no lo dice." — un hueco de
  documentación que conviene rellenar.

**No aceptable:**

- Editar geometría para reflejar una reclamación territorial.
- Cambiar la atribución de fuente por otra que trace la línea preferida, sin
  una razón sustantiva para preferir esa fuente.
- Issues que argumentan los méritos de una reclamación. Se cerrarán a
  comentarios; ver el
  [Código de conducta](../contributing/code-of-conduct.md).

## Casos ya presentes

- **El Territorio Antártico Chileno.** La región `Magallanes y de la Antártica
  Chilena` está presente en ADM1 y la provincia `Antártica Chilena` en ADM2,
  pero la comuna Antártica (`12202`) no: el paquete DPA 2023 de IDE Chile
  excluye la reclamación antártica, así que nada en los archivos actuales pasa
  de los 56,6°S. La reclamación de Chile se solapa con
  las de Argentina y el Reino Unido, y el Tratado Antártico suspende todas
  ellas. La geometría refleja lo que publica IDE Chile. (Los archivos
  heredados de la raíz, de BCN, son otro dataset.)
- **Isla de Pascua / Rapa Nui.** No está disputada entre estados, pero la
  denominación sí lo está localmente entre la forma española y la rapa nui. La
  comuna está presente en ADM3; `shapeName` lleva la forma de la fuente,
  `Isla de Pascua`.
- **Islas Malvinas / Falkland Islands (`FLK`) y Georgias del Sur y Sandwich
  del Sur (`SGS`).** La soberanía está en disputa entre el Reino Unido y
  Argentina. Ambos publican solo el contorno ADM0, de Natural Earth, cuya
  representación de facto se sigue. Los nombres de los manifiestos siguen
  ISO 3166 en cada idioma (`Falkland Islands` / `Islas Malvinas`);
  `shapeName` lleva la forma de Natural Earth. El `notes` de cada manifiesto
  registra la disputa y remite a esta página.

De los 55 manifiestos, `FLK` y `SGS` llevan hoy esa nota; el de Chile todavía
no.

## Nombres

Los topónimos están con frecuencia tan disputados como las líneas.

- `shapeName` lleva el nombre que usa la fuente, en el idioma local.
- Los `name.en` y `name.es` del manifiesto dan el nombre del territorio para
  mostrar en cada idioma; no se guarda ningún exónimo en inglés como propiedad
  de feature.
- Los nombres alternativos o disputados van en `notes`, con su contexto.

El proyecto no renombra features para favorecer la forma de una comunidad sobre
la de otra. Cuando un nombre está genuinamente en disputa, se registran ambos y
se dice que lo están.

## Cambiar esta política

Mediante un issue y discusión pública. Es deliberadamente mecánica: una
política que exija juzgar quién tiene razón es una política que se relitigará
en cada pull request.

--8<-- "abbreviations.md"
