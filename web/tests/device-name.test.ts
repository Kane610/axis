import { expect, test } from "vitest";

import { deviceName } from "../src/device-name";

const device = {
  alias: "",
  discovery: null,
  model: "AXIS M1234",
  serial: "SERIAL",
};

test("uses a saved alias before discovery or model", () => {
  expect(
    deviceName({
      ...device,
      alias: "Front door",
      discovery: { name: "Camera" },
    }),
  ).toBe("Front door");
});

test("uses the discovered name when there is no alias", () => {
  expect(deviceName({ ...device, discovery: { name: "Camera" } })).toBe(
    "Camera",
  );
});

test("uses the model when there is no saved name", () => {
  expect(deviceName({ ...device, alias: " ", discovery: { name: "" } })).toBe(
    "AXIS M1234",
  );
});

test("falls back to the serial when no name or model is available", () => {
  expect(deviceName({ ...device, model: "" })).toBe("SERIAL");
});
