import { expect, test } from "@playwright/test";
import { fileURLToPath } from "node:url";

const devices = [
  {
    serial: "A",
    alias: "Camera A",
    host: "camera-a",
    model: "",
    discovery: null,
  },
  {
    serial: "B",
    alias: "Camera B",
    host: "camera-b",
    model: "",
    discovery: null,
  },
];

async function openApp(
  page,
  savedDevices = devices,
  ready = () => true,
  holdInitialDiscovery = false,
  architecture = "armv7hf",
  holdPolicy = false,
) {
  const requests = [];
  const automaticScans = [];
  const sockets = [];
  const tokens = [];
  await page.route("http://axis.test/**", (route) => {
    const script = new URL(route.request().url()).pathname === "/app.js";
    return route.fulfill({
      path: fileURLToPath(
        new URL(
          script
            ? "../../axis/web/static/app.js"
            : "../../axis/web/static/index.html",
          import.meta.url,
        ),
      ),
      contentType: script ? "text/javascript" : "text/html",
      headers: {
        "Content-Security-Policy":
          "default-src 'self'; connect-src 'self' ws://axis.test; style-src 'self' 'unsafe-inline'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'",
      },
    });
  });
  await page.routeWebSocket("ws://axis.test/api/websocket", (socket) => {
    sockets.push(socket);
    let firstDiscovery = true;
    socket.onMessage((raw) => {
      const message = JSON.parse(raw);
      if ("token" in message) {
        tokens.push(message.token);
        if (ready()) socket.send(JSON.stringify({ type: "ready", version: 1 }));
      } else if (message.type === "devices/list") {
        socket.send(JSON.stringify({ id: message.id, result: savedDevices }));
      } else if (message.type === "device/architecture") {
        socket.send(
          JSON.stringify(
            architecture === null
              ? {
                  id: message.id,
                  error: { message: "Architecture unavailable." },
                }
              : { id: message.id, result: architecture },
          ),
        );
      } else if (message.type === "device/application-sdks") {
        socket.send(
          JSON.stringify({ id: message.id, result: ["acap4-native"] }),
        );
      } else if (message.type === "device/application-policy" && !holdPolicy) {
        socket.send(JSON.stringify({ id: message.id, result: false }));
      } else if (message.type === "devices/discover" && firstDiscovery) {
        firstDiscovery = false;
        automaticScans.push({ ...message, socket });
        if (!holdInitialDiscovery)
          socket.send(JSON.stringify({ id: message.id, result: [] }));
      } else {
        requests.push({ ...message, socket });
      }
    });
  });
  await page.goto("http://axis.test/#first-token");
  await expect(
    page.getByRole("button", { name: "Camera A", exact: false }),
  ).toBeEnabled();
  if (!holdInitialDiscovery)
    await expect(
      page.getByRole("button", { name: "Discover devices · No new devices" }),
    ).toBeEnabled();
  return { requests, automaticScans, sockets, tokens };
}

async function respond(page, request, result, error) {
  request.socket.send(JSON.stringify({ id: request.id, result, error }));
  await page.waitForFunction(
    (id) => !document.querySelector("axis-app").connection.pending.has(id),
    request.id,
  );
}

function health(product) {
  return {
    serial: "A",
    product,
    model: "Model",
    firmware_version: "1",
    observed_at: "now",
  };
}

async function select(page, name, requests, count) {
  if (await page.getByRole("dialog").isVisible())
    await page.keyboard.press("Escape");
  await page
    .getByRole("button", { name: `Camera ${name}`, exact: false })
    .click();
  await expect.poll(() => requests.length).toBe(count);
}

test("discovers automatically and shows distinct discovered tiles in the saved device list", async ({
  page,
}) => {
  const { automaticScans } = await openApp(
    page,
    [
      { ...devices[0], serial: "00408C010204", model: "Saved camera" },
      { ...devices[1], alias: "Camera B M3115 Lobby", model: "AXIS M3115-LVE" },
    ],
    undefined,
    true,
  );
  const scan = page.getByRole("button", {
    name: /^Discover devices/,
  });
  const scanning = page.getByRole("button", { name: "Discovering devices…" });
  await expect(scanning).toBeDisabled();
  await expect.poll(() => automaticScans.length).toBe(1);
  const [request] = automaticScans;
  expect(request.stream).toBe(true);
  const provisional = {
    name: "Provisional camera",
    host: "192.0.2.12",
    macaddress: "00:40:8c:01:02:12",
  };
  request.socket.send(
    JSON.stringify({
      id: request.id,
      type: "discovery/device",
      device: provisional,
    }),
  );
  const tile = page.getByRole("button", {
    name: /Provisional camera.*Discovered/,
  });
  await expect(tile).toBeVisible();
  await expect(scanning).toBeVisible();
  await tile.click();
  const preview = page.getByRole("dialog", { name: provisional.name });
  await expect(preview.getByLabel("Username")).toBeEditable();
  const previewTest = preview.getByRole("button", { name: "Test connection" });
  await expect(previewTest).toBeDisabled();
  await respond(page, request, [
    {
      name: "<b>Entrance camera</b>",
      host: "192.0.2.2",
      macaddress: "00:40:8c:01:02:03",
      model: "Test camera",
    },
  ]);
  await expect(
    preview
      .getByRole("paragraph")
      .filter({ hasText: "This device was not confirmed" }),
  ).toBeVisible();
  await expect(previewTest).toBeDisabled();
  await preview.getByRole("button", { name: "Close", exact: true }).click();
  await expect(tile).toHaveCount(0);
  await expect(scan).toHaveAccessibleName("Discover devices · 1 new");
  const list = page.getByRole("list", { name: "Devices", exact: true });
  await expect(
    page.getByRole("heading", { name: "Devices", exact: true }),
  ).toHaveCount(0);
  const saved = list.getByRole("button", { name: /Camera A/ });
  const discovered = list
    .getByRole("listitem")
    .filter({ hasText: "<b>Entrance camera</b>" });
  await expect(discovered).toBeVisible();
  await expect(discovered.locator(".device-name")).toHaveText(
    "<b>Entrance camera</b>",
  );
  await expect(discovered.locator(".device-meta")).toHaveText(
    "192.0.2.2 — 00:40:8c:01:02:03 — Test camera",
  );
  await expect(discovered).toContainText("Discovered");
  const discoveredButton = discovered.getByRole("button");
  await expect(discoveredButton).toBeEnabled();
  await expect(saved).toBeEnabled();
  await expect(saved).toHaveAccessibleName(
    "Camera A camera-a — 00:40:8c:01:02:04",
  );
  const secondSaved = list.getByRole("button", {
    name: "Camera B M3115 Lobby camera-b",
    exact: true,
  });
  await expect(secondSaved).toBeVisible();
  const deviceNameBox = await discovered.locator(".device-name").boundingBox();
  const deviceMetaBox = await discovered.locator(".device-meta").boundingBox();
  expect(deviceMetaBox.y).toBeGreaterThanOrEqual(
    deviceNameBox.y + deviceNameBox.height,
  );
  const savedBox = await saved.boundingBox();
  const secondSavedBox = await secondSaved.boundingBox();
  const discoveredBox = await discoveredButton.boundingBox();
  expect(secondSavedBox.y).toBeGreaterThanOrEqual(savedBox.y + savedBox.height);
  expect(discoveredBox.y).toBeGreaterThanOrEqual(
    secondSavedBox.y + secondSavedBox.height,
  );
  expect(discoveredBox.x).toBeCloseTo(savedBox.x);
  expect(discoveredBox.width).toBeCloseTo(savedBox.width);
  const scanBox = await scan.boundingBox();
  expect(scanBox.y).toBeGreaterThanOrEqual(
    discoveredBox.y + discoveredBox.height,
  );
  expect(scanBox.x + scanBox.width).toBeCloseTo(savedBox.x + savedBox.width);
  const savedOutline = await saved.evaluate(
    (button) => getComputedStyle(button).borderTopColor,
  );
  await expect(discoveredButton).toHaveCSS("border-top-style", "solid");
  await expect(discoveredButton).not.toHaveCSS(
    "border-top-color",
    savedOutline,
  );
  await expect(scan).toBeEnabled();
});

