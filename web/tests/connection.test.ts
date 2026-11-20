import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { AxisConnection } from "../src/data/connection";
import {
  fetchApis,
  fetchDevices,
  fetchHealth,
  fetchInterfaces,
  readInterface,
} from "../src/data/devices";
import wireResults from "./fixtures/websocket.json";

class MockSocket {
  static OPEN = 1;
  static instances: MockSocket[] = [];

  readyState = 0;
  sent: string[] = [];
  onopen: (() => void) | null = null;
  onmessage: ((event: { data: string }) => void) | null = null;
  onclose: ((event: { code: number }) => void) | null = null;

  constructor(readonly url: string) {
    MockSocket.instances.push(this);
  }

  send(message: string): void {
    this.sent.push(message);
  }

  open(): void {
    this.readyState = MockSocket.OPEN;
    this.onopen?.();
  }

  message(payload: unknown): void {
    this.onmessage?.({ data: JSON.stringify(payload) });
  }

  close(): void {
    this.readyState = 3;
  }

  serverClose(code = 1001): void {
    this.close();
    this.onclose?.({ code });
  }
}

beforeEach(() => {
  vi.useFakeTimers();
  MockSocket.instances = [];
  vi.stubGlobal("WebSocket", MockSocket);
  vi.stubGlobal("location", { host: "axis.test" });
});

afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

function connect() {
  const onStatus = vi.fn();
  const connection = new AxisConnection(onStatus);
  connection.connect("private-token");
  const socket = MockSocket.instances[0];
  socket.open();
  return { connection, socket, onStatus };
}

test("waits for authentication readiness and matches out-of-order results to commands", async () => {
  const { connection, socket, onStatus } = connect();
  expect(socket.url).toBe("ws://axis.test/api/websocket");
  expect(JSON.parse(socket.sent[0])).toEqual({ token: "private-token" });
  await expect(fetchDevices(connection)).rejects.toThrow("Not connected.");
  socket.message({ type: "ready", version: 1 });
  expect(onStatus).toHaveBeenLastCalledWith("connected");

  const devices = fetchDevices(connection);
  const health = fetchHealth(connection, "A");
  expect(socket.sent.slice(1).map((message) => JSON.parse(message))).toEqual([
    { id: 1, type: "devices/list" },
    { id: 2, type: "device/health", device: "A" },
  ]);
  socket.message({ id: 2, result: { serial: "A", product: "Camera" } });
  socket.message({ id: 1, result: [{ serial: "A" }] });
  await expect(devices).resolves.toEqual([{ serial: "A" }]);
  await expect(health).resolves.toEqual({ serial: "A", product: "Camera" });
  expect(vi.getTimerCount()).toBe(0);
  connection.disconnect();
});

test("rejects command errors without losing the connection", async () => {
  const { connection, socket } = connect();
  socket.message({ type: "ready" });
  const failure = expect(fetchHealth(connection, "A")).rejects.toThrow(
    "Cannot reach the device.",
  );
  socket.message({
    id: 1,
    error: { code: "connection", message: "Cannot reach the device." },
  });
  await failure;
  const devices = fetchDevices(connection);
  socket.message({ id: 2, result: [] });
  await expect(devices).resolves.toEqual([]);
  connection.disconnect();
});

test("sends the read commands and accepts the shared server responses", async () => {
  const { connection, socket } = connect();
  socket.message({ type: "ready", version: 1 });

  async function check<T>(
    request: Promise<T>,
    expected: Record<string, string>,
    result: NoInfer<T>,
  ) {
    const sent = JSON.parse(socket.sent.at(-1)!);
    expect(sent).toEqual({ id: expect.any(Number), ...expected });
    socket.message({ id: sent.id, result });
    await expect(request).resolves.toEqual(result);
  }

  const device = "SERIAL";
  await check(
    fetchDevices(connection),
    { type: "devices/list" },
    wireResults["devices/list"],
  );
  await check(
    fetchHealth(connection, device),
    { type: "device/health", device },
    wireResults["device/health"],
  );
  await check(
    fetchApis(connection, device),
    { type: "device/apis", device },
    wireResults["device/apis"],
  );
  await check(
    fetchInterfaces(connection, device),
    { type: "device/interfaces", device },
    wireResults["device/interfaces"],
  );
  const name = "light_control";
  await check(
    readInterface(connection, device, name),
    { type: "device/read", device, name },
    wireResults["device/read"],
  );
  connection.disconnect();
});

test("times out stalled commands but accepts subsequent replies", async () => {
  const { connection, socket } = connect();
  socket.message({ type: "ready" });
  const timeout = expect(fetchDevices(connection)).rejects.toThrow(
    "Request timed out.",
  );
  await vi.advanceTimersByTimeAsync(65000);
  await timeout;
  socket.message({ id: 1, result: ["late"] });
  const devices = fetchDevices(connection);
  socket.message({ id: 2, result: [] });
  await expect(devices).resolves.toEqual([]);
  expect(vi.getTimerCount()).toBe(0);
  connection.disconnect();
});

test("reconnects after an unexpected close and ignores obsolete socket callbacks", async () => {
  const { connection, socket } = connect();
  socket.message({ type: "ready" });
  const failure = expect(fetchDevices(connection)).rejects.toThrow(
    "Connection lost",
  );
  socket.serverClose();
  await failure;
  await vi.advanceTimersByTimeAsync(2000);
  const replacement = MockSocket.instances[1];
  replacement.open();
  expect(JSON.parse(replacement.sent[0])).toEqual({ token: "private-token" });
  replacement.message({ type: "ready" });
  const devices = fetchDevices(connection);
  socket.message({ id: 2, result: ["obsolete"] });
  socket.serverClose(1008);
  replacement.message({ id: 2, result: [] });
  await expect(devices).resolves.toEqual([]);
  expect(vi.getTimerCount()).toBe(0);
  connection.disconnect();
});

test("does not automatically reconnect after an authentication rejection", async () => {
  const { connection, socket, onStatus } = connect();
  socket.serverClose(1008);
  expect(onStatus).toHaveBeenLastCalledWith("denied");
  await vi.advanceTimersByTimeAsync(10000);
  expect(MockSocket.instances).toHaveLength(1);
  connection.disconnect();
});

test("disconnect cancels pending operations and a scheduled reconnect", async () => {
  const { connection, socket } = connect();
  socket.message({ type: "ready" });
  const failure = expect(fetchDevices(connection)).rejects.toThrow(
    "Connection lost",
  );
  connection.disconnect();
  await failure;
  socket.serverClose();
  expect(vi.getTimerCount()).toBe(0);

  connection.connect("replacement-token");
  MockSocket.instances[1].serverClose();
  connection.disconnect();
  await vi.advanceTimersByTimeAsync(10000);
  expect(MockSocket.instances).toHaveLength(2);
});
