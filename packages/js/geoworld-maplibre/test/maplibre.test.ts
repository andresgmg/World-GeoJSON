import assert from "node:assert/strict";
import { test } from "node:test";

import { UnknownCountry, UnknownLevel } from "geoworld";

import {
  addBoundaries,
  bboxFor,
  clearFeatureState,
  collection,
  DEFAULT_FILL,
  DEFAULT_LINE,
  fitToBounds,
  ID_PROPERTY,
  setFeatureState,
  sourceId,
  sourceSpec,
  toLngLatBounds,
  whenStyleReady,
  withIdProperty,
} from "../src/index.js";
import { fakeMap } from "./fakes.js";
import { client } from "./helpers.js";

const ABW_BBOX: [number, number, number, number] = [-70.062408, 12.41767, -69.87682, 12.632148];

test("toLngLatBounds keeps [west, south], [east, north]", () => {
  assert.deepEqual(toLngLatBounds(ABW_BBOX), [
    [-70.062408, 12.41767],
    [-69.87682, 12.632148],
  ]);
});

test("fitToBounds passes bounds and options through", () => {
  const { fake, map } = fakeMap();
  fitToBounds(map, ABW_BBOX);
  fitToBounds(map, ABW_BBOX, { padding: 20 });
  assert.equal(fake.fitted.length, 2);
  assert.deepEqual(fake.fitted[0], { bounds: toLngLatBounds(ABW_BBOX), options: undefined });
  assert.deepEqual(fake.fitted[1]!.options, { padding: 20 });
});

test("whenStyleReady resolves now, on style.load, or on idle", async () => {
  const loaded = fakeMap();
  await whenStyleReady(loaded.map);
  const bare = fakeMap();
  bare.fake.styleLoaded = undefined;
  await whenStyleReady(bare.map);

  const busy = fakeMap();
  busy.fake.styleLoaded = false;
  let settled = false;
  const waiting = whenStyleReady(busy.map).then(() => (settled = true));
  await Promise.resolve();
  assert.equal(settled, false);
  assert.equal(busy.fake.pending("style.load"), 1);
  assert.equal(busy.fake.pending("idle"), 1);
  busy.fake.fire("style.load");
  await waiting;
  assert.equal(settled, true);
  assert.equal(busy.fake.pending("idle"), 0); // the other listener was removed

  const idle = fakeMap();
  idle.fake.styleLoaded = false;
  const waitingIdle = whenStyleReady(idle.map);
  idle.fake.fire("idle");
  await waitingIdle;
  assert.equal(idle.fake.pending("style.load"), 0);
});

test("sourceId defaults", () => {
  assert.equal(sourceId("chl", "adm1"), "geoworld-CHL-ADM1");
  assert.equal(sourceId("USA", "ADM2", { part: "US-CA" }), "geoworld-USA-ADM2-US-CA");
  assert.equal(sourceId("CHL", "ADM3", { preview: true }), "geoworld-CHL-ADM3-preview");
});

test("withIdProperty promotes the id without touching the original", () => {
  const fc = { type: "FeatureCollection" as const, features: [{ type: "Feature" as const, id: "X:ADM0:X", properties: { shapeName: "x", shapeISO: "", shapeGroup: "XXX", shapeType: "ADM0" }, geometry: { type: "Polygon" as const, coordinates: [] } }] };
  const promoted = withIdProperty(fc);
  assert.equal(promoted.features[0]!.properties.id, "X:ADM0:X");
  assert.equal(promoted.features[0]!.properties.shapeName, "x");
  assert.equal("id" in fc.features[0]!.properties, false);
  assert.equal(promoted.features[0]!.geometry, fc.features[0]!.geometry); // shallow
});

test("collection: preview, part, combined file, and parts-only concatenation", async () => {
  const world = client();
  assert.equal((await collection(world, "BRB", "ADM1", { preview: true })).features.length, 11);
  assert.equal((await collection(world, "DOM", "ADM2", { part: "DO-01" })).features.length, 1);
  assert.equal((await collection(world, "DOM", "ADM1")).features.length, 32);
  const parts = await collection(world, "DOM", "ADM2"); // no combined file in the fixture
  assert.equal(parts.features.length, 11);
  assert.equal(parts.features[0]!.id, "DOM:ADM2:DO-01.distrito-nacional");
});

test("sourceSpec inlines the promoted collection", async () => {
  const world = client();
  const spec = await sourceSpec(world, "ABW", "ADM0");
  assert.equal(spec.type, "geojson");
  assert.equal(spec.promoteId, ID_PROPERTY);
  const data = spec.data as { features: { id: string; properties: { id: string } }[] };
  assert.equal(data.features[0]!.properties.id, "ABW:ADM0:ABW");
  const cached = await world.get("ABW", "ADM0");
  assert.equal("id" in cached.features[0]!.properties, false);
});

test("bboxFor: level bbox, part bbox, case-insensitive part", async () => {
  const world = client();
  assert.deepEqual(await bboxFor(world, "ABW", "ADM0"), ABW_BBOX);
  assert.deepEqual(await bboxFor(world, "DOM", "ADM2", { part: "do-01" }), [-70.000412, 18.421806, -69.865501, 18.544317]);
  assert.deepEqual(await bboxFor(world, "DOM", "ADM2", { part: "nope" }), await world.bbox("DOM", "ADM2"));
});

