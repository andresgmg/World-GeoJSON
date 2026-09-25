import assert from "node:assert/strict";
import { test } from "node:test";

import { createStore, ensureLoaded, IDLE, keys, resourceKey } from "../src/index.js";

function deferred<T>(): { promise: Promise<T>; resolve: (v: T) => void; reject: (e: unknown) => void } {
  let resolve!: (v: T) => void;
  let reject!: (e: unknown) => void;
  const promise = new Promise<T>((res, rej) => {
    resolve = res;
    reject = rej;
  });
  return { promise, resolve, reject };
}

test("unknown keys report the one IDLE object", () => {
  const store = createStore();
  assert.equal(store.get("a"), IDLE);
  assert.equal(store.get("b"), IDLE);
  assert.equal(IDLE.status, "idle");
  assert.throws(() => {
    (IDLE as { status: string }).status = "x";
  });
});

test("load dedupes concurrent calls and settles to success", async () => {
  const store = createStore();
  const gate = deferred<number>();
  let calls = 0;
  const loader = (): Promise<number> => {
    calls += 1;
    return gate.promise;
  };
  const first = store.load("k", loader);
  const second = store.load("k", loader);
  assert.equal(calls, 1);
  assert.equal(first, second);
  assert.equal(store.get("k").status, "loading");
  gate.resolve(42);
  const state = await first;
  assert.deepEqual(state, { status: "success", data: 42, error: undefined });
  assert.equal(store.get("k"), state);
  await store.load("k", loader); // already succeeded: no new call
  assert.equal(calls, 1);
});

test("errors are states, data survives a failed reload, force reloads", async () => {
  const store = createStore();
  await store.load("k", async () => 1);
  const failed = await store.load("k", async (): Promise<number> => Promise.reject(new Error("boom")), { force: true });
  assert.equal(failed.status, "error");
  assert.equal(failed.data, 1);
  assert.equal((failed.error as Error).message, "boom");
  const again = await store.load("k", async () => 2); // error state: a plain load retries
  assert.deepEqual(again, { status: "success", data: 2, error: undefined });
  let calls = 0;
  await store.load("k", async () => {
    calls += 1;
    return 3;
  });
  assert.equal(calls, 0);
  await store.load(
    "k",
    async () => {
      calls += 1;
      return 3;
    },
    { force: true },
  );
  assert.equal(calls, 1);
  assert.equal(store.get("k").data, 3);
});

test("subscribe notifies per key and unsubscribes", async () => {
  const store = createStore();
  let a = 0;
  let b = 0;
  const off = store.subscribe("a", () => (a += 1));
  store.subscribe("b", () => (b += 1));
  await store.load("a", async () => 1);
  assert.equal(a, 2); // loading, then success
  assert.equal(b, 0);
  off();
  await store.load("a", async () => 2, { force: true });
  assert.equal(a, 2);
});

test("invalidate drops a key and ignores the stale in-flight result", async () => {
  const store = createStore();
  const gate = deferred<number>();
  let notified = 0;
  store.subscribe("k", () => (notified += 1));
  const pending = store.load("k", () => gate.promise);
  store.invalidate("k");
  assert.equal(store.get("k"), IDLE);
  gate.resolve(7);
  const state = await pending;
  assert.equal(state.status, "success"); // the caller still gets the result
  assert.equal(store.get("k"), IDLE); // but the store does not keep it
  assert.equal(notified, 2); // loading + invalidate
  await store.load("x", async () => 1);
  await store.load("y", async () => 2);
  store.invalidate();
  assert.equal(store.get("x"), IDLE);
  assert.equal(store.get("y"), IDLE);
});

test("ensureLoaded only loads idle keys", async () => {
  const store = createStore();
  let calls = 0;
  const loader = async (): Promise<number> => {
    calls += 1;
    return 1;
  };
  ensureLoaded(store, "k", loader);
  ensureLoaded(store, "k", loader);
  await Promise.resolve();
  assert.equal(calls, 1);
  await store.load("k", loader);
  ensureLoaded(store, "k", loader);
  assert.equal(calls, 1);
});

test("keys normalise case and optional parts", () => {
  assert.equal(keys.boundaries("chl", "adm1"), keys.boundaries("CHL", "ADM1"));
  assert.equal(keys.boundaries("CHL", "ADM1"), resourceKey(["boundaries", "CHL", "ADM1", null, false]));
  assert.notEqual(keys.boundaries("CHL", "ADM1"), keys.boundaries("CHL", "ADM1", { preview: true }));
  assert.notEqual(keys.boundaries("USA", "ADM2"), keys.boundaries("USA", "ADM2", { part: "US-CA" }));
  assert.equal(keys.country("dom"), keys.country("DOM"));
  assert.notEqual(keys.feature("A:ADM0:A"), keys.children("A:ADM0:A"));
});
