# Editar la documentación

## Cambios pequeños

Pulsa el icono :material-pencil: en la parte superior de cualquier página.
GitHub abre el archivo fuente en su editor; commitea a una rama y abre un PR.
Sin configuración local.

## Levantar el sitio localmente

```powershell
git clone https://github.com/andresgmg/World-GeoJSON.git
cd World-GeoJSON
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-docs.txt
.\.venv\Scripts\python.exe -m mkdocs serve
```

Luego abre <http://127.0.0.1:8000>. Las ediciones se recargan solas.

!!! tip "¿Por qué `.\.venv\Scripts\python.exe -m mkdocs` y no `mkdocs`?"

    Llamar al intérprete directamente funciona con independencia de la
    política de ejecución de PowerShell. `.\.venv\Scripts\Activate.ps1` está
    bloqueado por defecto en muchas instalaciones de Windows, y el error
    resultante es lo bastante confuso como para detener por completo a quien
    contribuye por primera vez.

    Si prefieres un shell activado:

    ```powershell
    Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
    .\.venv\Scripts\Activate.ps1
    mkdocs serve
    ```

Antes de abrir un PR:

```powershell
.\.venv\Scripts\python.exe -m mkdocs build --strict
```

`--strict` convierte los avisos en errores — enlaces internos rotos, páginas
fuera del nav. El CI ejecuta el mismo comando, así que si pasa localmente,
pasa allí.

## Notas sobre Windows

**Python de Microsoft Store.** Si `python` resuelve a
`…\WindowsApps\python.exe`, es la versión de la Store. Funciona, pero sus alias
de ejecución de aplicaciones confunden a veces a `venv` y no trae el lanzador
`py`. Instalar Python desde python.org evita toda una categoría de errores
raros.

**OneDrive.** Si tu clon vive dentro de una carpeta sincronizada por OneDrive,
excluye `.venv/` y `site/` de la sincronización. Si no, OneDrive intentará
subir miles de archivos del entorno virtual y volver a subir el sitio
construido tras cada build, lo que provoca errores de bloqueo "archivo en uso"
a media compilación. Clic derecho en cada carpeta → desmarcar **Mantener
siempre en este dispositivo**, o mejor, mueve el clon fuera de OneDrive.

Si te topas con bucles de recompilación, `mkdocs serve --no-livereload` es la
salida de emergencia.

## Cómo está organizado el sitio

| Ruta | Qué es |
|---|---|
| `docs/` | Páginas escritas a mano. **No contiene datos.** |
| `includes/abbreviations.md` | Tooltips del glosario, añadidos a cada página |
| `pipeline/mkdocs_hook.py` | El hook de MkDocs que genera las páginas del catálogo desde los manifiestos en cada build. Reexporta `wgj.catalog` del paquete del pipeline, así que construir la documentación no necesita nada más que `requirements-docs.txt` |
| `mkdocs.yml` | Configuración y navegación |
| `data/` | El árbol GeoJSON — deliberadamente fuera de `docs/` |

!!! warning "Nunca muevas datos dentro de `docs/`"

    MkDocs copia todo lo que hay bajo `docs_dir` al sitio construido, tal cual,
    sin comprobar tamaños. Un solo archivo de 70 MB puesto ahí se publicaría en
    GitHub Pages en el siguiente despliegue.

## Las páginas del catálogo se generan

Las páginas bajo **Catálogo** no existen en disco. `wgj.catalog`, conectado a
través del hook `pipeline/mkdocs_hook.py`, las construye desde el
`manifest.json` de cada dataset en cada build.

Para corregir un dato de una página de catálogo, **edita el manifiesto**. El
botón de edición de la página ya apunta ahí.

El generador no debe abrir nunca un archivo `.geojson` — solo lee manifiestos.
Esa restricción es lo que mantiene los builds rápidos y lo que permite al CI
hacer checkout del repositorio sin ningún archivo de datos.

## Contenido bilingüe

El sitio está en inglés por defecto con traducciones al español, usando el
esquema de sufijo de archivo:

```
docs/index.md      → inglés
docs/index.es.md   → español
```

Un `.es.md` que falte cae a la página en inglés en lugar de dar 404, así que
traducir parcialmente está bien. Traducir una página significa añadir el
archivo hermano `.es.md`; las etiquetas de navegación se traducen en
`mkdocs.yml`, bajo `nav_translations`.

Las páginas de catálogo generadas están solo en inglés por ahora — son
mayormente tablas, números y URLs.

## Estilo

- Escribe para alguien que sabe de GIS pero no conoce este proyecto.
- Prefiere un ejemplo concreto a una descripción abstracta.
- Documenta el estado actual con honestidad, incluidas las partes que están
  mal. Varias páginas describen defectos conocidos de los datos existentes; es
  deliberado y conviene mantenerlo.
- Usa admoniciones para trampas reales, no para dar énfasis.

--8<-- "abbreviations.md"
