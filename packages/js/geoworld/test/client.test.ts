import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { test } from "node:test";

import {
  ChecksumMismatch,
  DEFAULT_BASE_URL,
  DEFAULT_DATA_VERSION,
  DownloadError,
  GeoWorld,
  InvalidFeatureId,
  MemoryCache,
  NoCombinedFile,
  NoPreview,
  NotSplit,
  UnknownCountry,
  UnknownFeature,
  UnknownLevel,
  UnknownPart,
  UnsupportedSchema,
  createClient,
  normalise,
  parseId,
  sha256Hex,
} from "../src/index.js";
import { BASE_URL, FIXTURES, client, fixturesFetch } from "./helpers.js";

test("default urls", () => {
  const world = createClient();
  assert.equal(world.version, DEFAULT_DATA_VERSION);
  assert.equal(world.baseUrl, `${DEFAULT_BASE_URL}/v${DEFAULT_DATA_VERSION}`);
  assert.ok(world.urlFor("data/index.json").endsWith("/v1.0.0/data/index.json"));
  assert.ok(createClient({ version: "2.3.4" }).baseUrl.endsWith("/v2.3.4"));
  assert.equal(createClient({ baseUrl: "https://cdn.example/wg/" }).baseUrl, "https://cdn.example/wg");
});

test("version main warns and drops the persistent store", () => {
  const warnings: string[] = [];
  const original = console.warn;
  console.warn = (message: string) => warnings.push(message);
  try {
    const world = createClient({ version: "main", cache: new MemoryCache() });
    assert.ok(world.baseUrl.endsWith("/main"));
    assert.match(warnings.join("\n"), /moving branch/);
  } finally {
    console.warn = original;
  }
});

test("index and summaries", async () => {
  const world = client();
  const index = await world.index();
  assert.equal(index.schema_version, 1);
  assert.equal(index.totals.countries, 3);
  assert.equal(await world.index(), index);
  const summaries = await world.countries();
  assert.deepEqual(
    summaries.map((c) => c.iso_a3),
    ["ABW", "BRB", "DOM"],
  );
  const dom = summaries.find((c) => c.iso_a3 === "DOM")!;
  assert.equal(dom.features, 1 + 32 + 11);
  assert.equal(dom.datasets, 3);
  assert.ok("datasets" in (await world.country("DOM")));
  assert.equal((await world.country("dom")).iso_a3, "DOM");
  assert.deepEqual(await world.levels("DOM"), ["ADM0", "ADM1", "ADM2"]);
  assert.equal((await world.dataset("DOM", "adm1")).level, "ADM1");
  assert.deepEqual(await world.bbox("ABW", "ADM0"), [-70.062408, 12.41767, -69.87682, 12.632148]);
  assert.deepEqual(await world.parts("DOM", "ADM2"), ["DO-01", "DO-02"]);
});

test("lookups fail loudly", async () => {
  const world = client();
  await assert.rejects(world.country("XXX"), UnknownCountry);
  await assert.rejects(world.get("ABW", "ADM1"), (e: Error) => {
    assert.ok(e instanceof UnknownLevel);
    assert.equal(e.message, "ABW has no ADM1; available: ADM0");
    return true;
  });
  await assert.rejects(world.parts("DOM", "ADM1"), NotSplit);
  await assert.rejects(world.getPart("DOM", "ADM2", "DO-99"), UnknownPart);
  await assert.rejects(world.preview("DOM", "ADM2"), NoPreview);
  await assert.rejects(world.find("DOM:ADM1:DO-99"), UnknownFeature);
  await assert.rejects(world.find("not an id"), InvalidFeatureId);
  await assert.rejects(world.url("DOM", "ADM1", { part: "x", preview: true }), TypeError);
});

test("urls", async () => {
  const world = client();
  assert.equal(await world.url("DOM", "ADM1"), `${BASE_URL}/data/earth/DOM/DOM_ADM1.geojson`);
  assert.equal(await world.url("DOM", "ADM2", { part: "DO-01" }), `${BASE_URL}/data/earth/DOM/ADM2/DO-01.geojson`);
  assert.ok((await world.url("DOM", "ADM2", { part: "do-01" })).endsWith("/DO-01.geojson"));
  assert.ok((await world.url("DOM", "ADM1", { preview: true })).endsWith("/preview/DOM_ADM1.preview.geojson"));
});

