#!/usr/bin/env node
/**
 * Generate simplified preview files for the catalog maps.
 *
 *     node scripts/make_previews.mjs data/earth/CHL
 *     node scripts/make_previews.mjs            # every country
 *
 * Full-resolution data cannot be displayed in a browser, and jsDelivr refuses
 * files over 20 MB, so every dataset ships a small companion used only by the
 * map on its catalog page. See docs/contributing/previews.md.
 *
 * Split levels are merged before simplification so the preview shows the whole
 * country rather than one region.
 */

import { execFileSync } from "node:child_process";
import {
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { basename, dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const REPO = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const DATA = join(REPO, "data", "earth");

const TARGET_BYTES = 800 * 1024; // aim below this
const HARD_LIMIT = 2 * 1024 * 1024; // CI fails above this
const MIN_PERCENTAGE = 0.2;

const LEVEL_DIR = /^ADM\d$|^QUAD$/;
const LEVEL_FILE = /^([A-Z]{3,4})_(ADM\d|QUAD)\.geojson$/;

// Run the pinned copy's entry script with the current node binary.
//
// Not node_modules/.bin/mapshaper: on Windows that is a .cmd shim, and
// execFileSync cannot spawn a .cmd without a shell — it fails with
// `status: null, pid: 0`, which reads like a missing binary rather than a
// spawn restriction. Invoking the .js directly sidesteps the shim entirely
// and avoids shell:true, which concatenates arguments instead of escaping
// them and would mangle any path containing a space.
const ENTRY = join(REPO, "node_modules", "mapshaper", "bin", "mapshaper");
const HAVE_LOCAL = existsSync(ENTRY);
const NPX = process.platform === "win32" ? "npx.cmd" : "npx";

function mapshaper(args) {
  const [bin, prefix] = HAVE_LOCAL
    ? [process.execPath, [ENTRY]]
    : [NPX, ["-y", "mapshaper"]];
  execFileSync(bin, [...prefix, ...args], {
    stdio: ["ignore", "pipe", "pipe"],
  });
}

function mb(n) {
  return n >= 1024 * 1024
    ? `${(n / 1024 / 1024).toFixed(1)} MB`
    : `${Math.round(n / 1024)} KB`;
}

/**
 * Simplify until the result fits the target, then verify nothing was lost.
 *
 * `keep-shapes` stops whole polygons collapsing, but a multipolygon can still
 * shed small members — so the feature count is compared against the source and
 * a mismatch is a hard error, not a warning.
 */
function buildPreview(inputs, dest, sourceFeatures) {
  const combine = inputs.length > 1 ? ["combine-files", "-merge-layers", "force"] : [];

  // mapshaper drops a GeoJSON Feature's `id` as soon as the attribute table
  // is edited (-filter-fields, -each). `id-field=__id` on import copies the
  // id into a property that survives the edits; restoreIds() moves it back.
  const write = (pct) => {
    mapshaper([
      "-i",
      ...inputs,
      "id-field=__id",
      ...combine,
      "-simplify",
      `percentage=${pct}%`,
      "keep-shapes",
      "-filter-fields",
      "shapeName,shapeISO,shapeType,__id",
      "-o",
      "precision=0.0001",
      "bbox",
      "format=geojson",
      dest,
    ]);
    return restoreIds(dest);
  };

  let pct = 5;
  let size = write(pct);
  while (size > TARGET_BYTES && pct > MIN_PERCENTAGE) {
    pct = Math.max(MIN_PERCENTAGE, pct / 2);
    size = write(pct);
  }

  const out = JSON.parse(readFileSync(dest, "utf8"));
  const got = out.features.length;
  if (got !== sourceFeatures) {
    throw new Error(
      `${basename(dest)}: simplification dropped geometry — ` +
        `${got} features out of ${sourceFeatures}. Raise the percentage.`
    );
  }
  if (size > HARD_LIMIT) {
    throw new Error(
      `${basename(dest)}: ${mb(size)} exceeds the ${mb(HARD_LIMIT)} budget ` +
        `even at ${pct}%.`
    );
  }
  return { size, pct, features: got };
}

/**
 * Move the `__id` property back to the Feature id and rewrite the file in the
 * same canonical layout as the full-resolution data: one feature per line,
 * `id` before `properties`, no trailing newline. Returns the new size.
 */
function restoreIds(dest) {
  const out = JSON.parse(readFileSync(dest, "utf8"));
  const lines = out.features.map((f) => {
    const { __id, ...props } = f.properties;
    if (__id === undefined) {
      throw new Error(`${basename(dest)}: a feature has no id — run finalize_geojson.py first`);
    }
    return JSON.stringify({ type: "Feature", id: __id, properties: props, geometry: f.geometry });
  });
  const text =
    `{"type":"FeatureCollection","bbox":${JSON.stringify(out.bbox)},"features":[\n` +
    lines.join(",\n") +
    "\n]}";
  writeFileSync(dest, text);
  return Buffer.byteLength(text);
}

function countFeatures(paths) {
  let n = 0;
  for (const p of paths) {
    n += JSON.parse(readFileSync(p, "utf8")).features.length;
  }
  return n;
}

function processCountry(dir) {
  const code = basename(dir);
  const previewDir = join(dir, "preview");
  const levels = new Map();

  // Sorted explicitly: readdirSync order is filesystem-defined, and NTFS
  // (case-insensitive) and ext4 (bytewise) disagree on where a lowercase
  // `unassigned.geojson` sits among uppercase `US-XX.geojson` parts. The
  // merge order decides feature order in the preview, so the preview bytes
  // must not depend on which machine generated them.
  for (const name of readdirSync(dir).sort()) {
    const full = join(dir, name);
    const m = LEVEL_FILE.exec(name);
    if (m && statSync(full).isFile()) {
      // A combined file wins over the parts when both exist: it holds the
      // same features and a single input is the cheaper merge. Parts are
      // the fallback for levels published without one (Brazil ADM2).
      levels.set(m[2], [full]);
    } else if (statSync(full).isDirectory() && LEVEL_DIR.test(name)) {
      const parts = readdirSync(full)
        .filter((f) => f.endsWith(".geojson"))
        .sort()
        .map((f) => join(full, f));
      if (parts.length && !levels.has(name)) levels.set(name, parts);
    }
  }

  if (!levels.size) return;
  mkdirSync(previewDir, { recursive: true });

  for (const [level, inputs] of [...levels].sort()) {
    const dest = join(previewDir, `${code}_${level}.preview.geojson`);
    const src = countFeatures(inputs);
    const { size, pct, features } = buildPreview(inputs, dest, src);
    console.log(
      `  ${code} ${level.padEnd(5)} ${String(features).padStart(5)} features  ` +
        `${mb(size).padStart(8)}  at ${pct}%`
    );
  }
}

const args = process.argv.slice(2);
const targets = args.length
  ? args.map((a) => resolve(REPO, a))
  : readdirSync(DATA)
      .sort()
      .map((d) => join(DATA, d))
      .filter((d) => statSync(d).isDirectory());

if (!targets.length) {
  console.error("no country directories found under data/earth/");
  process.exit(1);
}

for (const t of targets) {
  if (!existsSync(t)) {
    console.error(`missing: ${t}`);
    process.exit(1);
  }
  processCountry(t);
}