test("saves a discovered device with a custom port and protocol and opens Health", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 480 });
  const saved = [...devices];
  const { requests } = await openApp(page, saved);
  await page.getByRole("button", { name: /^Discover devices/ }).click();
  await expect.poll(() => requests.length).toBe(1);
  const found = {
    name: "Entrance camera",
    host: "192.0.2.2",
    macaddress: "00:40:8c:01:02:03",
  };
  requests[0].socket.send(
    JSON.stringify({
      id: requests[0].id,
      type: "discovery/device",
      device: found,
    }),
  );
  await page
    .getByRole("button", { name: /Entrance camera.*Discovered/ })
    .click();
  const dialog = page.getByRole("dialog", { name: found.name });
  await expect(
    dialog.getByRole("heading", { name: "Save discovered device" }),
  ).toBeVisible();
  await expect(
    dialog.getByRole("group", { name: "General" }).getByLabel("Alias"),
  ).toHaveAttribute("placeholder", found.name);
  const connection = dialog.getByRole("group", { name: "Connection" });
  await expect(connection.getByLabel("Address")).toHaveValue(found.host);
  await expect(connection.getByLabel("Address")).not.toBeEditable();
  const port = connection.getByLabel("Port");
  await expect(port).toHaveValue("443");
  const advanced = dialog.getByRole("group", { name: "Advanced" });
  const protocol = advanced.getByLabel("Protocol");
  await expect(protocol).toHaveValue("https");
  const verify = advanced.getByRole("checkbox", {
    name: "Verify HTTPS certificates",
  });
  await expect(verify).not.toBeChecked();
  await connection.getByLabel("Username").fill("root");
  const password = connection.getByLabel("Password");
  await password.fill("dummy-test-password");
  await dialog.getByLabel("Alias").fill("Entrance");
  const testConnection = dialog
    .locator("axis-button")
    .filter({ hasText: "Test connection" });
  const save = dialog.locator("axis-button").filter({ hasText: "Save device" });
  await expect(save.getByRole("button")).toBeDisabled();
  await expect(testConnection.getByRole("button")).toBeDisabled();
  await respond(page, requests[0], [found]);
  await expect(password).toHaveValue("dummy-test-password");
  await expect(testConnection.getByRole("button")).toBeEnabled();
  const testLabel = testConnection.locator('[part="label"]');
  await testConnection.scrollIntoViewIfNeeded();
  const labelBounds = await testLabel.boundingBox();
  expect(labelBounds).not.toBeNull();
  await testConnection.click();
  await expect.poll(() => requests.length).toBe(2);
  await expect(testConnection).toHaveAttribute("busy", "");
  const testBounds = await testConnection.boundingBox();
  expect(await testLabel.boundingBox()).toEqual(labelBounds);
  expect(requests[1]).toMatchObject({
    type: "devices/test-connection",
    host: found.host,
    password: "dummy-test-password",
  });
  await respond(page, requests.pop(), "NEW");
  await expect(testConnection).toHaveAttribute("variant", "success");
  await expect(testConnection.getByRole("button")).toHaveCSS(
    "border-top-color",
    "rgb(0, 107, 60)",
  );
  await expect(testConnection).toHaveAttribute(
    "title",
    "Connection successful (serial: NEW).",
  );
  expect(await testConnection.boundingBox()).toEqual(testBounds);
  expect(await testLabel.boundingBox()).toEqual(labelBounds);
  await expect(testConnection).toHaveText("Test connection");
  await expect(password).toHaveValue("dummy-test-password");
  await dialog.getByRole("button", { name: "Save device" }).click();
  await expect.poll(() => requests.length).toBe(2);
  await expect(save).toHaveAttribute("busy", "");
  await expect(save.getByRole("button")).toBeDisabled();
  expect(requests[1]).toMatchObject({
    type: "devices/save",
    host: found.host,
    username: "root",
    password: "dummy-test-password",
    alias: "Entrance",
    port: 0,
    web_proto: "https",
    verify_ssl: false,
  });
  await expect(password).toHaveValue("");
  await respond(page, requests[1], undefined, {
    code: "authentication",
    message: "Invalid device credentials.",
  });
  await expect(page.getByRole("alert")).toHaveText(
    "Invalid device credentials.",
  );
  await port.fill("8443");
  await protocol.selectOption("http");
  await expect(port).toHaveValue("80");
  await port.fill("8080");
  await protocol.selectOption("https");
  await expect(port).toHaveValue("8443");
  await protocol.selectOption("http");
  await expect(port).toHaveValue("8080");
  await password.fill("new-dummy-password");
  await expect(save.getByRole("button")).toBeDisabled();
  await testConnection.click();
  await expect.poll(() => requests.length).toBe(3);
  await respond(page, requests.pop(), "NEW");
  await expect(testConnection).toHaveAttribute("variant", "success");
  await page.getByRole("button", { name: "Save device" }).click();
  await expect.poll(() => requests.length).toBe(3);
  expect(requests[2]).toMatchObject({
    type: "devices/save",
    host: found.host,
    port: 8080,
    web_proto: "http",
  });

  saved.push({
    ...devices[0],
    alias: "Entrance",
    host: found.host,
    serial: "NEW",
    port: 8080,
    web_proto: "http",
    discovery: { macaddress: found.macaddress },
  });
  await respond(page, requests[2], "NEW");
  await expect(
    page.getByRole("heading", { name: "Save discovered device" }),
  ).toHaveCount(0);
  await expect(page.getByRole("button", { name: /Discovered/ })).toHaveCount(0);
  await expect(page.getByRole("dialog", { name: "Entrance" })).toBeVisible();
  await expect.poll(() => requests.length).toBe(4);
  expect(requests[3]).toMatchObject({ type: "device/health", device: "NEW" });
  await page.getByRole("button", { name: "Close", exact: true }).click();
  await expect(
    page.getByRole("button", { name: /^Entrance 192\.0\.2\.2/ }),
  ).toBeEnabled();
});

test("keeps saved tiles when discovery reports the same devices", async ({
  page,
}) => {
  const { requests } = await openApp(page, [
    { ...devices[0], host: "192.0.2.2" },
    { ...devices[1], serial: "ACCC8E010203" },
    {
      ...devices[1],
      alias: "Camera C",
      serial: "OTHER",
      discovery: { macaddress: "B8-A4-4F-01-02-03*" },
    },
  ]);
  const scan = page.getByRole("button", {
    name: /^Discover devices/,
  });
  const savedAnnouncements = [
    {
      name: "Saved by serial",
      host: "192.0.2.3",
      serial: "A",
      macaddress: "00:40:8c:01:02:03",
    },
    {
      name: "Saved with MAC as serial",
      host: "192.0.2.4",
      macaddress: "ac:cc:8e:01:02:03",
    },
    {
      name: "Saved with previous discovery metadata",
      host: "192.0.2.5",
      macaddress: "b8:a4:4f:01:02:03",
    },
  ];

  await scan.click();
  await expect.poll(() => requests.length).toBe(1);
  await respond(page, requests[0], [
    ...savedAnnouncements,
    {
      name: "Different camera at a saved address",
      host: "192.0.2.2",
      macaddress: "00:40:8c:01:02:04",
    },
  ]);
  const list = page.getByRole("list", { name: "Devices", exact: true });
  await expect(list.getByRole("listitem")).toHaveCount(4);
  await expect(list.getByRole("button", { name: /^Camera [ABC]/ })).toHaveCount(
    3,
  );
  await expect(scan).toHaveAccessibleName("Discover devices · 1 new");
  await expect(list).toContainText("Different camera at a saved address");

  await scan.click();
  await expect.poll(() => requests.length).toBe(2);
  const previousResult = list.getByRole("button", {
    name: /Different camera at a saved address/,
  });
  await expect(previousResult).toBeVisible();
  await expect(previousResult).toBeEnabled();
  await expect(list.getByRole("button", { name: /Camera A/ })).toBeEnabled();
  await respond(page, requests[1], savedAnnouncements);
  await expect(scan).toHaveAccessibleName("Discover devices · No new devices");
  await expect(page.locator(".scan-status")).toHaveText(
    "All discovered devices are already saved.",
  );
  await expect(list.getByRole("listitem")).toHaveCount(3);
});

test("reports a failed scan and can retry with no results", async ({
  page,
}) => {
  const { requests } = await openApp(page);
  const scan = page.getByRole("button", { name: /^Discover devices/ });
  await scan.click();
  await expect.poll(() => requests.length).toBe(1);
  await respond(page, requests[0], undefined, {
    code: "operation",
    message: "Device discovery failed.",
  });
  const retry = page.getByRole("button", { name: "Retry discovery · Failed" });
  await expect(retry).toHaveAccessibleDescription("Device discovery failed.");
  await expect(page.getByText("Device discovery failed.")).not.toBeInViewport();
  await retry.click();
  await expect.poll(() => requests.length).toBe(2);
  await respond(page, requests[1], []);
  await expect(
    page.getByRole("button", { name: "Discover devices · No new devices" }),
  ).toBeEnabled();
  await expect(page.getByRole("alert")).toHaveCount(0);
});

test("moves the scan outline unless reduced motion is enabled", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "no-preference" });
  const { requests } = await openApp(page);
  await page.getByRole("button", { name: /^Discover devices/ }).click();
  await expect.poll(() => requests.length).toBe(1);
  const outline = page.locator(".scan-control .busy-outline rect");
  await expect(outline).toBeInViewport();
  await expect(outline).toHaveCSS("stroke-dasharray", "3px, 2px");
  const readOffset = () =>
    outline.evaluate((rect) => getComputedStyle(rect).strokeDashoffset);
  const offset = await readOffset();
  await expect.poll(readOffset).not.toBe(offset);
  await page.emulateMedia({ reducedMotion: "reduce" });
  await expect(outline).toHaveCSS("animation-name", "none");
  await expect(outline).toHaveCSS("stroke-dasharray", "3px, 2px");
  await respond(page, requests[0], []);
  await expect(outline).toHaveCount(0);
});

for (const outcome of ["success", "error"]) {
  test(`ignores obsolete health ${outcome} after selecting A, B, A`, async ({
    page,
  }) => {
    const { requests } = await openApp(page);
    await select(page, "A", requests, 1);
    await select(page, "B", requests, 2);
    await select(page, "A", requests, 3);

    await respond(
      page,
      requests[0],
      outcome === "success" ? health("Obsolete") : undefined,
      outcome === "error"
        ? { code: "connection", message: "Obsolete error" }
        : undefined,
    );
    await respond(page, requests[1], { serial: "B", product: "Wrong device" });
    await expect(
      page.getByRole("button", { name: "Health", exact: true }),
    ).toHaveAttribute("aria-busy", "true");
    await expect(page.getByText("Obsolete", { exact: true })).toHaveCount(0);
    await expect(page.getByRole("alert")).toHaveCount(0);

    await respond(page, requests[2], health("Current"));
    await expect(page.getByText("Current", { exact: true })).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Health", exact: true }),
    ).toBeEnabled();
  });
}

for (const outcome of ["success", "error"]) {
  test(`ignores obsolete browse ${outcome} after leaving and returning`, async ({
    page,
  }) => {
    const { requests } = await openApp(page);
    await select(page, "A", requests, 1);
    await respond(page, requests[0], health("Initial"));
    await page.getByRole("button", { name: "Interfaces", exact: true }).click();
    await expect.poll(() => requests.length).toBe(2);
    await select(page, "B", requests, 3);
    await select(page, "A", requests, 4);

    await respond(
      page,
      requests[1],
      outcome === "success"
        ? [{ name: "Obsolete", supported: true }]
        : undefined,
      outcome === "error"
        ? { code: "connection", message: "Obsolete error" }
        : undefined,
    );
    await expect(
      page.getByRole("button", { name: "Health", exact: true }),
    ).toHaveAttribute("aria-busy", "true");
    await expect(page.getByRole("button", { name: "Obsolete" })).toHaveCount(0);
    await expect(page.locator("pre")).toHaveCount(0);
    await expect(page.getByRole("alert")).toHaveCount(0);

    await respond(page, requests[3], health("Current"));
    await expect(page.getByText("Current", { exact: true })).toBeVisible();
  });
}

test("keeps the newest health when an older response arrives last", async ({
  page,
}) => {
  const { requests } = await openApp(page);
  await select(page, "A", requests, 1);
  await select(page, "B", requests, 2);
  await select(page, "A", requests, 3);
  await respond(page, requests[2], health("Current"));
  await expect(page.getByText("Current", { exact: true })).toBeVisible();
  await respond(page, requests[0], health("Obsolete"));
  await expect(page.getByText("Current", { exact: true })).toBeVisible();
  await expect(page.getByText("Obsolete", { exact: true })).toHaveCount(0);
});

test("ignores an outstanding read after dismissal", async ({ page }) => {
  const { requests } = await openApp(page);
  await expect(page.getByRole("button", { name: "Refresh list" })).toHaveCount(
    0,
  );
  await select(page, "A", requests, 1);
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toBeHidden();
  await respond(page, requests[0], undefined, {
    code: "connection",
    message: "Obsolete error",
  });
  await expect(page.getByRole("alert")).toHaveCount(0);
  await expect(page.locator("axis-button[busy]")).toHaveCount(0);
});