test("get, parts and previews", async () => {
  const world = client();
  const adm0 = await world.get("ABW", "ADM0");
  assert.equal(adm0.type, "FeatureCollection");
  assert.equal(adm0.features[0]!.id, "ABW:ADM0:ABW");
  assert.equal(await world.get("ABW", "ADM0"), adm0); // memoised
  const part = await world.getPart("DOM", "ADM2", "DO-01");
  assert.deepEqual(
    part.features.map((f) => f.id),
    ["DOM:ADM2:DO-01.distrito-nacional"],
  );
  const codes: string[] = [];
  for await (const [code] of world.iterParts("DOM", "ADM2")) codes.push(code);
  assert.deepEqual(codes, ["DO-01", "DO-02"]);
  let count = 0;
  for await (const _ of world.features("DOM", "ADM2")) count += 1;
  assert.equal(count, 11);
  const preview = await world.preview("BRB", "ADM1");
  assert.equal(preview.features.length, 11);
  assert.deepEqual(Object.keys(preview.features[0]!.properties).sort(), ["shapeISO", "shapeName", "shapeType"]);
});

test("split level without a combined file", async () => {
  const world = client();
  await assert.rejects(world.get("DOM", "ADM2"), (e: Error) => {
    assert.ok(e instanceof NoCombinedFile);
    assert.match(e.message, /iterParts/);
    return true;
  });
  await assert.rejects(world.url("DOM", "ADM2"), NoCombinedFile);
  const ids: string[] = [];
  for await (const f of world.features("DOM", "ADM2")) ids.push(f.id);
  assert.deepEqual(ids.slice(0, 2), ["DOM:ADM2:DO-01.distrito-nacional", "DOM:ADM2:DO-02.azua-de-compostela"]);
});

test("navigation", async () => {
  const world = client();
  assert.equal((await world.find("DOM:ADM1:DO-01")).properties.shapeName, "Distrito Nacional");
  assert.equal(await world.parent("DOM:ADM0:DOM"), null);
  assert.equal((await world.parent("DOM:ADM1:DO-01"))!.id, "DOM:ADM0:DOM");
  assert.equal((await world.find("DOM:ADM2:DO-02.estebania")).properties.parentID, "DOM:ADM1:DO-02");
  assert.equal((await world.parent("DOM:ADM2:DO-02.estebania"))!.id, "DOM:ADM1:DO-02");
  assert.deepEqual(
    (await world.children("DOM:ADM1:DO-01")).map((f) => f.id),
    ["DOM:ADM2:DO-01.distrito-nacional"],
  );
  assert.equal((await world.children("DOM:ADM1:DO-02")).length, 10);
  assert.deepEqual(await world.children("DOM:ADM1:DO-05"), []);
  assert.equal((await world.children("DOM:ADM0:DOM")).length, 32);
  assert.deepEqual(await world.children("DOM:ADM2:DO-02.estebania"), []);
  await assert.rejects(world.children("DOM:ADM3:x"), UnknownLevel);
});

test("find reads only the part it needs", async () => {
  const requests: string[] = [];
  const world = client({}, requests);
  await world.find("DOM:ADM2:DO-01.distrito-nacional");
  assert.ok(requests.includes("/data/earth/DOM/ADM2/DO-01.geojson"));
  assert.ok(!requests.includes("/data/earth/DOM/ADM2/DO-02.geojson"));
});

test("search", async () => {
  const world = client();
  assert.deepEqual((await world.search("santo", "DOM")).map((f) => f.id), ["DOM:ADM1:DO-32"]);
  assert.deepEqual(
    (await world.search("Compostéla", "dom", "adm2")).map((f) => f.id),
    ["DOM:ADM2:DO-02.azua-de-compostela"],
  );
  assert.deepEqual((await world.search("do-01", "DOM", "ADM1")).map((f) => f.id), ["DOM:ADM1:DO-01"]);
  assert.deepEqual(await world.search("   ", "DOM"), []);
  assert.equal(normalise("  Ñuñoa  DEL  Mar "), "nunoa del mar");
});

test("parseId", () => {
  assert.deepEqual(parseId("USA:ADM2:US-DE.new-castle"), { iso3: "USA", level: "ADM2", key: "US-DE.new-castle" });
  assert.throws(() => parseId("usa:ADM2:x"), InvalidFeatureId);
});

