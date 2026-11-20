import type { AxisConnection } from "./connection";

export type Discovery = {
  firmware: string;
  host: string;
  last_seen: string;
  link_local_host: string;
  macaddress: string;
  model: string;
  module: string;
  name: string;
  vendor: string;
};

export type DiscoveredDevice = {
  firmware?: string;
  host: string;
  link_local_host?: string;
  macaddress: string;
  model?: string;
  module?: string;
  name: string;
  serial?: string;
  vendor?: string;
};

export type DeviceConnection = {
  host: string;
  username: string;
  password: string;
  port: number;
  web_proto: string;
  verify_ssl: boolean;
};

export type SaveDevice = DeviceConnection & { alias: string };

export type DeviceSettings = { device: Device; username: string };
export type ConfiguredDevice = { device: Device; connection_changed: boolean };

export type ServerSettings = {
  selected: string[] | null;
  interfaces: {
    name: string;
    label: string;
    addresses: string[];
    up: boolean | null;
  }[];
};

export type Device = {
  alias: string;
  discovery: Discovery | null;
  host: string;
  is_companion: boolean;
  model: string;
  port: number;
  serial: string;
  verify_ssl: boolean;
  web_proto: string;
};

export type Health = {
  firmware_version: string;
  model: string;
  observed_at: string;
  product: string;
  serial: string;
  target: Device;
};

export type DeviceApi = {
  id: string;
  name: string;
  status: string;
  version: string;
};

export type DeviceInterface = {
  api_id: string;
  api_version: string;
  initialized: boolean;
  items: number;
  listed: boolean;
  name: string;
  probe_attempted: boolean;
  probe_succeeded: boolean;
  supported: boolean;
};

export const fetchDevices = (connection: AxisConnection) =>
  connection.callWS("devices/list", {});

export const discoverDevices = (
  connection: AxisConnection,
  onDiscovered: (device: DiscoveredDevice) => void,
  onWarning: (message: string) => void,
) =>
  connection.callWS(
    "devices/discover",
    { stream: true },
    onDiscovered,
    onWarning,
  );

export const saveDevice = (connection: AxisConnection, settings: SaveDevice) =>
  connection.callWS("devices/save", settings);

export const fetchDeviceSettings = (
  connection: AxisConnection,
  device: string,
) => connection.callWS("device/settings", { device });

export const configureDevice = (
  connection: AxisConnection,
  device: string,
  settings: SaveDevice,
) => connection.callWS("device/configure", { device, ...settings });

export const fetchHealth = (connection: AxisConnection, device: string) =>
  connection.callWS("device/health", { device });

export const fetchApis = (connection: AxisConnection, device: string) =>
  connection.callWS("device/apis", { device });

export const fetchInterfaces = (connection: AxisConnection, device: string) =>
  connection.callWS("device/interfaces", { device });

export const readInterface = (
  connection: AxisConnection,
  device: string,
  name: string,
) => connection.callWS("device/read", { device, name });