for (const state of ["complete", "scanning"]) {
  test(`keeps ${state} discovery results visible when disconnected`, async ({
    page,
  }) => {
    await page.clock.install();
    const { requests, automaticScans, sockets } = await openApp(
      page,
      devices,
      undefined,
      true,
    );
    await expect.poll(() => automaticScans.length).toBe(1);
    const found = {
      name: "Entrance camera",
      host: "192.0.2.2",
      macaddress: "00:40:8c:01:02:03",
    };
    const first = automaticScans[0];
    first.socket.send(
      JSON.stringify({
        id: first.id,
        type: "discovery/device",
        device: found,
      }),
    );
    const tile = page.getByRole("button", {
      name: /Entrance camera.*Discovered/,
    });
    await expect(tile).toBeVisible();
    if (state === "complete") await respond(page, first, [found]);
    sockets[0].close({ code: 1001 });
    await expect(tile).toBeVisible();
    await expect(tile).toBeDisabled();
    await expect(page.locator("main .connection-status")).toHaveText(
      "Reconnecting to Axis…",
    );

    await page.clock.fastForward(2100);
    await expect.poll(() => automaticScans.length).toBe(2);
    await expect(tile).toBeVisible();
    await tile.click();
    const dialog = page.getByRole("dialog", { name: found.name });
    await expect(
      dialog.getByRole("button", { name: "Test connection" }),
    ).toBeDisabled();
    await respond(page, automaticScans[1], undefined, {
      code: "connection",
      message: "Device discovery failed.",
    });
    await expect(
      dialog
        .getByRole("paragraph")
        .filter({ hasText: "This device was not confirmed" }),
    ).toBeVisible();
    await dialog.getByRole("button", { name: "Close", exact: true }).click();
    await expect(tile).toBeVisible();
    await page
      .getByRole("button", { name: "Retry discovery · Failed" })
      .click();
    await expect.poll(() => requests.length).toBe(1);
    await expect(tile).toBeVisible();
    await respond(page, requests[0], []);
    await expect(tile).toHaveCount(0);
  });
}

test("clicking outside closes a device modal, including Settings", async ({
  page,
}) => {
  const { requests } = await openApp(page);
  await select(page, "A", requests, 1);
  await respond(page, requests[0], health("Camera"));
  const dialog = page.getByRole("dialog");
  await dialog.getByText("Camera", { exact: true }).click();
  await expect(dialog).toBeVisible();
  await page.mouse.click(2, 2);
  await expect(dialog).toBeHidden();

  await select(page, "A", requests, 2);
  await respond(page, requests[1], health("Camera"));
  await dialog.getByRole("button", { name: "Settings", exact: true }).click();
  await expect.poll(() => requests.length).toBe(3);
  await respond(page, requests[2], {
    device: { ...devices[0], web_proto: "https", port: 0, verify_ssl: true },
    username: "operator",
  });
  await dialog.getByLabel("Alias").fill("Unsaved");
  await page.mouse.click(2, 2);
  await expect(dialog).toBeHidden();
  await expect(page.getByRole("button", { name: /Camera A/ })).toBeVisible();
});

test("keeps Interfaces in place through repeated connection retries", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 600 });
  await page.emulateMedia({
    colorScheme: "light",
    reducedMotion: "no-preference",
  });
  await page.clock.install();
  let ready = true;
  const { requests, automaticScans, sockets, tokens } = await openApp(
    page,
    devices,
    () => ready,
  );
  await select(page, "A", requests, 1);
  const dialog = page.getByRole("dialog");
  await dialog.getByRole("button", { name: "Interfaces", exact: true }).click();
  await expect.poll(() => requests.length).toBe(2);
  await respond(page, requests[1], [{ name: "Light", supported: true }]);
  await dialog.getByRole("button", { name: "Light", exact: true }).click();
  await expect.poll(() => requests.length).toBe(3);
  await respond(page, requests[2], { enabled: true });

  const data = dialog.locator("pre");
  await expect(data).toContainText('"enabled": true');
  const originalBounds = await data.boundingBox();
  await expect(dialog.locator(".connection-status")).toHaveCount(0);
  const status = page.locator("main .connection-status");
  await expect(status).toHaveCSS("background-color", "rgb(0, 107, 60)");
  await expect(status).toHaveCSS("animation-name", "none");
  const listTop = await page
    .locator("axis-device-list")
    .evaluate((list) => list.getBoundingClientRect().top);
  ready = false;
  sockets[0].close({ code: 1001 });
  await expect(status).toHaveText("Reconnecting to Axis…");
  await expect(status).toHaveCSS("background-color", "rgb(169, 76, 0)");
  await expect(status).toHaveCSS("animation-name", "connection-pulse");
  await page.emulateMedia({ reducedMotion: "reduce" });
  await expect(status).toHaveCSS("animation-name", "none");
  expect(await data.boundingBox()).toEqual(originalBounds);
  await page.clock.fastForward(2100);
  await expect.poll(() => tokens.length).toBe(2);
  await expect(status).toHaveText("Reconnecting to Axis…");
  sockets[1].close({ code: 1001 });
  await page.clock.fastForward(2100);
  await expect.poll(() => tokens.length).toBe(3);
  await expect(status).toHaveText("Reconnecting to Axis…");
  expect(await data.boundingBox()).toEqual(originalBounds);
  expect(
    await page
      .locator("axis-device-list")
      .evaluate((list) => list.getBoundingClientRect().top),
  ).toBe(listTop);

  sockets[2].send(JSON.stringify({ type: "ready", version: 1 }));
  await expect.poll(() => automaticScans.length).toBe(2);
  await expect(status).toHaveText("Connected to Axis");
  await expect(status).toHaveCSS("background-color", "rgb(0, 107, 60)");
  await expect(
    dialog.getByRole("button", { name: "Light", exact: true }),
  ).toHaveAttribute("aria-pressed", "true");
  await expect(data).toContainText('"enabled": true');
  expect(await data.boundingBox()).toEqual(originalBounds);
});

for (const state of ["connected", "denied", "disconnected"]) {
  test(`uses a replacement link when ${state} without reloading`, async ({
    page,
  }) => {
    await page.emulateMedia({ colorScheme: "light" });
    await page.clock.install();
    const { requests, sockets, tokens } = await openApp(page);
    await select(page, "A", requests, 1);
    if (state !== "connected") {
      sockets[0].close({ code: state === "denied" ? 1008 : 1001 });
      await expect(page.locator("main .connection-status")).toHaveText(
        state === "denied" ? "Access link rejected" : "Reconnecting to Axis…",
      );
      if (state === "denied") {
        const indicator = page.locator("main .connection-status");
        await expect(indicator).toHaveCSS("background-color", "rgb(160, 0, 0)");
        await expect(indicator).toHaveCSS("animation-name", "none");
        await expect(page.getByRole("alert")).toHaveText(
          "Open the private URL printed by the running server.",
        );
      }
    }
    await page.evaluate(() => {
      location.hash = "replacement-token";
    });
    await expect
      .poll(() => tokens)
      .toEqual(["first-token", "replacement-token"]);
    await expect.poll(() => requests.length).toBe(2);
    await expect(page).toHaveURL("http://axis.test/");
    expect(
      await page.evaluate(() => sessionStorage.getItem("axis-token")),
    ).toBe("replacement-token");

    await respond(page, requests[1], health("Reconnected"));
    await expect(page.getByText("Reconnected", { exact: true })).toBeVisible();
    await expect(page.getByRole("alert")).toHaveCount(0);
    await page.clock.fastForward(2500);
    expect(sockets).toHaveLength(2);
    expect(tokens).toEqual(["first-token", "replacement-token"]);
  });
}

test("server settings select discovery interfaces and show warnings", async ({
  page,
}) => {
  const { requests } = await openApp(page);
  const open = page.getByRole("button", {
    name: "Server settings",
    exact: true,
  });
  await open.click();
  await expect.poll(() => requests.length).toBe(1);
  expect(requests[0].type).toBe("server/settings");
  await respond(page, requests[0], {
    selected: null,
    interfaces: [
      { name: "lan", label: "Ethernet", addresses: ["192.0.2.10"], up: true },
      { name: "vpn", label: "VPN", addresses: [], up: false },
    ],
  });
  const dialog = page.getByRole("dialog", { name: "Server settings" });
  await dialog.getByLabel("Use selected interfaces").check();
  await expect(dialog.getByLabel(/Ethernet/)).toBeChecked();
  await dialog.getByLabel(/VPN/).check();
  await dialog.getByRole("button", { name: "Save settings" }).click();
  await expect.poll(() => requests.length).toBe(2);
  expect(requests[1]).toMatchObject({
    type: "server/configure",
    interfaces: ["lan", "vpn"],
  });
  await respond(page, requests[1], {
    selected: ["lan", "vpn"],
    interfaces: [],
  });
  await expect(dialog).not.toBeVisible();
  await expect(open).toBeFocused();

  await page.getByRole("button", { name: /Discover devices/ }).click();
  await expect.poll(() => requests.length).toBe(3);
  requests[2].socket.send(
    JSON.stringify({
      id: requests[2].id,
      type: "discovery/warning",
      message: "Selected interfaces are down or unavailable: vpn",
    }),
  );
  await respond(page, requests[2], []);
  await expect(
    page.getByRole("status").filter({ hasText: "vpn" }),
  ).toBeVisible();
});

test("dialog controls respond to hover in both themes", async ({ page }) => {
  const { requests } = await openApp(page);
  await select(page, "A", requests, 1);
  const dialog = page.getByRole("dialog", { name: "Camera A" });
  for (const scheme of ["light", "dark"]) {
    await page.emulateMedia({ colorScheme: scheme });
    for (const name of ["Settings", "Close"]) {
      const button = dialog.getByRole("button", { name, exact: true });
      await page.mouse.move(0, 0);
      const background = await button.evaluate(
        (element) => getComputedStyle(element).backgroundColor,
      );
      await button.hover();
      await expect(button).not.toHaveCSS("background-color", background);
      await expect(button).toHaveCSS("cursor", "pointer");
    }
  }
  const settings = dialog.getByRole("button", { name: "Settings" });
  await page.mouse.move(0, 0);
  await settings.evaluate((button) => (button.disabled = true));
  const disabledBackground = await settings.evaluate(
    (element) => getComputedStyle(element).backgroundColor,
  );
  await settings.hover();
  await expect(settings).toHaveCSS("background-color", disabledBackground);
});