test("persistent store round-trip and verification", async () => {
  const store = new MemoryCache();
  const world = client({ cache: store });
  await world.get("ABW", "ADM0");
  const key = "1.0.0/data/earth/ABW/ABW_ADM0.geojson";
  const onDisk = await readFile(join(FIXTURES, "data/earth/ABW/ABW_ADM0.geojson"));
  assert.deepEqual(store.get(key), new Uint8Array(onDisk));
  // A second client reads from the store, and re-hashes what it reads.
  const again = new GeoWorld({ baseUrl: "https://unreachable.test", fetch: fixturesFetch(), cache: store });
  assert.equal((await again.get("ABW", "ADM0")).features[0]!.id, "ABW:ADM0:ABW");
  // Corrupt the stored bytes: they are discarded and refetched (here, unreachable).
  store.set(key, new TextEncoder().encode('{"type":"FeatureCollection","features":[]}'));
  await again.clearCache({ store: false });
  await assert.rejects(again.get("ABW", "ADM0"), DownloadError);
  assert.equal(store.get(key), undefined);
  await world.clearCache();
  assert.equal(store.size, 0);
});

test("cache none refetches, memory does not", async () => {
  const requests: string[] = [];
  const none = client({ cache: "none" }, requests);
  await none.get("ABW", "ADM0");
  await none.get("ABW", "ADM0");
  assert.equal(requests.filter((p) => p.endsWith("ABW_ADM0.geojson")).length, 2);
  assert.equal(requests.filter((p) => p.endsWith("index.json")).length, 1);
  requests.length = 0;
  const memory = client({}, requests);
  await Promise.all([memory.get("ABW", "ADM0"), memory.get("ABW", "ADM0")]);
  assert.equal(requests.filter((p) => p.endsWith("ABW_ADM0.geojson")).length, 1);
});

test("checksum mismatch", async () => {
  const world = client();
  (await world.dataset("ABW", "ADM0")).sha256 = "0".repeat(64);
  await assert.rejects(world.get("ABW", "ADM0"), (e: Error) => {
    assert.ok(e instanceof ChecksumMismatch);
    assert.match(e.message, /ABW_ADM0/);
    return true;
  });
  const relaxed = client({ verify: false });
  (await relaxed.dataset("ABW", "ADM0")).sha256 = "0".repeat(64);
  assert.ok((await relaxed.get("ABW", "ADM0")).features.length);
});

test("unsupported schema", async () => {
  const world = new GeoWorld({
    baseUrl: BASE_URL,
    fetch: async () => new Response(JSON.stringify({ schema_version: 2, bodies: [], totals: {}, countries: [] })),
  });
  await assert.rejects(world.index(), (e: Error) => {
    assert.ok(e instanceof UnsupportedSchema);
    assert.match(e.message, /upgrade geoworld/);
    return true;
  });
});

test("fetch is invoked without the client as receiver (browsers reject that)", async () => {
  let receiver: unknown = "unset";
  const strict = function (this: unknown, input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
    receiver = this;
    return fixturesFetch()(input, init);
  };
  const world = new GeoWorld({ baseUrl: BASE_URL, fetch: strict as typeof fetch });
  await world.index();
  assert.equal(receiver, undefined);
});

test("download errors", async () => {
  const missing = new GeoWorld({ baseUrl: "https://fixtures.test/nowhere", fetch: fixturesFetch() });
  await assert.rejects(missing.index(), (e: Error) => {
    assert.ok(e instanceof DownloadError);
    assert.equal(e.status, 404);
    assert.match(e.message, /HTTP 404/);
    return true;
  });
  const broken = new GeoWorld({
    baseUrl: BASE_URL,
    fetch: async () => {
      throw new Error("boom");
    },
  });
  await assert.rejects(broken.index(), /could not fetch .*boom/);
  await assert.rejects(broken.index(), DownloadError); // not stuck on a rejected promise
});

test("sha256 of the fixture files matches the index", async () => {
  const world = client();
  for (const country of (await world.index()).countries) {
    for (const dataset of country.datasets) {
      const entries: [string, string][] = dataset.path ? [[dataset.path, dataset.sha256!]] : [];
      for (const part of dataset.parts ?? []) entries.push([part.path, part.sha256]);
      for (const [path, expected] of entries) {
        const digest = await sha256Hex(new Uint8Array(await readFile(join(FIXTURES, path))));
        assert.equal(digest, expected, path);
      }
    }
  }
});
