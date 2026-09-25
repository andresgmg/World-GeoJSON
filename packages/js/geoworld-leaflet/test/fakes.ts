import type { FeatureCollection } from "geoworld";
import type * as Leaflet from "leaflet";

import type { LeafletNamespace } from "../src/index.js";

export class FakeGeoJSON {
  layers: FakeMap[] = [];
  constructor(
    public data: unknown,
    public options: Record<string, unknown> | null | undefined,
  ) {}
  addTo(map: FakeMap): this {
    map.layers.push(this);
    return this;
  }
  getLayers(): { feature: unknown }[] {
    return (this.data as FeatureCollection).features.map((feature) => ({ feature }));
  }
}

export class FakeLatLngBounds {
  constructor(public args: unknown) {}
}

export class FakeMap {
  layers: FakeGeoJSON[] = [];
  fitted: { bounds: unknown; options: unknown }[] = [];
  fitBounds(bounds: unknown, options?: unknown): this {
    this.fitted.push({ bounds, options });
    return this;
  }
}

export const fakeL = { GeoJSON: FakeGeoJSON, LatLngBounds: FakeLatLngBounds } as unknown as LeafletNamespace;

export function fakeMap(): { fake: FakeMap; map: Leaflet.Map } {
  const fake = new FakeMap();
  return { fake, map: fake as unknown as Leaflet.Map };
}
