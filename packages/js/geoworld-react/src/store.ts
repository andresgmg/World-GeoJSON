/**
 * A tiny keyed resource store, independent of React.
 *
 * The client caches *promises*, which React cannot read synchronously; this
 * store holds the settled state per key so a component mounting on cached
 * data renders `success` at once, concurrent loads of one key are made only
 * once, and `reload`/`invalidate` have a shared home. `useSyncExternalStore`
 * reads it; nothing here imports React, so it is tested on its own.
 */

export type ResourceState<T> =
  | { status: "idle"; data: undefined; error: undefined }
  | { status: "loading"; data: T | undefined; error: undefined }
  | { status: "success"; data: T; error: undefined }
  | { status: "error"; data: T | undefined; error: unknown };

/** The one state every unknown key reports; referentially stable. */
export const IDLE: ResourceState<never> = Object.freeze({
  status: "idle",
  data: undefined,
  error: undefined,
}) as ResourceState<never>;

export interface LoadOptions {
  /** Load again even if the key already succeeded or is loading. */
  force?: boolean;
}

export interface Store {
  /** Current state of a key (`IDLE` when unknown). Stable until it changes. */
  get<T>(key: string): ResourceState<T>;
  /** Start (or join) a load; never rejects, the state carries the error. */
  load<T>(key: string, loader: () => Promise<T>, options?: LoadOptions): Promise<ResourceState<T>>;
  /** Be told when one key's state object changes. */
  subscribe(key: string, listener: () => void): () => void;
  /** Forget one key, or every key; in-flight results for them are ignored. */
  invalidate(key?: string): void;
}

interface Entry {
  state: ResourceState<unknown>;
  version: number;
  pending: Promise<ResourceState<unknown>> | null;
}

export function createStore(): Store {
  const entries = new Map<string, Entry>();
  const listeners = new Map<string, Set<() => void>>();

  const notify = (key: string): void => {
    for (const listener of listeners.get(key) ?? []) listener();
  };

  const settle = (key: string, version: number, state: ResourceState<unknown>): ResourceState<unknown> => {
    const entry = entries.get(key);
    if (!entry || entry.version !== version) return state; // invalidated or superseded meanwhile
    entries.set(key, { state, version, pending: null });
    notify(key);
    return state;
  };

  return {
    get<T>(key: string): ResourceState<T> {
      return (entries.get(key)?.state ?? IDLE) as ResourceState<T>;
    },

    load<T>(key: string, loader: () => Promise<T>, options: LoadOptions = {}): Promise<ResourceState<T>> {
      const current = entries.get(key);
      if (!options.force) {
        if (current?.pending) return current.pending as Promise<ResourceState<T>>;
        if (current?.state.status === "success") {
          return Promise.resolve(current.state as ResourceState<T>);
        }
      }
      const version = (current?.version ?? 0) + 1;
      const previous = current?.state.data as T | undefined;
      const entry: Entry = {
        state: { status: "loading", data: previous, error: undefined },
        version,
        pending: null,
      };
      entry.pending = loader().then(
        (data) => settle(key, version, { status: "success", data, error: undefined }),
        (error: unknown) => settle(key, version, { status: "error", data: previous, error }),
      );
      entries.set(key, entry);
      notify(key);
      return entry.pending as Promise<ResourceState<T>>;
    },

    subscribe(key: string, listener: () => void): () => void {
      let set = listeners.get(key);
      if (!set) listeners.set(key, (set = new Set()));
      set.add(listener);
      return () => {
        set.delete(listener);
        if (set.size === 0) listeners.delete(key);
      };
    },

    invalidate(key?: string): void {
      if (key === undefined) {
        entries.clear();
        for (const each of listeners.keys()) notify(each);
      } else {
        entries.delete(key);
        notify(key);
      }
    },
  };
}

/** Load a key only when nothing has been asked of it yet. The body of the hooks' effect. */
export function ensureLoaded<T>(store: Store, key: string, loader: () => Promise<T>): void {
  if (store.get(key).status === "idle") void store.load(key, loader);
}

/** A stable key from plain parts (`JSON.stringify`). */
export function resourceKey(parts: ReadonlyArray<string | number | boolean | null>): string {
  return JSON.stringify(parts);
}

export interface BoundariesKeyOptions {
  part?: string;
  preview?: boolean;
}

/** The keys the built-in hooks use; ISO3 and level are upper-cased so `chl` and `CHL` share one entry. */
export const keys = {
  index: (): string => resourceKey(["index"]),
  countries: (): string => resourceKey(["countries"]),
  country: (iso3: string): string => resourceKey(["country", iso3.toUpperCase()]),
  boundaries: (iso3: string, level: string, options: BoundariesKeyOptions = {}): string =>
    resourceKey(["boundaries", iso3.toUpperCase(), level.toUpperCase(), options.part ?? null, options.preview === true]),
  feature: (id: string): string => resourceKey(["feature", id]),
  children: (id: string): string => resourceKey(["children", id]),
};
