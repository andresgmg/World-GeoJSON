import assert from "node:assert/strict";
import { mkdtemp, readdir, rm, stat } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";

import { DiskCache, defaultCacheDir, diskCache } from "../src/node.js";
import { client } from "./helpers.js";

test("defaultCacheDir per platform", () => {
  assert.equal(defaultCacheDir({ GEOWORLD_CACHE: "/x" }, "linux"), "/x");
  assert.equal(defaultCacheDir({ XDG_CACHE_HOME: "/xdg" }, "linux"), join("/xdg", "geoworld"));
  assert.ok(defaultCacheDir({}, "linux").endsWith(join(".cache", "geoworld")));
  assert.ok(defaultCacheDir({}, "darwin").endsWith(join("Library", "Caches", "geoworld")));
  assert.equal(defaultCacheDir({ LOCALAPPDATA: "C:\\Users\\a\\AppData\\Local" }, "win32"), join("C:\\Users\\a\\AppData\\Local", "geoworld"));
});

test("disk cache stores <version>/<path> atomically and refuses odd keys", async () => {
  const dir = await mkdtemp(join(tmpdir(), "geoworld-"));
  try {
    const cache = diskCache(dir);
    assert.ok(cache instanceof DiskCache);
    assert.equal(await cache.get("1.0.0/data/index.json"), undefined);
    await cache.set("1.0.0/data/index.json", new TextEncoder().encode("{}"));
    assert.equal(cache.pathFor("1.0.0/data/index.json"), join(dir, "1.0.0", "data", "index.json"));
    assert.deepEqual(await readdir(join(dir, "1.0.0", "data")), ["index.json"]);
    assert.equal(new TextDecoder().decode(await cache.get("1.0.0/data/index.json")), "{}");
    await cache.delete("1.0.0/data/index.json");
    await cache.delete("1.0.0/data/index.json"); // idempotent
    assert.equal(await cache.get("1.0.0/data/index.json"), undefined);
    assert.throws(() => cache.pathFor("1.0.0/../escape.json"), /unexpected key/);
    assert.throws(() => cache.pathFor("../1.0.0/data/index.json"), /unexpected key/);
    assert.throws(() => cache.pathFor("1.0.0/data/earth/DOM/x.txt"), /unexpected key/);

    const world = client({ cache });
    await world.get("ABW", "ADM0");
    assert.ok((await stat(join(dir, "1.0.0", "data", "earth", "ABW", "ABW_ADM0.geojson"))).isFile());
    await cache.clear();
    await assert.rejects(stat(dir));
  } finally {
    await rm(dir, { recursive: true, force: true });
  }
});
