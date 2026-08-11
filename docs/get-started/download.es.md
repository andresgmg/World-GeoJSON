# Descarga y CDN

Hay tres formas de obtener un archivo. No son intercambiables.

## CDN de jsDelivr

Rápido, cacheado globalmente, con cabeceras CORS correctas. **Lo mejor para
navegadores.**

```
https://cdn.jsdelivr.net/gh/andresgmg/World-GeoJSON@main/<ruta>
```

!!! danger "Límite duro de 20 MB"

    jsDelivr se niega a servir archivos de más de **20 MB**. El archivo de
    comunas de Chile pesa 70 MB, así que la ruta CDN sencillamente no existe
    para él — obtienes un error, no una descarga lenta. Usa raw GitHub para
    archivos grandes, o los archivos de preview simplificados, que están
    construidos precisamente para quedar muy por debajo de este límite.

**Fija una etiqueta en producción.** `@main` sigue la rama por defecto, así que
una corrección de límites que se mergee aguas arriba cambia lo que recibe tu
aplicación, en silencio.

=== "Fijado (recomendado)"

    ```
    https://cdn.jsdelivr.net/gh/andresgmg/World-GeoJSON@v1.0.0/<ruta>
    ```

=== "Última versión"

    ```
    https://cdn.jsdelivr.net/gh/andresgmg/World-GeoJSON@main/<ruta>
    ```

## Raw GitHub

```
https://raw.githubusercontent.com/andresgmg/World-GeoJSON/main/<ruta>
```

Funciona con archivos de cualquier tamaño y envía
`Access-Control-Allow-Origin: *`, así que `fetch` desde el navegador funciona.
Pero **no es un CDN**: sin caché de borde, y con límite de peticiones. Bien
para desarrollo, scripts y descargas desde servidor; mal para tráfico de
navegador en producción.

## Git

Para trabajar con los datos localmente o en un pipeline.

El tamaño empaquetado del repositorio es de solo unos 8,5 MB — el JSON con
indentación comprime aproximadamente 9:1 — así que un clon completo es más
rápido de lo que sugieren los tamaños de archivo. Lo lento es hacer checkout de
148 MB de working tree que quizá no necesitas.

=== "Todo"

    ```bash
    git clone https://github.com/andresgmg/World-GeoJSON.git
    ```

=== "Un país (sparse)"

    ```bash
    git clone --filter=blob:none --sparse https://github.com/andresgmg/World-GeoJSON.git
    cd World-GeoJSON
    git sparse-checkout set data/earth/CHL
    ```

    `--filter=blob:none` hace que el clon obtenga el contenido de los archivos
    de forma perezosa, así que solo descargas los blobs de los que realmente
    haces checkout.

=== "Solo metadatos"

    ```bash
    git clone --filter=blob:none --no-checkout https://github.com/andresgmg/World-GeoJSON.git
    cd World-GeoJSON
    git sparse-checkout set --no-cone '/*' '!/data/**' '/data/**/manifest.json'
    git checkout main
    ```

    Obtiene todos los manifiestos sin un solo archivo GeoJSON. Es exactamente
    lo que hace el CI de este sitio — el build de documentación solo lee
    manifiestos.

## Checksums

Cada página de dataset publica un SHA-256 de su archivo. Verifica una descarga
con:

=== "PowerShell"

    ```powershell
    Get-FileHash .\CHL_ADM1.geojson -Algorithm SHA256
    ```

=== "Bash"

    ```bash
    sha256sum CHL_ADM1.geojson
    ```

!!! warning "Los finales de línea romperán tu checksum"

    Git normaliza los finales de línea al hacer checkout. En Windows, un
    `.geojson` con CRLF es un byte por línea más grande que el mismo archivo en
    Linux — para el archivo de comunas de Chile eso son 1,8 MB de diferencia, y
    un hash completamente distinto.

    El `.gitattributes` del repositorio fija `*.geojson` a LF precisamente para
    que los checksums publicados coincidan en todas partes. Si tu hash no
    cuadra, revisa `git config core.autocrlf` antes de suponer que el archivo
    está corrupto.

--8<-- "abbreviations.md"
