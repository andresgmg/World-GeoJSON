/* --------------------------------------------------------------------------
   World GeoJSON — catalog preview maps

   Initialises a Leaflet map for every <div class="geojson-map" data-src="…">
   that wgj.catalog (the MkDocs hook, pipeline/mkdocs_hook.py) emits on a dataset page.

   Only *preview* files are ever loaded here. A full-resolution dataset is tens
   of megabytes and would crash a mobile tab; see docs/contributing/previews.md.
   -------------------------------------------------------------------------- */

(function () {
  "use strict";

  var EARTH_TILES = "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png";
  var EARTH_ATTR =
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> ' +
    "contributors &copy; <a href=\"https://carto.com/attributions\">CARTO</a>";

  function basemap(map, body) {
    if (body === "earth" || !body) {
      L.tileLayer(EARTH_TILES, { maxZoom: 12, attribution: EARTH_ATTR }).addTo(map);
      return;
    }
    // No Web Mercator tile service exists for planetary bodies. USGS
    // Astrogeology serves equirectangular WMS, which is why the map is built
    // with L.CRS.EPSG4326 for these. See docs/reference/planetary.md.
    L.tileLayer
      .wms(
        "https://planetarymaps.usgs.gov/cgi-bin/mapserv?map=/maps/" +
          body +
          "/" +
          body +
          "_simp_cyl.map",
        {
          layers: body === "mars" ? "MDIM21_color" : "LROC_WAC",
          format: "image/png",
          attribution: "USGS Astrogeology Science Center",
        }
      )
      .addTo(map);
  }

  function label(feature) {
    var p = feature.properties || {};
    return p.shapeName || p.name || p.Comuna || p.Region || null;
  }

  function initOne(el) {
    var body = el.getAttribute("data-body") || "earth";
    var src = el.getAttribute("data-src");
    if (!src) return;

    var map = L.map(el, {
      // Never hijack page scroll; the user has to click in first.
      scrollWheelZoom: false,
      crs: body === "earth" ? L.CRS.EPSG3857 : L.CRS.EPSG4326,
    });
    map.on("click", function () {
      map.scrollWheelZoom.enable();
    });

    basemap(map, body);

    fetch(src)
      .then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(function (data) {
        var layer = L.geoJSON(data, {
          style: { weight: 1, color: "#00695c", fillColor: "#00695c", fillOpacity: 0.12 },
          onEachFeature: function (feature, lyr) {
            var name = label(feature);
            if (name) lyr.bindTooltip(String(name), { sticky: true });
            lyr.on({
              mouseover: function () {
                lyr.setStyle({ fillOpacity: 0.35 });
              },
              mouseout: function () {
                lyr.setStyle({ fillOpacity: 0.12 });
              },
            });
          },
        }).addTo(map);

        var bounds = layer.getBounds();
        if (bounds.isValid()) map.fitBounds(bounds, { padding: [8, 8] });
        else map.setView([0, 0], 2);
      })
      .catch(function (err) {
        el.innerHTML =
          '<p class="geojson-map__error">Preview unavailable (' +
          String(err.message || err) +
          "). Use the download links below.</p>";
      });
  }

  function initMaps() {
    if (typeof L === "undefined") return;
    var nodes = document.querySelectorAll(".geojson-map:not([data-ready])");
    for (var i = 0; i < nodes.length; i++) {
      nodes[i].setAttribute("data-ready", "1");
      initOne(nodes[i]);
    }
  }

  // Material's instant navigation exposes `document$`. Subscribing to it as
  // well as DOMContentLoaded means the maps keep working if
  // navigation.instant is ever enabled — under instant nav, DOMContentLoaded
  // never fires again after the first page.
  if (typeof document$ !== "undefined" && document$.subscribe) {
    document$.subscribe(initMaps);
  } else if (document.readyState !== "loading") {
    initMaps();
  } else {
    document.addEventListener("DOMContentLoaded", initMaps);
  }
})();
