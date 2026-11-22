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
export type ApplicationAction = "start" | "stop" | "restart" | "remove";
export type Application = {
  id: string;
  name: string;
  nice_name: string;
  status: string;
  version: string;
  vendor: string;
  application_id: string | null;
  configuration_page: string | null;
  license_status: string;
  license_name: string;
  license_expiration_date: string;
  bundled?: string | null;
  signature_status?: string | null;
  resources?: { name?: string; used?: string }[];
  compatible_os_versions?: { Min?: string; Max?: string }[];
};
export type ConfiguredDevice = { device: Device; connection_changed: boolean };

export type ServerSettings = {
  selected: string[] | null;
  acap_folder: string | null;
  interfaces: {
    name: string;
    label: string;
    addresses: string[];
    up: boolean | null;
  }[];
};

export type AcapPackage = {
  filename: string;
  digest: string;
  size: number;
  name: string;
  friendly_name: string;
  version: string;
  architecture: string;
  vendor: string;
  vendor_id: string;
  os_ranges: [string, string][];
  sdk: string;
  signature: "present_unverified" | "not_detected" | "unknown";
};

export type AcapCatalog = {
  folder: string | null;
  packages: AcapPackage[];
  errors: { filename: string; message: string }[];
  error: string;
};

export type AcapUpdate = {
  name: string;
  version: string;
  status: string;
  candidates: AcapCandidate[];
};

export type AcapCandidate = {
  package: AcapPackage;
  warnings: string[];
  downgrade: boolean;
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
  doc_link: string;
  id: string;
  name: string;
  status: string;
  version: string;
};

export type ApplicationSupport = {
  apis: DeviceApi[] | null;
  supported: boolean;
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

export const fetchArchitecture = (connection: AxisConnection, device: string) =>
  connection.callWS("device/architecture", { device });

export const fetchApis = (connection: AxisConnection, device: string) =>
  connection.callWS("device/apis", { device });

export const fetchInterfaces = (connection: AxisConnection, device: string) =>
  connection.callWS("device/interfaces", { device });

export const readInterface = (
  connection: AxisConnection,
  device: string,
  name: string,
) => connection.callWS("device/read", { device, name });

export const restartDevice = (connection: AxisConnection, device: string) =>
  connection.callWS("device/restart", { device, confirmed: true });

export const fetchApplications = (connection: AxisConnection, device: string) =>
  connection.callWS("device/applications", { device });

export const fetchApplicationSupport = (
  connection: AxisConnection,
  device: string,
) => connection.callWS("device/application-support", { device });

export const fetchAcapUpdates = (connection: AxisConnection, device: string) =>
  connection.callWS("device/acap-updates", { device });

export const fetchAcapInstallCandidates = (
  connection: AxisConnection,
  device: string,
) => connection.callWS("device/acap-install-candidates", { device });

export const installCatalogApplication = (
  connection: AxisConnection,
  device: string,
  candidate: AcapCandidate,
) => connection.installCatalogApplication(device, candidate);

export const updateApplication = (
  connection: AxisConnection,
  device: string,
  app: Application,
  candidate: AcapCandidate,
) => connection.updateApplication(device, app, candidate);

export const fetchApplicationSdks = (
  connection: AxisConnection,
  device: string,
) => connection.callWS("device/application-sdks", { device });

export const fetchApplicationPolicy = (
  connection: AxisConnection,
  device: string,
) => connection.callWS("device/application-policy", { device });

export const setApplicationPolicy = (
  connection: AxisConnection,
  device: string,
  previous: boolean,
  value: boolean,
) =>
  connection.callWS("device/application-policy-set", {
    device,
    previous,
    value,
    confirmed: true,
  });

export const removeApplicationLicense = (
  connection: AxisConnection,
  device: string,
  app: Application,
) =>
  connection.callWS("device/application-license-remove", {
    device,
    package: app.name,
    version: app.version,
    status: app.status,
    license_status: app.license_status,
    confirmed: true,
  });

export const uploadApplicationLicense = (
  connection: AxisConnection,
  device: string,
  app: Application,
  file: File,
) => connection.uploadLicense(device, app, file);

export const installApplication = (
  connection: AxisConnection,
  device: string,
  file: File,
) => connection.installApplication(device, file);

export const controlApplication = (
  connection: AxisConnection,
  device: string,
  app: Application,
  action: ApplicationAction,
) =>
  connection.callWS("device/application-action", {
    device,
    action,
    package: app.name,
    version: app.version,
    status: app.status,
    confirmed: true,
  });
