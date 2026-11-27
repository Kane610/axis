import { expect, test } from "vitest";
import { compareApplicationVersions } from "../src/application-versions";

test("sorts shuffled versions numerically, newest first", () => {
  expect(
    ["1.6.1", "2.0.1", "2.0.0", "1.6.0", "1.6.7", "1.10.0", "10.0.0"].sort(
      compareApplicationVersions,
    ),
  ).toEqual(["10.0.0", "2.0.1", "2.0.0", "1.10.0", "1.6.7", "1.6.1", "1.6.0"]);
});

test("orders prereleases semantically and ignores build metadata", () => {
  expect(
    [
      "2.0.0-rc.2",
      "2.0.0-alpha",
      "2.0.0",
      "2.0.0-rc.10",
      "2.0.0-1",
      "2.0.0-rc",
    ].sort(compareApplicationVersions),
  ).toEqual([
    "2.0.0",
    "2.0.0-rc.10",
    "2.0.0-rc.2",
    "2.0.0-rc",
    "2.0.0-alpha",
    "2.0.0-1",
  ]);
  expect(compareApplicationVersions("2.0.0+one", "2.0.0+two")).toBe(0);
});

test("keeps unrecognized versions last in their original order", () => {
  expect(
    ["beta", "2.0.0-01", "", "01.0.0", "1.0.0"].sort(
      compareApplicationVersions,
    ),
  ).toEqual(["1.0.0", "beta", "2.0.0-01", "", "01.0.0"]);
});
