import type { Map as MapLibreMap } from "maplibre-gl";

type Listener = (event: unknown) => void;

interface LayerEntry {
  id: string;
  spec: Record<string, unknown>;
  before: string | undefined;
}

/** Enough of `maplibregl.Map` to observe what the adapter does, and strict where MapLibre is lax. */
export class FakeMap {
  sources = new Map<string, unknown>();
  layers: LayerEntry[] = [];
  featureState = new Map<string, Record<string, unknown>>();
  fitted: { bounds: unknown; options: unknown }[] = [];
  calls: string[] = [];
  styleLoaded: boolean | undefined = true;
  private readonly listeners = new Map<string, Set<Listener>>();

  isStyleLoaded(): boolean | undefined {
    return this.styleLoaded;
  }

  once(type: string, listener: Listener): this {
    let set = this.listeners.get(type);
    if (!set) this.listeners.set(type, (set = new Set()));
    set.add(listener);
    return this;
  }

  off(type: string, listener: Listener): this {
    this.listeners.get(type)?.delete(listener);
    return this;
  }

  fire(type: string): void {
    const set = this.listeners.get(type);
    if (!set) return;
    this.listeners.delete(type);
    for (const listener of set) listener({ type });
  }

  pending(type: string): number {
    return this.listeners.get(type)?.size ?? 0;
  }

  addSource(id: string, spec: unknown): this {
    if (this.sources.has(id)) throw new Error(`source ${id} already exists`);
    this.sources.set(id, spec);
    this.calls.push(`addSource:${id}`);
    return this;
  }

  getSource(id: string): unknown {
    return this.sources.get(id);
  }

  removeSource(id: string): this {
    if (this.layers.some((l) => l.spec["source"] === id)) throw new Error(`source ${id} still has layers`);
    if (!this.sources.delete(id)) throw new Error(`no source ${id}`);
    this.calls.push(`removeSource:${id}`);
    return this;
  }

  addLayer(spec: { id: string; [key: string]: unknown }, before?: string): this {
    if (before !== undefined && !this.layers.some((l) => l.id === before)) throw new Error(`no layer ${before}`);
    if (this.layers.some((l) => l.id === spec.id)) throw new Error(`layer ${spec.id} already exists`);
    this.layers.push({ id: spec.id, spec, before });
    this.calls.push(`addLayer:${spec.id}`);
    return this;
  }

  getLayer(id: string): LayerEntry | undefined {
    return this.layers.find((l) => l.id === id);
  }

  removeLayer(id: string): this {
    const index = this.layers.findIndex((l) => l.id === id);
    if (index < 0) throw new Error(`no layer ${id}`);
    this.layers.splice(index, 1);
    this.calls.push(`removeLayer:${id}`);
    return this;
  }

  setFeatureState(target: { source: string; id?: string | number }, state: Record<string, unknown>): this {
    const key = `${target.source}/${String(target.id)}`;
    this.featureState.set(key, { ...(this.featureState.get(key) ?? {}), ...state });
    this.calls.push(`setFeatureState:${key}`);
    return this;
  }

  removeFeatureState(target: { source: string; id?: string | number }, key?: string): this {
    if (target.id === undefined) {
      for (const k of [...this.featureState.keys()]) if (k.startsWith(`${target.source}/`)) this.featureState.delete(k);
    } else {
      const stateKey = `${target.source}/${String(target.id)}`;
      if (key === undefined) this.featureState.delete(stateKey);
      else {
        const state = { ...(this.featureState.get(stateKey) ?? {}) };
        delete state[key];
        this.featureState.set(stateKey, state);
      }
    }
    this.calls.push(`removeFeatureState:${target.source}/${String(target.id)}/${String(key)}`);
    return this;
  }

  fitBounds(bounds: unknown, options?: unknown): this {
    this.fitted.push({ bounds, options });
    this.calls.push("fitBounds");
    return this;
  }
}

export function fakeMap(): { fake: FakeMap; map: MapLibreMap } {
  const fake = new FakeMap();
  return { fake, map: fake as unknown as MapLibreMap };
}
