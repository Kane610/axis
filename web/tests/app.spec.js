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

async function openApp(page, savedDevices = devices) {
  const requests = [];
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
    socket.onMessage((raw) => {
      const message = JSON.parse(raw);
      if ("token" in message) {
        tokens.push(message.token);
        socket.send(JSON.stringify({ type: "ready", version: 1 }));
      } else if (message.type === "devices/list") {
        socket.send(JSON.stringify({ id: message.id, result: savedDevices }));
      } else {
        requests.push({ ...message, socket });
      }
    });
  });
  await page.goto("http://axis.test/#first-token");
  await expect(
    page.getByRole("button", { name: "Camera A", exact: false }),
  ).toBeEnabled();
  return { requests, sockets, tokens };
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

test("scans only on request and shows distinct discovered tiles in the saved device list", async ({
  page,
}) => {
  const { requests } = await openApp(page, [
    { ...devices[0], serial: "00408C010204", model: "Saved camera" },
    { ...devices[1], alias: "Camera B M3115 Lobby", model: "AXIS M3115-LVE" },
  ]);
  const scan = page.getByRole("button", {
    name: /^Scan (local network|again)/,
  });
  expect(requests).toHaveLength(0);

  await scan.click();
  const scanning = page.getByRole("button", { name: "Scanning…" });
  await expect(scanning).toBeDisabled();
  await expect(scanning).toBeFocused();
  await page.keyboard.press("Enter");
  await expect
    .poll(() => requests.map(({ type }) => type))
    .toEqual(["devices/discover"]);
  await respond(page, requests[0], [
    {
      name: "<b>Entrance camera</b>",
      host: "192.0.2.2",
      macaddress: "00:40:8c:01:02:03",
      model: "Test camera",
    },
  ]);
  await expect(scan).toHaveAccessibleName("Scan again · 1 new");
  const list = page.getByRole("list", { name: "Devices", exact: true });
  const saved = list.getByRole("button", { name: /Camera A/ });
  const discovered = list
    .getByRole("listitem")
    .filter({ hasText: "<b>Entrance camera</b>" });
  await expect(discovered).toBeVisible();
  await expect(discovered).toContainText(
    "192.0.2.2) — 00:40:8c:01:02:03 — Test camera",
  );
  await expect(discovered).toContainText("Discovered");
  const discoveredButton = discovered.getByRole("button");
  await expect(discoveredButton).toBeEnabled();
  await expect(saved).toBeEnabled();
  await expect(saved).toHaveAccessibleName(
    "Camera A (camera-a) — 00:40:8c:01:02:04",
  );
  const secondSaved = list.getByRole("button", {
    name: "Camera B M3115 Lobby (camera-b)",
    exact: true,
  });
  await expect(secondSaved).toBeVisible();
  const savedBox = await saved.boundingBox();
  const secondSavedBox = await secondSaved.boundingBox();
  const discoveredBox = await discoveredButton.boundingBox();
  expect(secondSavedBox.y).toBeGreaterThanOrEqual(savedBox.y + savedBox.height);
  expect(discoveredBox.y).toBeGreaterThanOrEqual(
    secondSavedBox.y + secondSavedBox.height,
  );
  expect(discoveredBox.x).toBeCloseTo(savedBox.x);
  expect(discoveredBox.width).toBeCloseTo(savedBox.width);
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
  await page.getByRole("button", { name: "Scan local network" }).click();
  await expect.poll(() => requests.length).toBe(1);
  const found = {
    name: "Entrance camera",
    host: "192.0.2.2",
    macaddress: "00:40:8c:01:02:03",
  };
  await respond(page, requests[0], [found]);
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
    page.getByRole("button", { name: /^Entrance \(/ }),
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
    name: /^Scan (local network|again)/,
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
  await expect(scan).toHaveAccessibleName("Scan again · 1 new");
  await expect(list).toContainText("Different camera at a saved address");

  await scan.click();
  await expect.poll(() => requests.length).toBe(2);
  const previousResult = list.getByRole("button", {
    name: /Different camera at a saved address/,
  });
  await expect(previousResult).toBeVisible();
  await expect(previousResult).toBeDisabled();
  await expect(list.getByRole("button", { name: /Camera A/ })).toBeEnabled();
  await respond(page, requests[1], savedAnnouncements);
  await expect(scan).toHaveAccessibleName("Scan again · No new devices");
  await expect(page.locator(".scan-status")).toHaveText(
    "All discovered devices are already saved.",
  );
  await expect(list.getByRole("listitem")).toHaveCount(3);
});

test("reports a failed scan and can retry with no results", async ({
  page,
}) => {
  const { requests } = await openApp(page);
  const scan = page.getByRole("button", { name: "Scan local network" });
  await scan.click();
  await expect.poll(() => requests.length).toBe(1);
  await respond(page, requests[0], undefined, {
    code: "operation",
    message: "Device discovery failed.",
  });
  const retry = page.getByRole("button", { name: "Retry scan · Scan failed" });
  await expect(retry).toHaveAccessibleDescription("Device discovery failed.");
  await expect(page.getByText("Device discovery failed.")).not.toBeInViewport();
  await retry.click();
  await expect.poll(() => requests.length).toBe(2);
  await respond(page, requests[1], []);
  await expect(
    page.getByRole("button", { name: "Scan again · No new devices" }),
  ).toBeEnabled();
  await expect(page.getByRole("alert")).toHaveCount(0);
});

test("moves the scan outline unless reduced motion is enabled", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "no-preference" });
  const { requests } = await openApp(page);
  await page.getByRole("button", { name: "Scan local network" }).click();
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

test("ignores an outstanding read after dismissal and a list refresh", async ({
  page,
}) => {
  const savedDevices = [...devices];
  const { requests } = await openApp(page, savedDevices);
  await select(page, "A", requests, 1);
  await page.keyboard.press("Escape");
  savedDevices.length = 0;
  await page.getByRole("button", { name: "Refresh list" }).click();
  await expect(
    page.getByText("No saved devices.", { exact: false }),
  ).toBeVisible();
  await respond(page, requests[0], undefined, {
    code: "connection",
    message: "Obsolete error",
  });
  await expect(page.getByRole("alert")).toHaveCount(0);
  await expect(page.locator("axis-button[busy]")).toHaveCount(0);
});

for (const state of ["connected", "denied", "disconnected"]) {
  test(`uses a replacement link when ${state} without reloading`, async ({
    page,
  }) => {
    await page.clock.install();
    const { requests, sockets, tokens } = await openApp(page);
    await select(page, "A", requests, 1);
    if (state !== "connected") {
      sockets[0].close({ code: state === "denied" ? 1008 : 1001 });
      await expect(
        page
          .getByRole("dialog")
          .getByText(
            state === "denied" ? "Access denied" : "Disconnected; reconnecting",
            { exact: true },
          ),
      ).toBeVisible();
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
  await expect(close).toBeFocused();
  await camera.evaluate((button) => button.focus());
  await expect(close).toBeFocused();
  await expect(
    dialog.getByRole("button", { name: "Refresh health" }),
  ).toHaveCount(0);
  await respond(page, requests[0], health("Camera"));

  await views.getByRole("button", { name: "APIs", exact: true }).click();
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
    page.getByRole("button", { name: /Front entrance \(camera-a\)/ }),
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