test("applications present details, configuration links, and confirmed controls", async ({
  page,
}) => {
  const { requests } = await openApp(page, [
    { ...devices[0], web_proto: "https", port: 0 },
    devices[1],
  ]);
  await select(page, "A", requests, 1);
  await respond(page, requests[0], health("Camera"));
  const dialog = page.getByRole("dialog");
  await dialog.getByRole("button", { name: "Interfaces" }).click();
  await expect.poll(() => requests.length).toBe(2);
  await respond(page, requests[1], [{ name: "applications", supported: true }]);
  await dialog.getByRole("button", { name: "applications" }).click();
  await expect(dialog).toHaveAccessibleName("Applications");
  await expect(dialog.getByRole("button", { name: "Back" })).toBeFocused();
  await expect.poll(() => requests.length).toBe(3);
  expect(requests[2]).toMatchObject({
    type: "device/applications",
    device: "A",
  });
  const apps = [
    {
      name: "objectanalytics",
      nice_name: "Object Analytics",
      status: "Stopped",
      version: "2.0",
      vendor: "Axis",
      license_status: "None",
      configuration_page: "local/objectanalytics/index.html",
    },
    {
      name: "other",
      nice_name: "Other",
      status: "Running",
      version: "1.0",
      vendor: "Axis",
      license_status: "Valid",
      configuration_page: "//evil.example/",
    },
  ];
  await respond(page, requests[2], apps);
  const app = dialog
    .locator("axis-card")
    .filter({ has: page.getByRole("heading", { name: "Object Analytics" }) })
    .last();
  await expect(app).toContainText("Stopped");
  await expect(app).toContainText("2.0");
  const disabledConfiguration = app.getByRole("button", {
    name: "Open configuration",
  });
  await expect(disabledConfiguration).toBeDisabled();
  await expect(
    app.getByRole("link", { name: "Open configuration" }),
  ).toHaveCount(0);
  await expect(
    dialog.getByRole("link", { name: "Open configuration" }),
  ).toHaveCount(0);
  await app.getByRole("button", { name: "Start" }).click();
  await expect(app.getByText("Start Object Analytics?")).toBeVisible();
  await app.getByRole("button", { name: "Cancel" }).click();
  expect(requests).toHaveLength(3);
  await app.getByRole("button", { name: "Start" }).click();
  await app.getByRole("button", { name: "Confirm start" }).click();
  await expect.poll(() => requests.length).toBe(4);
  expect(requests[3]).toMatchObject({
    type: "device/application-action",
    device: "A",
    action: "start",
    package: "objectanalytics",
    version: "2.0",
    status: "Stopped",
    confirmed: true,
  });
  await expect(dialog.getByRole("button", { name: "Back" })).toBeDisabled();
  await expect(dialog.getByRole("button", { name: "Close" })).toBeDisabled();
  await page.keyboard.press("Escape");
  await expect(dialog).toBeVisible();
  await respond(page, requests[3], null);
  await expect.poll(() => requests.length).toBe(5);
  await respond(page, requests[4], [
    { ...apps[0], status: "Running" },
    apps[1],
  ]);
  await expect(app.getByRole("button", { name: "Stop" })).toBeVisible();
  const link = app.getByRole("link", { name: "Open configuration" });
  await expect(link).toHaveAttribute(
    "href",
    "https://camera-a/local/objectanalytics/index.html",
  );
  await expect(link).toHaveAttribute("target", "_blank");
  await expect(link).toHaveAttribute("rel", "noopener noreferrer");
  await app.getByRole("button", { name: "Uninstall" }).click();
  await expect(
    app.getByText("Uninstall Object Analytics and remove its data?"),
  ).toBeVisible();
  await app.getByRole("button", { name: "Cancel" }).click();
  expect(requests).toHaveLength(5);
  await app.getByRole("button", { name: "Uninstall" }).click();
  await app.getByRole("button", { name: "Confirm uninstall" }).click();
  await expect.poll(() => requests.length).toBe(6);
  expect(requests[5]).toMatchObject({
    type: "device/application-action",
    action: "remove",
    package: "objectanalytics",
    status: "Running",
    confirmed: true,
  });
  await respond(page, requests[5], null);
  await expect.poll(() => requests.length).toBe(7);
  await respond(page, requests[6], [apps[1]]);
  await expect(
    dialog.getByRole("heading", { name: "Object Analytics" }),
  ).toHaveCount(0);
  await dialog.getByRole("button", { name: "Back" }).click();
  await expect.poll(() => requests.length).toBe(8);
  expect(requests[7]).toMatchObject({ type: "device/interfaces" });
});

test("license management offers removal only for an installed license", async ({
  page,
}) => {
  const { requests } = await openApp(page);
  await select(page, "A", requests, 1);
  await respond(page, requests[0], health("Camera"));
  const dialog = page.getByRole("dialog");
  await dialog.getByRole("button", { name: "Interfaces" }).click();
  await expect.poll(() => requests.length).toBe(2);
  await respond(page, requests[1], [{ name: "applications", supported: true }]);
  await dialog.getByRole("button", { name: "applications" }).click();
  await expect.poll(() => requests.length).toBe(3);
  await respond(
    page,
    requests[2],
    ["Valid", "Invalid", "Missing", "None", "Custom", "Unknown"].map(
      (status) => ({
        name: status,
        nice_name: status,
        status: "Stopped",
        version: "1",
        license_status: status,
      }),
    ),
  );
  await expect(
    dialog.getByRole("button", { name: "Remove license" }),
  ).toHaveCount(0);
  await dialog.getByRole("button", { name: "Manage licenses" }).click();
  const license = page.getByRole("dialog", { name: "Manage licenses" });
  const selector = license.getByLabel("Application");
  await expect(
    license.getByRole("button", { name: "Remove license" }),
  ).toHaveCount(0);
  for (const status of [
    "Valid",
    "Invalid",
    "Missing",
    "None",
    "Custom",
    "Unknown",
  ]) {
    await selector.selectOption(status);
    await expect(license.getByText(`License status: ${status}`)).toBeVisible();
    const remove = license.getByRole("button", { name: "Remove license" });
    if (status === "Valid" || status === "Invalid") {
      await expect(remove).toBeVisible();
    } else {
      await expect(remove).toHaveCount(0);
    }
  }
  await selector.selectOption("Valid");
  await license.getByRole("button", { name: "Remove license" }).click();
  await expect(
    license.getByText("Remove the license for Valid?"),
  ).toBeVisible();
  await selector.selectOption("Invalid");
  await expect(
    license.getByRole("button", { name: "Confirm license removal" }),
  ).toHaveCount(0);
  await license.getByRole("button", { name: "Remove license" }).click();
  await license.getByRole("button", { name: "Cancel removal" }).click();
  expect(requests).toHaveLength(3);
});

test("application policy applies immediately while restart and license changes require confirmation", async ({
  page,
}) => {
  const { requests } = await openApp(page, [
    { ...devices[0], host: "192.0.2.1", port: 80, web_proto: "http" },
  ]);
  await select(page, "A", requests, 1);
  const dialog = page.getByRole("dialog");
  await dialog.getByRole("button", { name: "Interfaces" }).click();
  await expect.poll(() => requests.length).toBe(2);
  await respond(page, requests[1], [{ name: "applications", supported: true }]);
  await dialog.getByRole("button", { name: "applications" }).click();
  await expect.poll(() => requests.length).toBe(3);
  const app = {
    name: "example",
    nice_name: "Example",
    version: "1",
    status: "Running",
    vendor: "Vendor",
    license_status: "Valid",
    bundled: "Yes",
    signature_status: "Signed",
    resources: [{ name: "camera", used: "yes" }],
    compatible_os_versions: [{ Min: "11", Max: "12" }],
  };
  await respond(page, requests[2], [app]);
  await expect(dialog.getByText("Signed", { exact: true })).toBeVisible();
  await expect(dialog.getByText("camera: yes")).toBeVisible();
  await expect(dialog.getByText("11 – 12")).toBeVisible();
  await dialog.getByRole("button", { name: "Restart", exact: true }).click();
  await expect(dialog.getByText("Restart Example?")).toBeVisible();
  await dialog.getByRole("button", { name: "Confirm restart" }).click();
  await expect.poll(() => requests.length).toBe(4);
  expect(requests[3]).toMatchObject({
    type: "device/application-action",
    action: "restart",
    confirmed: true,
  });
  await respond(page, requests[3], null);
  await expect.poll(() => requests.length).toBe(5);
  await respond(page, requests[4], [app]);

  const policy = dialog.getByRole("switch", {
    name: /Allow unsigned applications/,
  });
  await expect(policy).not.toBeChecked();
  await policy.click();
  await expect(policy).not.toBeChecked();
  await expect(policy).toBeDisabled();
  await expect(dialog.getByText(/weakens application security/)).toHaveCount(0);
  await expect.poll(() => requests.length).toBe(6);
  await expect(
    dialog.getByRole("button", { name: "Confirm policy change" }),
  ).toHaveCount(0);
  expect(requests[5]).toMatchObject({
    type: "device/application-policy-set",
    previous: false,
    value: true,
    confirmed: true,
  });
  await respond(page, requests[5], null);
  await expect(policy).toBeChecked();
  await dialog.getByRole("button", { name: "Install application" }).click();
  const install = page.getByRole("dialog", { name: "Install application" });
  await expect(install.getByText("Supported SDKs: acap4-native")).toBeVisible();
  await expect(
    install.getByText("Unsigned applications: Allowed"),
  ).toBeVisible();
  await install.getByRole("button", { name: "Close" }).click();

  const uploads = [];
  await page.route("**/api/application-license", async (route) => {
    uploads.push(route.request());
    await route.fulfill({ json: { result: null } });
  });
  await dialog.getByRole("button", { name: "Manage licenses" }).click();
  const license = page.getByRole("dialog", { name: "Manage licenses" });
  await license.getByLabel("Application").selectOption("example");
  await license.locator("input[type=file]").setInputFiles({
    name: "key.xml",
    mimeType: "text/xml",
    buffer: Buffer.from("<license/>"),
  });
  expect(uploads).toHaveLength(0);
  await license.getByRole("button", { name: "Confirm license upload" }).click();
  await expect.poll(() => uploads.length).toBe(1);
  expect(uploads[0].headers()["x-axis-package"]).toBe("example");
  expect(uploads[0].headers()["x-axis-confirmed"]).toBe("true");
  expect(uploads[0].postData()).toBe("<license/>");
  await expect.poll(() => requests.length).toBe(7);
  await respond(page, requests[6], [app]);
  await dialog.getByRole("button", { name: "Manage licenses" }).click();
  await license.getByLabel("Application").selectOption("example");
  await license.getByRole("button", { name: "Remove license" }).click();
  await expect(
    license.getByText("Remove the license for Example?"),
  ).toBeVisible();
  await license.getByRole("button", { name: "Cancel removal" }).click();
  expect(requests).toHaveLength(7);
  await license.getByRole("button", { name: "Remove license" }).click();
  await license
    .getByRole("button", { name: "Confirm license removal" })
    .click();
  await expect.poll(() => requests.length).toBe(8);
  await expect(
    license.getByRole("button", { name: "Confirm license removal" }),
  ).toBeDisabled();
  await page.keyboard.press("Escape");
  await expect(license).toBeVisible();
  expect(requests[7]).toMatchObject({
    type: "device/application-license-remove",
    license_status: "Valid",
    confirmed: true,
  });
  await respond(page, requests[7], null);
  await expect.poll(() => requests.length).toBe(9);
  await respond(page, requests[8], [{ ...app, license_status: "Missing" }]);
  await expect(license).toBeHidden();
  await dialog.getByRole("button", { name: "Manage licenses" }).click();
  await license.getByLabel("Application").selectOption("example");
  await expect(
    license.getByRole("button", { name: "Remove license" }),
  ).toHaveCount(0);
});

