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
   en disputa, el campo `notes` del dataset lo registra e identifica las
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

Los datos actuales de Chile contienen dos:

- **El Territorio Antártico Chileno.** `Región de Magallanes y Antártica
  Chilena` está presente en ADM1. La reclamación antártica de Chile se solapa
  con las de Argentina y el Reino Unido, y el Tratado Antártico suspende todas
  ellas. La geometría refleja lo que publica BCN.
- **Isla de Pascua / Rapa Nui.** No está disputada entre estados, pero la
  denominación sí lo está localmente entre la forma española y la rapa nui. El
  campo `shapeName` lleva la forma de la fuente; los nombres alternativos
  pueden registrarse aparte.

Ninguno está anotado hoy en un manifiesto, porque todavía no existen
manifiestos. Ambos lo estarán cuando se reestructuren los datos.

## Nombres

Los topónimos están con frecuencia tan disputados como las líneas.

- `shapeName` lleva el nombre que usa la fuente, en el idioma local.
- `shapeNameEn` puede llevar un exónimo en inglés cuando sea de uso común.
- Los nombres alternativos o disputados van en `notes`, con su contexto.

El proyecto no renombra features para favorecer la forma de una comunidad sobre
la de otra. Cuando un nombre está genuinamente en disputa, se registran ambos y
se dice que lo están.

## Cambiar esta política

Mediante un issue y discusión pública. Es deliberadamente mecánica: una
política que exija juzgar quién tiene razón es una política que se relitigará
en cada pull request.

--8<-- "abbreviations.md"
