/**
 * `geoworld/node`: a persistent on-disk cache for Node.js.
 *
 * ```ts
 * import { createClient } from "geoworld";
 * import { diskCache } from "geoworld/node";
 * const world = createClient({ cache: diskCache() });
 * ```
 *
 * Files land in `<dir>/<version>/<path>`, the same layout as the Python
 * client, so both can share a cache directory.
 */

import { mkdir, readFile, rename, rm, unlink, writeFile } from "node:fs/promises";
import { homedir } from "node:os";
import { join, sep } from "node:path";

import type { CacheLike } from "./cache.js";
import { isSafePath } from "./verify.js";

/**
 * The platform's cache location for geoworld: `$GEOWORLD_CACHE`, else
 * `%LOCALAPPDATA%` on Windows, `~/Library/Caches` on macOS and
 * `$XDG_CACHE_HOME` (default `~/.cache`) elsewhere.
 */
export function defaultCacheDir(env: NodeJS.ProcessEnv = process.env, platform = process.platform): string {
  if (env.GEOWORLD_CACHE) return env.GEOWORLD_CACHE;
  let base: string;
  if (platform === "win32") base = env.LOCALAPPDATA || join(homedir(), "AppData", "Local");
  else if (platform === "darwin") base = join(homedir(), "Library", "Caches");
  else base = env.XDG_CACHE_HOME || join(homedir(), ".cache");
  return join(base, "geoworld");
}

export class DiskCache implements CacheLike {
  constructor(public readonly dir: string = defaultCacheDir()) {}

  /** Where a key (`"<version>/<path>"`) is stored. */
  pathFor(key: string): string {
    const slash = key.indexOf("/");
    const version = slash < 0 ? "" : key.slice(0, slash);
    const path = key.slice(slash + 1);
    if (!/^[A-Za-z0-9_.-]+$/.test(version) || !isSafePath(path)) {
      throw new Error(`refusing to cache an unexpected key: ${JSON.stringify(key)}`);
    }
    return join(this.dir, version, ...path.split("/"));
  }

  async get(key: string): Promise<Uint8Array | undefined> {
    try {
      return new Uint8Array(await readFile(this.pathFor(key)));
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === "ENOENT") return undefined;
      throw error;
    }
  }

  async set(key: string, value: Uint8Array): Promise<void> {
    const target = this.pathFor(key);
    const parent = target.slice(0, target.lastIndexOf(sep));
    await mkdir(parent, { recursive: true });
    const tmp = `${target}.tmp-${process.pid}-${Date.now()}`;
    try {
      await writeFile(tmp, value);
      await rename(tmp, target);
    } catch (error) {
      await unlink(tmp).catch(() => undefined);
      throw error;
    }
  }

  async delete(key: string): Promise<void> {
    await unlink(this.pathFor(key)).catch((error: NodeJS.ErrnoException) => {
      if (error.code !== "ENOENT") throw error;
    });
  }

  /** Remove everything cached, for every data version. */
  async clear(): Promise<void> {
    await rm(this.dir, { recursive: true, force: true });
  }
}

/** A `DiskCache` for `createClient({ cache })`. */
export function diskCache(dir?: string): DiskCache {
  return new DiskCache(dir);
}
