/**
 * Where downloaded bytes go between calls.
 *
 * Keys are `"<data version>/<repository path>"`, so one store can hold several
 * data versions and the layout matches the Python client's disk cache.
 */
export interface CacheLike {
  get(key: string): Promise<Uint8Array | undefined> | Uint8Array | undefined;
  set(key: string, value: Uint8Array): Promise<void> | void;
  delete(key: string): Promise<void> | void;
  clear(): Promise<void> | void;
}

/** A `Map`-backed store: bytes live as long as the client does. */
export class MemoryCache implements CacheLike {
  private readonly entries = new Map<string, Uint8Array>();

  get(key: string): Uint8Array | undefined {
    return this.entries.get(key);
  }

  set(key: string, value: Uint8Array): void {
    this.entries.set(key, value);
  }

  delete(key: string): void {
    this.entries.delete(key);
  }

  clear(): void {
    this.entries.clear();
  }

  get size(): number {
    return this.entries.size;
  }
}
