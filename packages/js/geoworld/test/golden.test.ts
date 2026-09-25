/**
 * The JavaScript client must produce fixtures/expected/fixtures.json byte for
 * byte, exactly as the Python client does (packages/python/geoworld/tests/goldens.py).
 */
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { test } from "node:test";

import type { GeoWorld } from "../src/index.js";
import { FIXTURES, client } from "./helpers.js";

const SEARCHES: [string, string | null][] = [
  ["santo", null],
  ["las", "ADM2"],
  ["san", "ADM2"],
  ["DO-01", "ADM1"],
  ["PERAVIA", null],
  ["compostéla", "ADM2"],
  ["", null],
];

function sortKeys(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(sortKeys);
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.keys(value as Record<string, unknown>)
        .sort()
        .map((k) => [k, sortKeys((value as Record<string, unknown>)[k])]),
    );
  }
  return value;
}

/** Same as Python's `json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"`. */
export function canonical(value: unknown): string {
  return `${JSON.stringify(sortKeys(value), null, 2)}\n`;
}

async function count(iterable: AsyncIterable<unknown>): Promise<number> {
  let n = 0;
  for await (const _ of iterable) n += 1;
  return n;
}

export async function build(world: GeoWorld): Promise<unknown> {
  const dom = await world.country("DOM");
  const root = "DOM:ADM0:DOM";
  const tree: Record<string, Record<string, string[]>> = { [root]: {} };
  for (const adm1 of await world.children(root)) {
    tree[root]![adm1.id] = (await world.children(adm1.id)).map((c) => c.id);
  }
  const parents = {
    "DOM:ADM0:DOM": null,
    "DOM:ADM1:DO-02": (await world.parent("DOM:ADM1:DO-02"))!.id,
    "DOM:ADM2:DO-02.estebania": (await world.parent("DOM:ADM2:DO-02.estebania"))!.id,
  };
  const leaf = await world.find("DOM:ADM2:DO-02.guayabal");
  const levels = await world.levels("DOM");
  const bbox: Record<string, unknown> = {};
  const featureCounts: Record<string, number> = {};
  for (const level of levels) {
    bbox[level] = await world.bbox("DOM", level);
    featureCounts[level] = await count(world.features("DOM", level));
  }
  const search: Record<string, string[]> = {};
  for (const [text, level] of SEARCHES) {
    search[`${text}|${level ?? "*"}`] = (await world.search(text, "DOM", level ?? undefined)).map((f) => f.id);
  }
  return {
    countries: await world.countries(),
    totals: (await world.index()).totals,
    dom: {
      levels,
      municipal_level: dom.municipal_level,
      terms: dom.terms ?? null,
      parts: await world.parts("DOM", "ADM2"),
      paths: {
        ADM0: (await world.dataset("DOM", "ADM0")).path,
        ADM1_preview: (await world.dataset("DOM", "ADM1")).preview,
        ADM2_parts: (await world.dataset("DOM", "ADM2")).parts!.map((p) => p.path),
      },
      bbox,
      feature_counts: featureCounts,
      preview_ids: (await world.preview("DOM", "ADM1")).features.map((f) => f.id).slice(0, 5),
      tree,
      parents,
      leaf: {
        id: leaf.id,
        properties: leaf.properties,
        bbox: leaf.bbox ?? null,
        geometry_type: leaf.geometry.type,
      },
      search,
    },
  };
}

test("matches the cross-language golden", async () => {
  const expected = await readFile(join(FIXTURES, "expected", "fixtures.json"), "utf8");
  assert.equal(canonical(await build(client())), expected, "regenerate with: python packages/python/geoworld/tests/goldens.py");
});