test("license removal failure remains visible without retry", async ({
  page,
}) => {
  const { requests } = await openApp(page);
  await select(page, "A", requests, 1);
  await respond(page, requests[0], health("Camera"));
  const dialog = page.getByRole("dialog");
  await dialog.getByRole("button", { name: "Interfaces" }).click();
  await expect.poll(() => requests.length).toBe(2);
  await respond(page, requests[1], [{ name: "applications", supported: true }]);
  await dialog.getByRole("button", { name: "applications" }).click();
  await expect.poll(() => requests.length).toBe(3);
  await respond(page, requests[2], [
    {
      name: "example",
      nice_name: "Example",
      version: "1",
      status: "Stopped",
      license_status: "Valid",
    },
  ]);
  await dialog.getByRole("button", { name: "Manage licenses" }).click();
  const license = page.getByRole("dialog", { name: "Manage licenses" });
  await license.getByLabel("Application").selectOption("example");
  await license.getByRole("button", { name: "Remove license" }).click();
  await license
    .getByRole("button", { name: "Confirm license removal" })
    .click();
  await expect.poll(() => requests.length).toBe(4);
  await respond(page, requests[3], undefined, {
    message:
      "License change outcome is unknown. Check the application before trying again.",
  });
  await expect(license.getByRole("alert")).toContainText("outcome is unknown");
  await expect(
    license.getByRole("button", { name: "Remove license" }),
  ).toHaveCount(0);
  await expect(
    license.getByRole("button", { name: "Confirm license upload" }),
  ).toBeDisabled();
  expect(requests).toHaveLength(4);
});

test("license modal validates drops and blocks navigation during upload", async ({
  page,
}) => {
  await page.setViewportSize({ width: 375, height: 667 });
  const { requests } = await openApp(page);
  await select(page, "A", requests, 1);
  await respond(page, requests[0], health("Camera"));
  const dialog = page.getByRole("dialog");
  await dialog.getByRole("button", { name: "Interfaces" }).click();
  await expect.poll(() => requests.length).toBe(2);
  await respond(page, requests[1], [{ name: "applications", supported: true }]);
  await dialog.getByRole("button", { name: "applications" }).click();
  await expect.poll(() => requests.length).toBe(3);
  const apps = ["first", "second"].map((name) => ({
    name,
    nice_name: name,
    version: "1",
    status: "Stopped",
    license_status: "Missing",
  }));
  await respond(page, requests[2], apps);
  const trigger = dialog.getByRole("button", { name: "Manage licenses" });
  await trigger.click();
  const license = page.getByRole("dialog", { name: "Manage licenses" });
  const box = await license.boundingBox();
  expect(box.x).toBeGreaterThanOrEqual(0);
  expect(box.x + box.width).toBeLessThanOrEqual(375);
  expect(
    await license
      .locator(".dialog-content")
      .evaluate((element) => element.scrollWidth <= element.clientWidth),
  ).toBe(true);
  const confirm = license.getByRole("button", {
    name: "Confirm license upload",
  });
  const dropzone = license.getByRole("region", {
    name: "License file drop area",
  });
  await expect(confirm).toBeDisabled();
  const drop = async (files) => {
    const dataTransfer = await page.evaluateHandle((entries) => {
      const transfer = new DataTransfer();
      for (const [name, content] of entries)
        transfer.items.add(new File([content], name));
      return transfer;
    }, files);
    await dropzone.dispatchEvent("dragover", { dataTransfer });
    await expect(dropzone).toHaveAttribute("data-dragging", "");
    await dropzone.dispatchEvent("drop", { dataTransfer });
    await expect(dropzone).not.toHaveAttribute("data-dragging", "");
    await dataTransfer.dispose();
  };
  await drop([
    ["a.xml", "a"],
    ["b.xml", "b"],
  ]);
  await expect(license.getByRole("alert")).toHaveText(
    "Choose one license file.",
  );
  await drop([["empty.xml", ""]]);
  await expect(license.getByRole("alert")).toContainText("non-empty");
  await drop([["large.xml", "x".repeat(1024 * 1024 + 1)]]);
  await expect(license.getByRole("alert")).toContainText("1 MiB");
  await drop([["key.xml", "<license/>"]]);
  await expect(license.getByText("Selected: key.xml")).toBeVisible();
  await expect(confirm).toBeDisabled();
  await license.getByLabel("Application").selectOption("second");
  await expect(confirm).toBeEnabled();
  await page.keyboard.press("Escape");
  await expect(license).toBeHidden();
  await expect(trigger).toBeFocused();
  await trigger.click();
  await expect(confirm).toBeDisabled();
  await license.getByLabel("Application").selectOption("second");
  await drop([["key.xml", "<license/>"]]);
  let release;
  const waiting = new Promise((resolve) => (release = resolve));
  const uploads = [];
  await page.route("**/api/application-license", async (route) => {
    uploads.push(route.request());
    await waiting;
    await route.fulfill({ json: { result: null } });
  });
  await confirm.click();
  await expect.poll(() => uploads.length).toBe(1);
  expect(uploads[0].headers()["x-axis-package"]).toBe("second");
  expect(uploads[0].postData()).toBe("<license/>");
  await expect(confirm).toBeDisabled();
  await expect(license.getByRole("button", { name: "Close" })).toBeDisabled();
  await page.keyboard.press("Escape");
  await expect(license).toBeVisible();
  expect(uploads).toHaveLength(1);
  release();
  await expect.poll(() => requests.length).toBe(4);
  await respond(page, requests[3], apps);
  await expect(license).toBeHidden();
  await expect(trigger).toBeFocused();
  await expect(dialog.getByText("License change accepted.")).toBeVisible();
});

test("unavailable unsigned policy disables the switch until refreshed", async ({
  page,
}) => {
  const { requests } = await openApp(
    page,
    [devices[0]],
    undefined,
    false,
    "armv7hf",
    true,
  );
  await select(page, "A", requests, 1);
  await respond(page, requests[0], health("Camera"));
  const dialog = page.getByRole("dialog");
  await dialog.getByRole("button", { name: "Interfaces" }).click();
  await expect.poll(() => requests.length).toBe(2);
  await respond(page, requests[1], [{ name: "applications", supported: true }]);
  await dialog.getByRole("button", { name: "applications" }).click();
  await expect.poll(() => requests.length).toBe(4);
  await respond(page, requests[2], undefined, {
    message: "Policy unsupported.",
  });
  await respond(page, requests[3], []);
  const policy = dialog.getByRole("switch", {
    name: /Allow unsigned applications/,
  });
  await expect(policy).toBeDisabled();
  await expect(
    dialog.getByText("Policy: Unavailable: Policy unsupported."),
  ).toBeVisible();
  await dialog
    .getByRole("button", { name: "Refresh application information" })
    .click();
  await expect.poll(() => requests.length).toBe(5);
  await respond(page, requests[4], true);
  await expect(policy).toBeChecked();
  await expect(policy).toBeEnabled();
  await policy.click();
  await expect(policy).toBeChecked();
  await expect(policy).toBeDisabled();
  await expect.poll(() => requests.length).toBe(6);
  expect(requests[5]).toMatchObject({
    type: "device/application-policy-set",
    previous: true,
    value: false,
    confirmed: true,
  });
  await respond(page, requests[5], null);
  await expect(policy).not.toBeChecked();
  await policy.click();
  await expect.poll(() => requests.length).toBe(7);
  await respond(page, requests[6], undefined, {
    message:
      "Policy change outcome is unknown. Check the policy before trying again.",
  });
  await expect(policy).toBeDisabled();
  await expect(
    dialog.getByText(/Policy change outcome is unknown/),
  ).toBeVisible();
  await dialog
    .getByRole("button", { name: "Refresh application information" })
    .click();
  await expect.poll(() => requests.length).toBe(8);
  await respond(page, requests[7], true);
  await expect(policy).toBeChecked();
  await expect(policy).toBeEnabled();
});

test("license upload errors remain in the modal without retrying", async ({
  page,
}) => {
  const { requests } = await openApp(page);
  await select(page, "A", requests, 1);
  await respond(page, requests[0], health("Camera"));
  const dialog = page.getByRole("dialog");
  await dialog.getByRole("button", { name: "Interfaces" }).click();
  await expect.poll(() => requests.length).toBe(2);
  await respond(page, requests[1], [{ name: "applications", supported: true }]);
  await dialog.getByRole("button", { name: "applications" }).click();
  await expect.poll(() => requests.length).toBe(3);
  await respond(page, requests[2], [
    {
      name: "example",
      nice_name: "Example",
      version: "1",
      status: "Stopped",
      license_status: "Missing",
    },
  ]);
  let uploads = 0;
  await page.route("**/api/application-license", async (route) => {
    uploads++;
    await route.fulfill({
      status: 400,
      json: {
        error: {
          message:
            "License change outcome is unknown. Check the application before trying again.",
        },
      },
    });
  });
  await dialog.getByRole("button", { name: "Manage licenses" }).click();
  const license = page.getByRole("dialog", { name: "Manage licenses" });
  await license.getByLabel("Application").selectOption("example");
  await license.locator("input[type=file]").setInputFiles({
    name: "key.xml",
    mimeType: "text/xml",
    buffer: Buffer.from("key"),
  });
  await license.getByRole("button", { name: "Confirm license upload" }).click();
  await expect(license.getByRole("alert")).toContainText("outcome is unknown");
  await expect(
    license.getByRole("button", { name: "Confirm license upload" }),
  ).toBeDisabled();
  expect(uploads).toBe(1);
});

test("ignores an older unsigned-policy read after a toggle change", async ({
  page,
}) => {
  const { requests } = await openApp(
    page,
    [devices[0]],
    undefined,
    false,
    "armv7hf",
    true,
  );
  await select(page, "A", requests, 1);
  const dialog = page.getByRole("dialog");
  await dialog.getByRole("button", { name: "Interfaces" }).click();
  await expect.poll(() => requests.length).toBe(2);
  await respond(page, requests[1], [{ name: "applications", supported: true }]);
  await dialog.getByRole("button", { name: "applications" }).click();
  await expect.poll(() => requests.length).toBe(4);
  expect(requests[2].type).toBe("device/application-policy");
  await respond(page, requests[3], []);
  await dialog
    .getByRole("button", { name: "Refresh application information" })
    .click();
  await expect.poll(() => requests.length).toBe(5);
  await respond(page, requests[4], false);
  await dialog
    .getByRole("switch", { name: /Allow unsigned applications/ })
    .click();
  await expect.poll(() => requests.length).toBe(6);
  await respond(page, requests[5], null);
  await respond(page, requests[2], false);
  await expect(
    dialog.getByRole("switch", { name: /Allow unsigned applications/ }),
  ).toBeChecked();
});

