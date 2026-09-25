import assert from "node:assert/strict";
import { test } from "node:test";

import { UnknownLevel } from "geoworld";
import type * as Leaflet from "leaflet";

import { DEFAULT_STYLE, bboxFor, collection, layerById, toLatLngBounds, withLeaflet } from "../src/index.js";
import { FakeGeoJSON, FakeLatLngBounds, fakeL, fakeMap } from "./fakes.js";
import { client } from "./helpers.js";

const ABW_BBOX: [number, number, number, number] = [-70.062408, 12.41767, -69.87682, 12.632148];

test("toLatLngBounds swaps to [[south, west], [north, east]]", () => {
  assert.deepEqual(toLatLngBounds(ABW_BBOX), [
    [12.41767, -70.062408],
    [12.632148, -69.87682],
  ]);
});

test("bounds builds a LatLngBounds through the injected namespace", () => {
  const bounds = withLeaflet(fakeL).bounds(ABW_BBOX) as unknown as FakeLatLngBounds;
  assert.ok(bounds instanceof FakeLatLngBounds);
  assert.deepEqual(bounds.args, toLatLngBounds(ABW_BBOX));
});

test("collection: preview, part, combined and parts-only", async () => {
  const world = client();
  assert.equal((await collection(world, "BRB", "ADM1", { preview: true })).features.length, 11);
  assert.equal((await collection(world, "DOM", "ADM2", { part: "DO-01" })).features.length, 1);
  assert.equal((await collection(world, "DOM", "ADM1")).features.length, 32);
  assert.equal((await collection(world, "DOM", "ADM2")).features.length, 11);
});

test("boundaries passes layer options through and strips part/preview", async () => {
  const gw = withLeaflet(fakeL);
  const onEachFeature = (): void => undefined;
  const layer = (await gw.boundaries(client(), "DOM", "ADM2", {
    part: "DO-01",
    style: { color: "#f00" },
    onEachFeature,
  })) as unknown as FakeGeoJSON;
  assert.ok(layer instanceof FakeGeoJSON);
  assert.equal((layer.data as { features: unknown[] }).features.length, 1);
  assert.deepEqual(layer.options, { style: { color: "#f00" }, onEachFeature });
  const defaults = (await gw.boundaries(client(), "ABW", "ADM0")) as unknown as FakeGeoJSON;
  assert.deepEqual(defaults.options, { style: DEFAULT_STYLE });
});

test("addBoundaries adds to the map and fits when asked", async () => {
  const gw = withLeaflet(fakeL);
  const world = client();
  const { fake, map } = fakeMap();
  const plain = await gw.addBoundaries(map, world, "ABW", "ADM0");
  assert.equal(fake.layers.length, 1);
  assert.equal(fake.layers[0], plain as unknown as FakeGeoJSON);
  assert.equal(fake.fitted.length, 0);

  await gw.addBoundaries(map, world, "ABW", "ADM0", { fit: true });
  assert.deepEqual(fake.fitted[0], { bounds: toLatLngBounds(ABW_BBOX), options: undefined });

  await gw.addBoundaries(map, world, "DOM", "ADM2", { part: "DO-02", fit: { padding: [8, 8] } });
  assert.deepEqual(fake.fitted[1], {
    bounds: toLatLngBounds([-71.152229, 18.247917, -70.457863, 18.99604]),
    options: { padding: [8, 8] },
  });
  await gw.addBoundaries(map, world, "BRB", "ADM1", { preview: true, fit: false });
  assert.equal(fake.fitted.length, 2);
  assert.equal(fake.layers.length, 4);
});

test("bboxFor and errors", async () => {
  const world = client();
  assert.deepEqual(await bboxFor(world, "DOM", "ADM2", { part: "do-01" }), [-70.000412, 18.421806, -69.865501, 18.544317]);
  await assert.rejects(withLeaflet(fakeL).boundaries(world, "ABW", "ADM1"), UnknownLevel);
});

test("layerById finds the sub-layer by stable id", async () => {
  const layer = (await withLeaflet(fakeL).boundaries(client(), "DOM", "ADM1")) as unknown as Leaflet.GeoJSON;
  const hit = layerById(layer, "DOM:ADM1:DO-01") as unknown as { feature: { properties: { shapeName: string } } };
  assert.equal(hit.feature.properties.shapeName, "Distrito Nacional");
  assert.equal(layerById(layer, "DOM:ADM1:DO-99"), undefined);
});
