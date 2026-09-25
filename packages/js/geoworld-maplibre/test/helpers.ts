import { existsSync } from "node:fs";
import { readFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { type ClientOptions, GeoWorld } from "geoworld";

/** The repository root: the first ancestor with fixtures/data/index.json (tests run compiled). */
function findRepo(): string {
  let dir = dirname(fileURLToPath(import.meta.url));
  for (let i = 0; i < 8; i += 1) {
    if (existsSync(join(dir, "fixtures", "data", "index.json"))) return dir;
    dir = dirname(dir);
  }
  throw new Error("repository root with fixtures/ not found");
}

export const REPO = findRepo();
export const FIXTURES = join(REPO, "fixtures");
export const BASE_URL = "https://fixtures.test";

/** A `fetch` that serves `fixtures/` from disk at https://fixtures.test/…; other hosts get 502. */
export function fixturesFetch(root = FIXTURES, log?: string[]): typeof fetch {
  return async (input) => {
    const url = new URL(input instanceof Request ? input.url : String(input));
    log?.push(url.pathname);
    if (url.origin !== BASE_URL) return new Response("unreachable", { status: 502 });
    const file = join(root, ...url.pathname.split("/").filter(Boolean));
    try {
      const data = await readFile(file);
      return new Response(new Uint8Array(data), {
        status: 200,
        headers: { "content-type": "application/geo+json" },
      });
    } catch {
      return new Response("not found", { status: 404, statusText: "Not Found" });
    }
  };
}

export function client(options: ClientOptions = {}, log?: string[]): GeoWorld {
  return new GeoWorld({ baseUrl: BASE_URL, fetch: fixturesFetch(FIXTURES, log), ...options });
}