test("addBoundaries adds source, fill and line with defaults, and remove() undoes it in order", async () => {
  const { fake, map } = fakeMap();
  const handle = await addBoundaries(map, client(), "abw", "adm0");
  assert.equal(handle.source, "geoworld-ABW-ADM0");
  assert.deepEqual(handle.layers, ["geoworld-ABW-ADM0-fill", "geoworld-ABW-ADM0-line"]);
  assert.deepEqual(handle.bbox, ABW_BBOX);
  assert.equal(handle.iso3, "ABW");
  assert.equal(handle.level, "ADM0");
  assert.deepEqual(fake.calls, ["addSource:geoworld-ABW-ADM0", "addLayer:geoworld-ABW-ADM0-fill", "addLayer:geoworld-ABW-ADM0-line"]);
  assert.deepEqual(fake.layers[0]!.spec["paint"], DEFAULT_FILL);
  assert.deepEqual(fake.layers[1]!.spec["paint"], DEFAULT_LINE);
  assert.equal((fake.sources.get("geoworld-ABW-ADM0") as { promoteId: string }).promoteId, "id");
  assert.equal(fake.fitted.length, 0);

  fake.calls.length = 0;
  handle.remove();
  assert.deepEqual(fake.calls, ["removeLayer:geoworld-ABW-ADM0-line", "removeLayer:geoworld-ABW-ADM0-fill", "removeSource:geoworld-ABW-ADM0"]);
  handle.remove(); // idempotent
  assert.equal(fake.calls.length, 3);
});

test("addBoundaries options: source, fill/line off or custom, before, fit, part, preview", async () => {
  const { fake, map } = fakeMap();
  fake.addLayer({ id: "labels", type: "symbol" });
  const world = client();
  const handle = await addBoundaries(map, world, "DOM", "ADM2", {
    source: "dom",
    part: "DO-02",
    fill: { "fill-color": "#f00" },
    line: false,
    before: "labels",
    fit: { padding: 10 },
  });
  assert.equal(handle.source, "dom");
  assert.deepEqual(handle.layers, ["dom-fill"]);
  assert.equal(fake.layers.find((l) => l.id === "dom-fill")!.before, "labels");
  assert.deepEqual(fake.layers.find((l) => l.id === "dom-fill")!.spec["paint"], { "fill-color": "#f00" });
  assert.deepEqual(fake.fitted[0], { bounds: toLngLatBounds([-71.152229, 18.247917, -70.457863, 18.99604]), options: { padding: 10 } });
  assert.equal(fake.calls.indexOf("fitBounds") < fake.calls.indexOf("addSource:dom"), true);

  const preview = await addBoundaries(map, world, "BRB", "ADM1", { preview: true, fill: false, fit: true });
  assert.equal(preview.source, "geoworld-BRB-ADM1-preview");
  assert.deepEqual(preview.layers, ["geoworld-BRB-ADM1-preview-line"]);
  assert.deepEqual(fake.fitted[1]!.options, undefined);
});

test("addBoundaries waits for the style and refuses a taken source id", async () => {
  const { fake, map } = fakeMap();
  fake.styleLoaded = false;
  const pending = addBoundaries(map, client(), "ABW", "ADM0");
  while (fake.pending("idle") === 0) await new Promise((r) => setTimeout(r, 5)); // data fetched, style awaited
  assert.equal(fake.sources.size, 0);
  fake.fire("idle");
  await pending;
  assert.equal(fake.sources.size, 1);
  fake.styleLoaded = true; // a real map reports loaded from here on
  await assert.rejects(addBoundaries(map, client(), "ABW", "ADM0"), /already exists/);
});

test("addBoundaries fails early on an unknown territory or level", async () => {
  const { fake, map } = fakeMap();
  await assert.rejects(addBoundaries(map, client(), "XXX", "ADM0"), UnknownCountry);
  await assert.rejects(addBoundaries(map, client(), "ABW", "ADM1"), UnknownLevel);
  assert.equal(fake.calls.length, 0);
});

test("feature state helpers", () => {
  const { fake, map } = fakeMap();
  setFeatureState(map, "src", "CHL:ADM1:CL-RM", { hover: true });
  setFeatureState(map, "src", "CHL:ADM1:CL-RM", { selected: true });
  assert.deepEqual(fake.featureState.get("src/CHL:ADM1:CL-RM"), { hover: true, selected: true });
  clearFeatureState(map, "src", "CHL:ADM1:CL-RM", "hover");
  assert.deepEqual(fake.featureState.get("src/CHL:ADM1:CL-RM"), { selected: true });
  clearFeatureState(map, "src", "CHL:ADM1:CL-RM");
  assert.equal(fake.featureState.has("src/CHL:ADM1:CL-RM"), false);
  setFeatureState(map, "src", "a", { x: 1 });
  clearFeatureState(map, "src");
  assert.equal(fake.featureState.size, 0);
  assert.ok(fake.calls.at(-1)!.startsWith("removeFeatureState:src/undefined"));
});
