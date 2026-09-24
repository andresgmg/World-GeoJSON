"""Chile — IDE Chile / SUBDERE División Política Administrativa 2023."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from wgj.geojson_io import feature_count
from wgj.mapshaper import js_expr, js_lookup, run_mapshaper
from wgj.paths import CACHE, earth
from wgj.registry import iso3166_2
from wgj.simplify import SIZE_BUDGET, simplify
from wgj.sources import STANDARD_FIELDS


def build_chile() -> list[dict]:
    """Chile comes from IDE Chile DPA 2023, not geoBoundaries.

    geoBoundaries' Chile is a three-source mix whose ADM2 (provinces) is
    OpenStreetMap under ODbL — copyleft, and therefore excluded from this
    repository. DPA 2023 gives all three tiers from one CC BY source, in one
    vintage, with CUT codes already stored as zero-padded strings.
    """
    src_dir = CACHE / "DPA_2023"
    if not src_dir.exists():
        raise SystemExit(f"missing {src_dir} — run `wgj fetch --iso3 CHL` first")

    out_dir = earth() / "CHL"
    out_dir.mkdir(parents=True, exist_ok=True)
    codes = {k: v for k, v in iso3166_2()["CHL"].items() if not k.startswith("_")}
    results: list[dict] = []

    # --- ADM1: regions -----------------------------------------------------
    print("  ADM1 (regiones)")
    adm1_out = out_dir / "CHL_ADM1.geojson"
    iso_lookup = js_lookup(codes)
    simp = simplify(
        src_dir / "REGIONES" / "REGIONES_v1.shp",
        adm1_out,
        extra=[
            "-each",
            js_expr(
                {
                    "shapeName": "REGION",
                    "shapeISO": f"({iso_lookup})[CUT_REG] || CUT_REG",
                    "shapeGroup": "'CHL'",
                    "shapeType": "'ADM1'",
                    "src_cut_reg": "CUT_REG",
                    "src_superficie_km2": "SUPERFICIE",
                }
            ),
            "-filter-fields",
            ",".join([*STANDARD_FIELDS[:4], "src_cut_reg", "src_superficie_km2"]),
        ],
    )
    results.append({"level": "ADM1", "path": adm1_out, "simplification": simp})

    # --- ADM2: provinces ---------------------------------------------------
    print("  ADM2 (provincias)")
    adm2_out = out_dir / "CHL_ADM2.geojson"
    simp = simplify(
        src_dir / "PROVINCIAS" / "PROVINCIAS_v1.shp",
        adm2_out,
        extra=[
            "-each",
            js_expr(
                {
                    "shapeName": "PROVINCIA",
                    "shapeISO": "CUT_PROV",
                    "shapeGroup": "'CHL'",
                    "shapeType": "'ADM2'",
                    "parentISO": f"({iso_lookup})[CUT_REG] || CUT_REG",
                    "src_cut_prov": "CUT_PROV",
                    "src_cut_reg": "CUT_REG",
                    "src_region": "REGION",
                }
            ),
            "-filter-fields",
            ",".join([*STANDARD_FIELDS, "src_cut_prov", "src_cut_reg", "src_region"]),
        ],
    )
    results.append({"level": "ADM2", "path": adm2_out, "simplification": simp})

    # --- ADM3: communes, split by region ----------------------------------
    print("  ADM3 (comunas, split by region)")
    adm3_dir = out_dir / "ADM3"
    if adm3_dir.exists():
        shutil.rmtree(adm3_dir)
    adm3_dir.mkdir(parents=True)

    with tempfile.TemporaryDirectory() as tmp:
        combined = Path(tmp) / "CHL_ADM3.geojson"
        simp = simplify(
            src_dir / "COMUNAS" / "COMUNAS_v1.shp",
            combined,
            extra=[
                "-each",
                js_expr(
                    {
                        "shapeName": "COMUNA",
                        "shapeISO": "CUT_COM",
                        "shapeGroup": "'CHL'",
                        "shapeType": "'ADM3'",
                        # Immediate parent is the province, per the official
                        # hierarchy Región > Provincia > Comuna. The file the
                        # feature lands in is keyed by region — see naming.md.
                        "parentISO": "CUT_PROV",
                        "adm1ISO": f"({iso_lookup})[CUT_REG] || CUT_REG",
                        "src_cut_com": "CUT_COM",
                        "src_cut_prov": "CUT_PROV",
                        "src_cut_reg": "CUT_REG",
                        "src_provincia": "PROVINCIA",
                        "src_region": "REGION",
                    }
                ),
                "-filter-fields",
                ",".join(
                    [
                        *STANDARD_FIELDS,
                        "adm1ISO",
                        "src_cut_com",
                        "src_cut_prov",
                        "src_cut_reg",
                        "src_provincia",
                        "src_region",
                    ]
                ),
            ],
        )

        total = feature_count(combined)
        print(f"      {total} communes total")

        # Split by region. mapshaper names outputs after the split value.
        run_mapshaper(
            [
                str(combined),
                "-split",
                "adm1ISO",
                "-o",
                "precision=0.000001",
                "bbox",
                "format=geojson",
                str(adm3_dir),
            ]
        )

        parts = []
        for f in sorted(adm3_dir.glob("*.json")) + sorted(adm3_dir.glob("*.geojson")):
            code = f.stem
            target = adm3_dir / f"{code}.geojson"
            if f != target:
                f.rename(target)
            parts.append(target)

        combined_size = combined.stat().st_size
        # Only publish a whole-country file when it fits the CDN ceiling.
        if combined_size <= SIZE_BUDGET:
            shutil.copyfile(combined, out_dir / "CHL_ADM3.geojson")
            print(f"      combined file published ({combined_size / 1024 / 1024:.1f} MB)")
        else:
            print(
                f"      combined file omitted ({combined_size / 1024 / 1024:.1f} MB "
                f"exceeds the {SIZE_BUDGET / 1024 / 1024:.0f} MB CDN budget)"
            )

    results.append({"level": "ADM3", "path": adm3_dir, "simplification": simp, "split": True})
    return results
