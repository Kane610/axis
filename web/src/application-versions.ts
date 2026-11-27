const SEMVER =
  /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$/;

function versionParts(value: string) {
  const match = SEMVER.exec(value);
  if (!match || match[0] !== value) return null;
  const prerelease = match[4]?.split(".") ?? [];
  if (prerelease.some((part) => /^0\d+$/.test(part))) return null;
  return {
    numbers: match.slice(1, 4).map(BigInt),
    prerelease,
  };
}

export function isApplicationVersion(value: string): boolean {
  return versionParts(value) !== null;
}

export function compareApplicationVersions(
  left: string,
  right: string,
): number {
  const a = versionParts(left);
  const b = versionParts(right);
  if (!a || !b) return a ? -1 : b ? 1 : 0;
  for (let index = 0; index < 3; index++) {
    if (a.numbers[index] !== b.numbers[index])
      return a.numbers[index] > b.numbers[index] ? -1 : 1;
  }
  if (!a.prerelease.length || !b.prerelease.length)
    return a.prerelease.length ? 1 : b.prerelease.length ? -1 : 0;
  for (
    let index = 0;
    index < Math.min(a.prerelease.length, b.prerelease.length);
    index++
  ) {
    const x = a.prerelease[index];
    const y = b.prerelease[index];
    if (x === y) continue;
    const xNumeric = /^\d+$/.test(x);
    const yNumeric = /^\d+$/.test(y);
    if (xNumeric !== yNumeric) return xNumeric ? 1 : -1;
    if (xNumeric) return BigInt(x) > BigInt(y) ? -1 : 1;
    return x > y ? -1 : 1;
  }
  return b.prerelease.length - a.prerelease.length;
}
