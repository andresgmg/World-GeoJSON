import type { Country, CountrySummary, Feature, FeatureCollection, GeoWorld, Index } from "geoworld";
import { useCallback, useEffect, useRef, useSyncExternalStore } from "react";

import { useGeoWorld } from "./context.js";
import { ensureLoaded, IDLE, keys, type ResourceState } from "./store.js";

export type Resource<T> = ResourceState<T> & {
  /** Load again, even when already loaded; with the client's memory cache this only refetches after an error. */
  reload(): Promise<void>;
};

const noop = (): void => undefined;

/**
 * Subscribe to one key of the provider's store and load it on mount.
 *
 * `key === null` means "nothing to load": the resource stays `idle` and no
 * effect runs. The loader is kept in a ref, so an inline arrow is fine.
 */
export function useResource<T>(key: string | null, loader: () => Promise<T>): Resource<T> {
  const { store } = useGeoWorld();
  const loaderRef = useRef(loader);
  useEffect(() => {
    loaderRef.current = loader;
  });
  const subscribe = useCallback(
    (listener: () => void) => (key === null ? noop : store.subscribe(key, listener)),
    [store, key],
  );
  const getSnapshot = useCallback(
    (): ResourceState<T> => (key === null ? IDLE : store.get<T>(key)),
    [store, key],
  );
  const state = useSyncExternalStore(subscribe, getSnapshot, getSnapshot);
  useEffect(() => {
    if (key !== null) ensureLoaded(store, key, () => loaderRef.current());
  }, [store, key]);
  const reload = useCallback(async (): Promise<void> => {
    if (key !== null) await store.load(key, () => loaderRef.current(), { force: true });
  }, [store, key]);
  return { ...state, reload };
}

/** The whole `data/index.json`. */
export function useIndex(): Resource<Index> {
  const { client } = useGeoWorld();
  return useResource(keys.index(), () => client.index());
}

/** One summary per territory. */
export function useCountries(): Resource<CountrySummary[]> {
  const { client } = useGeoWorld();
  return useResource(keys.countries(), () => client.countries());
}

/** The full index entry of a territory; `null`/`undefined` keeps it idle. */
export function useCountry(iso3: string | null | undefined): Resource<Country> {
  const { client } = useGeoWorld();
  return useResource(iso3 ? keys.country(iso3) : null, () => client.country(iso3 as string));
}

export interface UseBoundariesOptions {
  /** One part of a split level (its ADM1 key, or `"unassigned"`). */
  part?: string;
  /** The simplified preview instead of the full-resolution file. */
  preview?: boolean;
  /** `false` keeps the resource idle without unmounting. */
  enabled?: boolean;
}

/** The FeatureCollection of a level, a part, or a preview. */
export function useBoundaries(
  iso3: string | null | undefined,
  level: string | null | undefined,
  options: UseBoundariesOptions = {},
): Resource<FeatureCollection> {
  const { client } = useGeoWorld();
  const enabled = options.enabled !== false && Boolean(iso3) && Boolean(level);
  const key = enabled ? keys.boundaries(iso3 as string, level as string, options) : null;
  return useResource(key, () => collection(client, iso3 as string, level as string, options));
}

/** One feature by stable id. */
export function useFeature(id: string | null | undefined): Resource<Feature> {
  const { client } = useGeoWorld();
  return useResource(id ? keys.feature(id) : null, () => client.find(id as string));
}

/** The features of the next published level under this id. */
export function useChildren(id: string | null | undefined): Resource<Feature[]> {
  const { client } = useGeoWorld();
  return useResource(id ? keys.children(id) : null, () => client.children(id as string));
}

/** Preview, part, combined file, or every part concatenated when there is no combined file. */
export async function collection(
  client: GeoWorld,
  iso3: string,
  level: string,
  options: { part?: string; preview?: boolean } = {},
): Promise<FeatureCollection> {
  if (options.preview) return client.preview(iso3, level);
  if (options.part !== undefined) return client.getPart(iso3, level, options.part);
  const dataset = await client.dataset(iso3, level);
  if (dataset.path !== undefined) return client.get(iso3, level);
  const features: Feature[] = [];
  for await (const [, part] of client.iterParts(iso3, level)) features.push(...part.features);
  return { type: "FeatureCollection", features };
}
