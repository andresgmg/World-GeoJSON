import type { GeoWorld } from "geoworld";
import { createContext, createElement, type ReactElement, type ReactNode, useContext, useMemo } from "react";

import { createStore, type Store } from "./store.js";

export interface GeoWorldContextValue {
  client: GeoWorld;
  store: Store;
}

const GeoWorldContext = createContext<GeoWorldContextValue | null>(null);

export interface GeoWorldProviderProps {
  /** The `geoworld` client every hook below reads through. */
  client: GeoWorld;
  /** A store to share across providers or to prime on the server; one is created otherwise. */
  store?: Store;
  children?: ReactNode;
}

/** Makes a client (and its resource store) available to the hooks. */
export function GeoWorldProvider({ client, store, children }: GeoWorldProviderProps): ReactElement {
  const value = useMemo<GeoWorldContextValue>(
    () => ({ client, store: store ?? createStore() }),
    [client, store],
  );
  return createElement(GeoWorldContext.Provider, { value }, children);
}

/** The client and store of the nearest provider; throws without one. */
export function useGeoWorld(): GeoWorldContextValue {
  const value = useContext(GeoWorldContext);
  if (!value) throw new Error("useGeoWorld() needs a <GeoWorldProvider client={…}> above it");
  return value;
}