test("configuration is available only for running applications", async ({
  page,
}) => {
  const { requests } = await openApp(page, [
    { ...devices[0], web_proto: "http", port: 80 },
    devices[1],
  ]);
  await select(page, "A", requests, 1);
  await respond(page, requests[0], health("Camera"));
  const dialog = page.getByRole("dialog");
  await dialog.getByRole("button", { name: "Interfaces" }).click();
  await expect.poll(() => requests.length).toBe(2);
  await respond(page, requests[1], [{ name: "applications", supported: true }]);
  await dialog.getByRole("button", { name: "applications" }).click();
  await expect.poll(() => requests.length).toBe(3);
  await respond(
    page,
    requests[2],
    ["Running", "Stopped", "Idle", "Unknown"].map((status) => ({
      name: status,
      nice_name: status,
      status,
      version: "1",
      vendor: "Axis",
      license_status: "None",
      configuration_page: "local/example/index.html",
    })),
  );
  await expect(
    dialog.getByRole("link", { name: "Open configuration" }),
  ).toHaveCount(1);
  const disabled = dialog.getByRole("button", { name: "Open configuration" });
  await expect(disabled).toHaveCount(3);
  for (const button of await disabled.all())
    await expect(button).toBeDisabled();
});

test("application installation is confirmed and blocks navigation while pending", async ({
  page,
}) => {
  const { requests } = await openApp(page);
  await select(page, "A", requests, 1);
  await respond(page, requests[0], health("Camera"));
  const dialog = page.getByRole("dialog");
  await dialog.getByRole("button", { name: "Interfaces" }).click();
  await expect.poll(() => requests.length).toBe(2);
  await respond(page, requests[1], [{ name: "applications", supported: true }]);
  await dialog.getByRole("button", { name: "applications" }).click();
  await expect.poll(() => requests.length).toBe(3);
  await respond(page, requests[2], []);
  await dialog.getByRole("button", { name: "Install application" }).click();
  const install = page.getByRole("dialog", { name: "Install application" });
  await expect(
    install.getByText("Hardware architecture: armv7hf"),
  ).toBeVisible();
  await expect(install.getByText(/upgraded or downgraded/)).toBeVisible();
  await expect(install.getByText(/both versions may be removed/)).toBeVisible();
  await expect(
    install.getByRole("button", { name: "Confirm installation" }),
  ).toBeDisabled();

  let release;
  const pending = new Promise((resolve) => (release = resolve));
  const uploads = [];
  await page.route("**/api/application-upload", async (route) => {
    uploads.push(route.request());
    await pending;
    await route.fulfill({ json: { result: null } });
  });
  const choose = async () => {
    const chooser = page.waitForEvent("filechooser");
    await install.getByRole("button", { name: "Choose file" }).click();
    await (
      await chooser
    ).setFiles({
      name: "example.eap",
      mimeType: "application/octet-stream",
      buffer: Buffer.from("package"),
    });
  };
  await choose();
  await expect(install.getByText("Selected: example.eap")).toBeVisible();
  await install.getByRole("button", { name: "Cancel" }).click();
  await expect(install).toBeHidden();
  await expect(
    dialog.getByRole("button", { name: "Install application" }),
  ).toBeFocused();
  expect(uploads).toHaveLength(0);
  await dialog.getByRole("button", { name: "Install application" }).click();
  await choose();
  await install.getByRole("button", { name: "Confirm installation" }).click();
  await expect.poll(() => uploads.length).toBe(1);
  expect(uploads[0].headers()["x-axis-confirmed"]).toBe("true");
  await expect(install.getByRole("button", { name: "Close" })).toBeDisabled();
  await expect(install.getByRole("button", { name: "Cancel" })).toBeDisabled();
  await expect(
    install.getByRole("button", { name: "Confirm installation" }),
  ).toBeDisabled();
  const unexpected = await page.evaluateHandle(() => {
    const transfer = new DataTransfer();
    transfer.items.add(new File(["other"], "other.eap"));
    return transfer;
  });
  await install
    .getByRole("region", { name: "Application package drop area" })
    .dispatchEvent("drop", { dataTransfer: unexpected });
  await unexpected.dispose();
  await expect(install.getByText("Selected: example.eap")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(install).toBeVisible();
  release();
  await expect.poll(() => requests.length).toBe(4);
  await respond(page, requests[3], []);
  await expect(install).toBeHidden();
  await expect(dialog.getByText("Application installed.")).toBeVisible();
  await expect(
    dialog.getByRole("button", { name: "Install application" }),
  ).toBeFocused();
  expect(uploads).toHaveLength(1);
});

test("architecture lookup failure is visible without blocking application installation", async ({
  page,
}) => {
  const { requests } = await openApp(page, devices, undefined, false, null);
  await select(page, "A", requests, 1);
  await respond(page, requests[0], health("Camera"));
  const dialog = page.getByRole("dialog");
  await dialog.getByRole("button", { name: "Interfaces" }).click();
  await expect.poll(() => requests.length).toBe(2);
  await respond(page, requests[1], [{ name: "applications", supported: true }]);
  await dialog.getByRole("button", { name: "applications" }).click();
  await expect.poll(() => requests.length).toBe(3);
  await respond(page, requests[2], []);
  await dialog.getByRole("button", { name: "Install application" }).click();
  const install = page.getByRole("dialog", { name: "Install application" });
  await expect(
    install.getByText(
      "Hardware architecture: Unavailable: Architecture unavailable.",
    ),
  ).toBeVisible();
  await expect(
    install.getByRole("button", { name: "Choose file" }),
  ).toBeEnabled();
});

test("drag and drop validates packages before confirmed installation", async ({
  page,
}) => {
  const { requests } = await openApp(page);
  await select(page, "A", requests, 1);
  await respond(page, requests[0], health("Camera"));
  const dialog = page.getByRole("dialog", { name: "Applications" });
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "Interfaces" })
    .click();
  await expect.poll(() => requests.length).toBe(2);
  await respond(page, requests[1], [{ name: "applications", supported: true }]);
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "applications" })
    .click();
  await expect.poll(() => requests.length).toBe(3);
  await respond(page, requests[2], []);
  await dialog.getByRole("button", { name: "Install application" }).click();
  const install = page.getByRole("dialog", { name: "Install application" });
  const dropzone = install.getByRole("region", {
    name: "Application package drop area",
  });
  expect(
    await page.evaluate(() => {
      const event = new DragEvent("drop", { bubbles: true, cancelable: true });
      return !document.body.dispatchEvent(event);
    }),
  ).toBe(true);
  const drop = async (files) => {
    const dataTransfer = await page.evaluateHandle((entries) => {
      const transfer = new DataTransfer();
      for (const [name, content] of entries)
        transfer.items.add(new File([content], name));
      return transfer;
    }, files);
    await dropzone.dispatchEvent("dragover", { dataTransfer });
    await expect(dropzone).toHaveAttribute("data-dragging", "");
    await dropzone.dispatchEvent("drop", { dataTransfer });
    await expect(dropzone).not.toHaveAttribute("data-dragging", "");
    await dataTransfer.dispose();
  };
  await drop([["example.eap", "package"]]);
  await expect(install.getByText("Selected: example.eap")).toBeVisible();
  await expect(
    install.getByRole("button", { name: "Confirm installation" }),
  ).toBeEnabled();
  await drop([["wrong.txt", "package"]]);
  await expect(install.getByRole("alert")).toContainText("non-empty .eap");
  await expect(
    install.getByRole("button", { name: "Confirm installation" }),
  ).toBeDisabled();
  await drop([
    ["one.eap", "one"],
    ["two.eap", "two"],
  ]);
  await expect(install.getByRole("alert")).toHaveText(
    "Choose one application package.",
  );
  await drop([["empty.eap", ""]]);
  await expect(install.getByRole("alert")).toContainText("non-empty .eap");
  await drop([["example.eap", "package"]]);

  const uploads = [];
  await page.route("**/api/application-upload", async (route) => {
    uploads.push(route.request());
    await route.fulfill({ json: { result: null } });
  });
  await page.keyboard.press("Escape");
  await expect(install).toBeHidden();
  expect(uploads).toHaveLength(0);
  await dialog.getByRole("button", { name: "Install application" }).click();
  await expect(
    install.getByRole("button", { name: "Confirm installation" }),
  ).toBeDisabled();
  await drop([["example.eap", "package"]]);
  await install.getByRole("button", { name: "Confirm installation" }).click();
  await expect.poll(() => uploads.length).toBe(1);
  expect(uploads[0].postData()).toBe("package");
  await expect.poll(() => requests.length).toBe(4);
  await respond(page, requests[3], []);
  await expect(dialog.getByText("Application installed.")).toBeVisible();
});

test("installation dialog fits a narrow screen", async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 667 });
  const { requests } = await openApp(page);
  await select(page, "A", requests, 1);
  await respond(page, requests[0], health("Camera"));
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "Interfaces" })
    .click();
  await expect.poll(() => requests.length).toBe(2);
  await respond(page, requests[1], [{ name: "applications", supported: true }]);
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "applications" })
    .click();
  await expect.poll(() => requests.length).toBe(3);
  await respond(page, requests[2], []);
  await page.getByRole("button", { name: "Install application" }).click();
  const install = page.getByRole("dialog", { name: "Install application" });
  const box = await install.boundingBox();
  expect(box.x).toBeGreaterThanOrEqual(0);
  expect(box.x + box.width).toBeLessThanOrEqual(375);
  expect(
    await install
      .locator(".dialog-content")
      .evaluate((element) => element.scrollWidth <= element.clientWidth),
  ).toBe(true);
  await expect(
    install.getByRole("button", { name: "Choose file" }),
  ).toBeVisible();
});

test("installation errors remain visible in the modal and do not retry", async ({
  page,
}) => {
  const { requests } = await openApp(page);
  await select(page, "A", requests, 1);
  await respond(page, requests[0], health("Camera"));
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "Interfaces" })
    .click();
  await expect.poll(() => requests.length).toBe(2);
  await respond(page, requests[1], [{ name: "applications", supported: true }]);
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "applications" })
    .click();
  await expect.poll(() => requests.length).toBe(3);
  await respond(page, requests[2], []);
  await page.getByRole("button", { name: "Install application" }).click();
  const install = page.getByRole("dialog", { name: "Install application" });
  let uploads = 0;
  await page.route("**/api/application-upload", async (route) => {
    uploads++;
    await route.fulfill({
      status: 400,
      json: {
        error: {
          message:
            "Installation outcome is unknown. Check applications before trying again.",
        },
      },
    });
  });
  await install.locator('input[type="file"]').setInputFiles({
    name: "example.eap",
    mimeType: "application/octet-stream",
    buffer: Buffer.from("package"),
  });
  await install.getByRole("button", { name: "Confirm installation" }).click();
  await expect(install.getByRole("alert")).toContainText(
    "Installation outcome is unknown",
  );
  await expect(
    install.getByRole("button", { name: "Confirm installation" }),
  ).toBeDisabled();
  expect(uploads).toBe(1);
});

