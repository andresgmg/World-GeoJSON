/**
 * The React layer, rendered with react-dom/server. Server rendering runs
 * `useContext` and `useSyncExternalStore` (through its server snapshot) but
 * no effects and no subscriptions: the three-line effect that calls
 * `ensureLoaded` is exercised by examples/react.html in a browser, and
 * `ensureLoaded` itself by store.test.ts.
 */
import assert from "node:assert/strict";
import { test } from "node:test";

import { createElement, type ReactElement } from "react";
import { renderToString } from "react-dom/server";

import {
  createStore,
  GeoWorldProvider,
  keys,
  useBoundaries,
  useCountry,
  useGeoWorld,
  type Store,
} from "../src/index.js";
import { client } from "./helpers.js";

function Boundaries({ iso3, level, enabled }: { iso3: string | null; level: string; enabled?: boolean }): ReactElement {
  const options = enabled === undefined ? {} : { enabled };
  const { status, data } = useBoundaries(iso3, level, options);
  return createElement("span", null, `${status}:${data?.features.length ?? 0}`);
}

function Country({ iso3 }: { iso3: string }): ReactElement {
  const { status, data } = useCountry(iso3);
  return createElement("span", null, `${status}:${data?.name.en ?? ""}`);
}

function ClientVersion(): ReactElement {
  return createElement("span", null, useGeoWorld().client.version);
}

function render(element: ReactElement, store?: Store): string {
  const props = store ? { client: client(), store } : { client: client() };
  return renderToString(createElement(GeoWorldProvider, props, element));
}

test("useGeoWorld exposes the provided client", () => {
  assert.equal(render(createElement(ClientVersion)), "<span>1.0.0</span>");
});

test("hooks read the server snapshot: idle before priming, success after", async () => {
  const store = createStore();
  const world = client();
  assert.equal(render(createElement(Boundaries, { iso3: "DOM", level: "ADM1" }), store), "<span>idle:0</span>");
  await store.load(keys.boundaries("DOM", "ADM1"), () => world.get("DOM", "ADM1"));
  assert.equal(render(createElement(Boundaries, { iso3: "dom", level: "adm1" }), store), "<span>success:32</span>");
  await store.load(keys.country("DOM"), () => world.country("DOM"));
  assert.equal(render(createElement(Country, { iso3: "DOM" }), store), "<span>success:Dominican Republic</span>");
});

test("enabled: false and nullish arguments stay idle even on a primed store", async () => {
  const store = createStore();
  await store.load(keys.boundaries("DOM", "ADM1"), () => client().get("DOM", "ADM1"));
  assert.equal(render(createElement(Boundaries, { iso3: "DOM", level: "ADM1", enabled: false }), store), "<span>idle:0</span>");
  assert.equal(render(createElement(Boundaries, { iso3: null, level: "ADM1" }), store), "<span>idle:0</span>");
});

test("hooks throw without a provider", () => {
  const error = console.error;
  console.error = () => undefined;
  try {
    assert.throws(() => renderToString(createElement(ClientVersion)), /GeoWorldProvider/);
  } finally {
    console.error = error;
  }
});
