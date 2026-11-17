type NamedDevice = {
  alias: string;
  discovery: { name: string } | null;
  model: string;
  serial: string;
};

export function deviceName(device: NamedDevice): string {
  return (
    device.alias.trim() ||
    device.discovery?.name.trim() ||
    device.model.trim() ||
    device.serial
  );
}