test("application action interruption warns before retry", async ({ page }) => {
  const { requests, sockets } = await openApp(page);
  await select(page, "A", requests, 1);
  await respond(page, requests[0], health("Camera"));
  const dialog = page.getByRole("dialog");
  await dialog.getByRole("button", { name: "Interfaces" }).click();
  await expect.poll(() => requests.length).toBe(2);
  await respond(page, requests[1], [{ name: "applications", supported: true }]);
  await dialog.getByRole("button", { name: "applications" }).click();
  await expect.poll(() => requests.length).toBe(3);
  await respond(page, requests[2], [
    {
      name: "example",
      nice_name: "Example",
      status: "Running",
      version: "1",
      vendor: "Axis",
      license_status: "None",
      configuration_page: null,
    },
  ]);
  await dialog.getByRole("button", { name: "Stop" }).click();
  await dialog.getByRole("button", { name: "Confirm stop" }).click();
  await expect.poll(() => requests.length).toBe(4);
  sockets[0].close({ code: 1001 });
  await expect(dialog.getByRole("alert")).toHaveText(
    "Application action outcome is unknown. Check the application before trying again.",
  );
  expect(
    requests.filter((item) => item.type === "device/application-action"),
  ).toHaveLength(1);
});

test("restart requires confirmation and prevents duplicate or conflicting actions", async ({
  page,
}) => {
  const { requests } = await openApp(page);
  await select(page, "A", requests, 1);
  await respond(page, requests[0], health("Camera"));
  const dialog = page.getByRole("dialog", { name: "Camera A" });
  const views = dialog.getByRole("navigation", { name: "Device views" });
  await views.getByRole("button", { name: "Interfaces" }).click();
  await expect.poll(() => requests.length).toBe(2);
  await respond(page, requests[1], [
    { name: "basic_device_info", supported: true },
  ]);
  await dialog.getByRole("button", { name: "Restart device" }).click();
  await expect(dialog.getByText("Restart Camera A (A)?")).toBeVisible();
  await dialog.getByRole("button", { name: "Cancel" }).click();
  expect(requests).toHaveLength(2);
  await dialog.getByRole("button", { name: "Restart device" }).click();
  await dialog.getByRole("button", { name: "Confirm restart" }).click();
  await expect.poll(() => requests.length).toBe(3);
  expect(requests[2]).toMatchObject({
    type: "device/restart",
    device: "A",
    confirmed: true,
  });
  await expect(
    dialog.getByRole("button", { name: "Confirm restart" }),
  ).toBeDisabled();
  await expect(dialog.getByRole("button", { name: "Close" })).toBeDisabled();
  await expect(views.getByRole("button", { name: "Health" })).toBeDisabled();
  await page.keyboard.press("Escape");
  await expect(dialog).toBeVisible();
  await respond(page, requests[2], null);
  await expect(dialog.getByRole("status")).toHaveText("Restart requested.");
  await views.getByRole("button", { name: "Health" }).click();
  await expect.poll(() => requests.length).toBe(4);
  expect(requests[3]).toMatchObject({ type: "device/health", device: "A" });
});

test("restart interruption warns against blind retry", async ({ page }) => {
  const { requests, sockets } = await openApp(page);
  await select(page, "A", requests, 1);
  await respond(page, requests[0], health("Camera"));
  const dialog = page.getByRole("dialog", { name: "Camera A" });
  await dialog.getByRole("button", { name: "Interfaces" }).click();
  await expect.poll(() => requests.length).toBe(2);
  await respond(page, requests[1], []);
  await dialog.getByRole("button", { name: "Restart device" }).click();
  await dialog.getByRole("button", { name: "Confirm restart" }).click();
  await expect.poll(() => requests.length).toBe(3);
  sockets[0].close({ code: 1001 });
  await expect(dialog.getByRole("alert")).toHaveText(
    "Restart outcome is unknown. Check the device before trying again.",
  );
  expect(
    requests.filter((request) => request.type === "device/restart"),
  ).toHaveLength(1);
});

test("keyboard selection and typed API commands work through the component boundaries", async ({
  page,
}) => {
  const { requests } = await openApp(page);
  const camera = page
    .getByRole("list", { name: "Devices", exact: true })
    .getByRole("button", { name: "Camera A", exact: false });
  await camera.focus();
  await camera.press("Enter");
  await expect.poll(() => requests.length).toBe(1);
  const dialog = page.getByRole("dialog", { name: "Camera A" });
  await expect(dialog).toBeVisible();
  const close = dialog.getByRole("button", { name: "Close" });
  const views = dialog.getByRole("navigation", { name: "Device views" });
  await expect(
    views.getByRole("button", { name: "Health", pressed: true }),
  ).toBeVisible();
  await expect(views.locator("axis-button.active")).toHaveCount(1);
  await expect(close).toBeFocused();
  await camera.evaluate((button) => button.focus());
  await expect(close).toBeFocused();
  await expect(
    dialog.getByRole("button", { name: "Refresh health" }),
  ).toHaveCount(0);
  await respond(page, requests[0], health("Camera"));

  await views.getByRole("button", { name: "APIs", exact: true }).click();
  await expect(views.locator("axis-button.active")).toHaveText("APIs");
  await expect.poll(() => requests.length).toBe(2);
  expect(requests[1]).toMatchObject({ type: "device/apis", device: "A" });
  await expect(
    dialog.getByRole("heading", { name: "Device health" }),
  ).toHaveCount(0);
  await respond(page, requests[1], [
    { id: "basic-device-info", version: "1.0" },
  ]);
  await expect(page.locator("pre")).toContainText("basic-device-info");

  await views.getByRole("button", { name: "Interfaces", exact: true }).click();
  await expect.poll(() => requests.length).toBe(3);
  expect(requests[2]).toMatchObject({ type: "device/interfaces", device: "A" });
  await respond(page, requests[2], [
    { name: "basic_device_info", supported: true },
    { name: "unavailable", supported: false },
  ]);
  await expect(
    page.getByRole("button", { name: "unavailable" }),
  ).toBeDisabled();
  await expect(views.getByRole("button")).toHaveCount(3);
  await expect(dialog.locator("pre")).not.toContainText(
    '"id": "basic-device-info"',
  );
  await page.getByRole("button", { name: "basic_device_info" }).click();
  await expect.poll(() => requests.length).toBe(4);
  expect(requests[3]).toMatchObject({
    type: "device/read",
    device: "A",
    name: "basic_device_info",
  });
  await respond(page, requests[3], { model: "AXIS test camera" });
  await expect(page.locator("pre")).toContainText("AXIS test camera");
  await page.keyboard.press("Escape");
  await expect(dialog).not.toBeVisible();
  await expect(camera).toBeFocused();
});

test("switches modal views while a request is pending without showing stale results", async ({
  page,
}) => {
  const { requests } = await openApp(page);
  await select(page, "A", requests, 1);
  const dialog = page.getByRole("dialog", { name: "Camera A" });
  const views = dialog.getByRole("navigation", { name: "Device views" });
  await views.getByRole("button", { name: "APIs", exact: true }).click();
  await expect.poll(() => requests.length).toBe(2);
  await respond(page, requests[1], [{ id: "current-api" }]);
  await respond(page, requests[0], health("Obsolete health"));
  await expect(dialog.locator("pre")).toContainText("current-api");
  await expect(dialog.getByText("Obsolete health")).toHaveCount(0);
  await views.getByRole("button", { name: "Health", exact: true }).click();
  await expect.poll(() => requests.length).toBe(3);
  await respond(page, requests[2], health("Current health"));
  await expect(dialog.getByText("Current health")).toBeVisible();
  await expect(dialog.locator("pre")).toHaveCount(0);
  const healthButton = views.getByRole("button", {
    name: "Health",
    exact: true,
    pressed: true,
  });
  const currentHealth = dialog.getByText("Current health");
  const before = await currentHealth.boundingBox();
  await healthButton.click();
  await expect.poll(() => requests.length).toBe(4);
  await expect(healthButton).toHaveAttribute("aria-busy", "true");
  const outline = views.locator(".busy-outline rect");
  await expect(outline).toBeInViewport();
  await expect(outline).toHaveCSS("animation-name", "busy-dashes");
  await expect(dialog.getByText(/Contacting the device/)).toHaveCount(0);
  await expect(currentHealth).toBeVisible();
  expect((await currentHealth.boundingBox()).y).toBeCloseTo(before.y);
  expect(requests[3]).toMatchObject({ type: "device/health", device: "A" });
  await respond(page, requests[3], health("Refreshed health"));
  await expect(dialog.getByText("Refreshed health")).toBeVisible();
  await expect(outline).toHaveCount(0);
});

test("reuses loaded views and interface results until the active button is clicked again", async ({
  page,
}) => {
  const { requests } = await openApp(page);
  await select(page, "A", requests, 1);
  await respond(page, requests[0], health("Cached health"));
  const dialog = page.getByRole("dialog", { name: "Camera A" });
  const views = dialog.getByRole("navigation", { name: "Device views" });
  const healthView = views.getByRole("button", { name: "Health", exact: true });
  const apis = views.getByRole("button", { name: "APIs", exact: true });
  const interfaces = views.getByRole("button", {
    name: "Interfaces",
    exact: true,
  });
  await apis.click();
  await expect.poll(() => requests.length).toBe(2);
  await respond(page, requests[1], [{ id: "cached-api" }]);
  await interfaces.click();
  await expect.poll(() => requests.length).toBe(3);
  await respond(page, requests[2], [
    { name: "basic_device_info", supported: true },
    { name: "light_control", supported: true },
  ]);
  const info = dialog.getByRole("button", {
    name: "basic_device_info",
    exact: true,
  });
  const light = dialog.getByRole("button", {
    name: "light_control",
    exact: true,
  });
  const result = dialog.locator("pre");
  await info.click();
  await expect.poll(() => requests.length).toBe(4);
  await respond(page, requests[3], { model: "Cached model" });
  await light.click();
  await expect.poll(() => requests.length).toBe(5);
  await respond(page, requests[4], null);
  await expect(result).toHaveText("null");

  await healthView.click();
  await expect(dialog.getByText("Cached health")).toBeVisible();
  await apis.click();
  await expect(result).toContainText("cached-api");
  await interfaces.click();
  await expect(light).toHaveAttribute("aria-pressed", "true");
  await expect(result).toHaveText("null");
  await info.click();
  await expect(result).toContainText("Cached model");
  expect(requests).toHaveLength(5);

  await info.click();
  await expect.poll(() => requests.length).toBe(6);
  await expect(info).toHaveAttribute("aria-busy", "true");
  await expect(interfaces).not.toHaveAttribute("aria-busy", "true");
  await expect(result).toContainText("Cached model");
  expect(requests[5]).toMatchObject({
    type: "device/read",
    name: "basic_device_info",
  });
  await respond(page, requests[5], { model: "Refreshed model" });
  await expect(result).toContainText("Refreshed model");
  await interfaces.click();
  await expect.poll(() => requests.length).toBe(7);
  await expect(interfaces).toHaveAttribute("aria-busy", "true");
  await expect(result).toContainText("Refreshed model");
  expect(requests[6]).toMatchObject({ type: "device/interfaces" });
  await respond(page, requests[6], []);
  await expect(result).toHaveText("[]");
  await expect(info).toHaveCount(0);
  await apis.click();
  await expect(result).toContainText("cached-api");
  await interfaces.click();
  await expect(result).toHaveText("[]");
  expect(requests).toHaveLength(7);
});

