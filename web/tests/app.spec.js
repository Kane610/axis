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
          "default-src 'self'; connect-src 'self' ws://axis.test; style-src 'self' 'unsafe-inline'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'",
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
  await page
    .getByRole("button", { name: `Camera ${name}`, exact: false })
    .click();
  await expect.poll(() => requests.length).toBe(count);
}

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
      page.getByText("Contacting the device.", { exact: false }),
    ).toBeVisible();
    await expect(page.getByText("Obsolete", { exact: true })).toHaveCount(0);
    await expect(page.getByRole("alert")).toHaveCount(0);

    await respond(page, requests[2], health("Current"));
    await expect(page.getByText("Current", { exact: true })).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Refresh health" }),
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
    await page.getByRole("button", { name: "Check interfaces" }).click();
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
      page.getByText("Contacting the device.", { exact: false }),
    ).toBeVisible();
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

test("ignores an outstanding read when refreshing removes the selected device", async ({
  page,
}) => {
  const savedDevices = [...devices];
  const { requests } = await openApp(page, savedDevices);
  await select(page, "A", requests, 1);
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
  await expect(
    page.getByText("Contacting the device.", { exact: false }),
  ).toHaveCount(0);
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
        page.getByText(
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
  const camera = page.getByRole("button", { name: "Camera A", exact: false });
  await camera.focus();
  await camera.press("Enter");
  await expect.poll(() => requests.length).toBe(1);
  await expect(
    page.getByRole("button", { name: "Camera A", exact: false, pressed: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Refresh health" }),
  ).toBeDisabled();
  await respond(page, requests[0], health("Camera"));

  await page.getByRole("button", { name: "List APIs" }).click();
  await expect.poll(() => requests.length).toBe(2);
  expect(requests[1]).toMatchObject({ type: "device/apis", device: "A" });
  await respond(page, requests[1], [
    { id: "basic-device-info", version: "1.0" },
  ]);
  await expect(page.locator("pre")).toContainText("basic-device-info");

  await page.getByRole("button", { name: "Check interfaces" }).click();
  await expect.poll(() => requests.length).toBe(3);
  expect(requests[2]).toMatchObject({ type: "device/interfaces", device: "A" });
  await respond(page, requests[2], [
    { name: "basic_device_info", supported: true },
    { name: "unavailable", supported: false },
  ]);
  await expect(
    page.getByRole("button", { name: "unavailable" }),
  ).toBeDisabled();
  await page.getByRole("button", { name: "basic_device_info" }).click();
  await expect.poll(() => requests.length).toBe(4);
  expect(requests[3]).toMatchObject({
    type: "device/read",
    device: "A",
    name: "basic_device_info",
  });
  await respond(page, requests[3], { model: "AXIS test camera" });
  await expect(page.locator("pre")).toContainText("AXIS test camera");
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
