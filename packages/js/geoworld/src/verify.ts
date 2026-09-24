/** SHA-256 as lower-case hex, with the Web Crypto API (Node ≥ 20 and browsers). */
export async function sha256Hex(data: Uint8Array): Promise<string> {
  const digest = await globalThis.crypto.subtle.digest("SHA-256", data as BufferSource);
  return Array.from(new Uint8Array(digest), (b) => b.toString(16).padStart(2, "0")).join("");
}

// Paths as the index writes them: the index itself, a country manifest or a
// .geojson under data/{body}/{ISO3}/. Anchored and without ".." so a hostile
// index cannot escape a persistent cache.
const SAFE_PATH =
  /^data\/(?:index\.json|[a-z]+\/[A-Z]{3}\/(?:manifest\.json|(?:[A-Za-z0-9_-]+\/)*[A-Za-z0-9_.-]+\.geojson))$/;

export function isSafePath(path: string): boolean {
  return SAFE_PATH.test(path) && !path.split("/").includes("..");
}