test("edits a saved device in Settings without reloading health for an alias change", async ({
  page,
}) => {
  const { requests } = await openApp(page);
  await select(page, "A", requests, 1);
  await respond(page, requests[0], health("Live camera"));
  const dialog = page.getByRole("dialog");
  const settings = dialog.getByRole("button", {
    name: "Settings",
    exact: true,
  });
  const device = {
    ...devices[0],
    web_proto: "https",
    port: 0,
    verify_ssl: true,
  };
  await settings.click();
  await expect.poll(() => requests.length).toBe(2);
  expect(requests[1]).toMatchObject({ type: "device/settings", device: "A" });
  await respond(page, requests[1], { device, username: "operator" });
  const name = dialog.getByRole("textbox", { name: "Alias" });
  await expect(name).toBeFocused();
  await expect(dialog.getByLabel("New password")).toHaveValue("");
  await expect(dialog.getByLabel("Username")).toHaveValue("operator");
  const port = dialog.getByLabel("Port");
  const protocol = dialog.getByLabel("Protocol");
  await expect(port).toHaveValue("443");
  await dialog.getByRole("button", { name: "Test connection" }).click();
  await expect.poll(() => requests.length).toBe(3);
  expect(requests[2]).toMatchObject({
    type: "device/test-connection",
    device: "A",
    password: "",
    port: 0,
  });
  await respond(page, requests.pop(), undefined, {
    code: "connection",
    message: "Could not connect.",
  });
  await expect(dialog.getByRole("alert")).toHaveText("Could not connect.");
  await protocol.selectOption("http");
  await expect(dialog.getByRole("alert")).toBeEmpty();
  await expect(port).toHaveValue("80");
  await protocol.selectOption("https");
  await expect(port).toHaveValue("443");
  await name.fill("");
  await expect(name).toHaveAttribute("placeholder", "A");
  await name.fill("Lobby");
  await name.press("Enter");
  await expect.poll(() => requests.length).toBe(3);
  expect(requests[2]).toMatchObject({
    type: "device/configure",
    device: "A",
    alias: "Lobby",
    username: "operator",
    password: "",
    port: 0,
    web_proto: "https",
    verify_ssl: true,
  });
  await respond(page, requests[2], undefined, {
    code: "storage",
    message: "That name is already in use.",
  });
  await expect(dialog.getByRole("alert")).toHaveText(
    "That name is already in use.",
  );
  await expect(name).toHaveValue("Lobby");
  await name.fill("Front entrance");
  await dialog.getByRole("button", { name: "Save settings" }).click();
  await expect.poll(() => requests.length).toBe(4);
  await respond(page, requests[3], {
    device: { ...device, alias: "Front entrance" },
    connection_changed: false,
  });
  const title = dialog.getByRole("heading", {
    name: "Front entrance",
    exact: true,
  });
  await expect(title).toBeVisible();
  await expect(settings).toBeFocused();
  await expect(dialog.getByText("Live camera")).toBeVisible();
  await settings.click();
  await expect.poll(() => requests.length).toBe(5);
  await page.keyboard.press("Escape");
  await expect(settings).toBeFocused();
  await dialog.getByRole("button", { name: "Close", exact: true }).click();
  await expect(
    page.getByRole("button", { name: /Front entrance camera-a/ }),
  ).toBeVisible();
  expect(requests).toHaveLength(5);
});

test("refreshes the saved device view after validated connection settings change", async ({
  page,
}) => {
  const { requests } = await openApp(page);
  await select(page, "A", requests, 1);
  await respond(page, requests[0], health("Old connection"));
  const dialog = page.getByRole("dialog");
  await dialog.getByRole("button", { name: "Settings", exact: true }).click();
  await expect.poll(() => requests.length).toBe(2);
  const device = {
    ...devices[0],
    web_proto: "https",
    port: 0,
    verify_ssl: true,
  };
  await respond(page, requests[1], { device, username: "operator" });
  await dialog.getByLabel("Address").fill("camera-new");
  await dialog.getByLabel("New password").fill("test-new-password");
  await dialog.getByLabel("Port").fill("8443");
  const save = dialog.getByRole("button", { name: "Save settings" });
  const testConnection = dialog
    .locator("axis-button")
    .filter({ hasText: "Test connection" });
  await expect(save).toBeDisabled();
  await testConnection.click();
  await expect.poll(() => requests.length).toBe(3);
  await respond(page, requests.pop(), undefined, {
    code: "connection",
    message: "Could not connect.",
  });
  await expect(testConnection).toHaveAttribute("variant", "danger");
  await expect(testConnection.getByRole("button")).toHaveCSS(
    "border-top-color",
    "rgb(160, 0, 0)",
  );
  await expect(testConnection).toHaveText("Test connection");
  await expect(save).toBeDisabled();
  await testConnection.click();
  await expect.poll(() => requests.length).toBe(3);
  await respond(page, requests.pop(), "A");
  await expect(testConnection).toHaveAttribute("variant", "success");
  await expect(save).toBeEnabled();
  await dialog.getByLabel("Port").fill("9443");
  await expect(testConnection).toHaveAttribute("variant", "neutral");
  await expect(save).toBeDisabled();
  await testConnection.click();
  await expect.poll(() => requests.length).toBe(3);
  await respond(page, requests.pop(), "A");
  await expect(testConnection).toHaveAttribute("variant", "success");
  await dialog.getByLabel("Alias").fill("New name");
  await expect(testConnection).toHaveAttribute("variant", "success");
  await save.click();
  await expect.poll(() => requests.length).toBe(3);
  await page.mouse.click(2, 2);
  await expect(dialog).toBeVisible();
  expect(requests[2]).toMatchObject({
    type: "device/configure",
    host: "camera-new",
    port: 9443,
    password: "test-new-password",
  });
  await respond(page, requests[2], {
    device: { ...device, host: "camera-new", port: 9443 },
    connection_changed: true,
  });
  await expect.poll(() => requests.length).toBe(4);
  expect(requests[3]).toMatchObject({ type: "device/health", device: "A" });
  await expect(dialog.getByText("Old connection")).toHaveCount(0);
  await respond(page, requests[3], health("New connection"));
  await expect(dialog.getByText("New connection")).toBeVisible();
});

test("keeps device details scrollable without extending the list page", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 480 });
  const { requests } = await openApp(page);
  const pageHeight = () =>
    page.evaluate(() => document.documentElement.scrollHeight);
  const closedHeight = await pageHeight();

  await select(page, "A", requests, 1);
  const dialog = page.getByRole("dialog", { name: "Camera A" });
  const devicesBox = page.locator("axis-device-list");
  const expectAligned = async () => {
    const dialogTop = await dialog.evaluate(
      (element) => element.getBoundingClientRect().top,
    );
    const devicesTop = await devicesBox.evaluate(
      (element) => element.getBoundingClientRect().top + window.scrollY,
    );
    expect(dialogTop).toBeCloseTo(devicesTop);
  };
  await expectAligned();
  await respond(page, requests[0], health("Camera"));
  await expect(dialog.getByText("Camera", { exact: true })).toBeVisible();
  await expectAligned();
  const bounds = await dialog.boundingBox();
  expect(bounds.width).toBeGreaterThan(350);
  expect(bounds.height).toBeLessThan(480);
  expect(await pageHeight()).toBe(closedHeight);
  const content = dialog.locator(".dialog-content");
  await expect
    .poll(() =>
      content.evaluate(
        (element) => element.scrollHeight - element.clientHeight,
      ),
    )
    .toBeGreaterThan(0);
  await content.evaluate((element) => {
    element.scrollTop = element.scrollHeight;
  });
  await expect(dialog.getByRole("button", { name: "Close" })).toBeInViewport();
  await page.setViewportSize({ width: 900, height: 720 });
  await expectAligned();
});

for (const serial of ["A", "B"]) {
  test(`health component preserves identity reporting for serial ${serial}`, async ({
    page,
  }) => {
    const { requests } = await openApp(page);
    await select(page, "A", requests, 1);
    await respond(page, requests[0], { ...health("Camera"), serial });
    if (serial === "A") {
      await expect(page.getByText("Serial", { exact: true })).toBeVisible();
      await expect(page.getByText("Saved serial", { exact: true })).toHaveCount(
        0,
      );
      await expect(page.getByText("Warning:", { exact: false })).toHaveCount(0);
    } else {
      await expect(
        page.getByText("Saved serial", { exact: true }),
      ).toBeVisible();
      await expect(
        page.getByText("Reported serial", { exact: true }),
      ).toBeVisible();
      await expect(page.getByText("Warning:", { exact: false })).toBeVisible();
    }
  });
}

test("system themes keep text readable and controls usable on a narrow screen", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.emulateMedia({ colorScheme: "light" });
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text());
  });
  await openApp(page, [
    { ...devices[0], alias: "Camera A with a long descriptive device name" },
  ]);
  const backgrounds = [];
  for (const colorScheme of ["light", "dark"]) {
    await page.emulateMedia({ colorScheme });
    const colors = await page.evaluate(() => {
      const style = getComputedStyle(document.documentElement);
      return { text: style.color, background: style.backgroundColor };
    });
    backgrounds.push(colors.background);
    const luminance = (color) => {
      const channels = color.match(/[\d.]+/g).map((value) => {
        const channel = Number(value) / 255;
        return channel <= 0.04045
          ? channel / 12.92
          : ((channel + 0.055) / 1.055) ** 2.4;
      });
      return channels[0] * 0.2126 + channels[1] * 0.7152 + channels[2] * 0.0722;
    };
    const text = luminance(colors.text);
    const background = luminance(colors.background);
    expect(
      (Math.max(text, background) + 0.05) / (Math.min(text, background) + 0.05),
    ).toBeGreaterThanOrEqual(4.5);
    const button = page.getByRole("button", { name: "Camera A", exact: false });
    const bounds = await button.boundingBox();
    expect(bounds.height).toBeGreaterThanOrEqual(44);
    expect(bounds.width).toBeGreaterThanOrEqual(44);
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth),
    ).toBeLessThanOrEqual(390);
  }
  expect(backgrounds[0]).not.toBe(backgrounds[1]);
  expect(errors).toEqual([]);
});
