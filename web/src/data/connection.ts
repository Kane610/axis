import type {
  ConfiguredDevice,
  Application,
  ApplicationAction,
  AcapCandidate,
  AcapCatalog,
  AcapUpdate,
  Device,
  DeviceApi,
  DeviceConnection,
  DeviceInterface,
  DeviceSettings,
  DiscoveredDevice,
  Health,
  SaveDevice,
  ServerSettings,
} from "./devices";

type Commands = {
  "devices/list": { args: Record<string, never>; result: Device[] };
  "devices/discover": {
    args: { stream: true };
    result: DiscoveredDevice[];
  };
  "server/settings": { args: Record<string, never>; result: ServerSettings };
  "server/browse-folders": {
    args: { path: string | null };
    result: {
      path: string;
      parent: string | null;
      directories: { name: string; path: string }[];
    };
  };
  "server/configure": {
    args: { interfaces: string[] | null; acap_folder?: string | null };
    result: ServerSettings;
  };
  "acap/catalog": { args: Record<string, never>; result: AcapCatalog };
  "acap/scan": { args: Record<string, never>; result: AcapCatalog };
  "devices/save": { args: SaveDevice; result: string };
  "devices/test-connection": { args: DeviceConnection; result: string };
  "device/test-connection": {
    args: DeviceConnection & { device: string };
    result: string;
  };
  "device/settings": { args: { device: string }; result: DeviceSettings };
  "device/configure": {
    args: SaveDevice & { device: string };
    result: ConfiguredDevice;
  };
  "device/health": { args: { device: string }; result: Health };
  "device/architecture": { args: { device: string }; result: string };
  "device/apis": { args: { device: string }; result: DeviceApi[] };
  "device/interfaces": { args: { device: string }; result: DeviceInterface[] };
  "device/read": { args: { device: string; name: string }; result: unknown };
  "device/restart": { args: { device: string; confirmed: true }; result: null };
  "device/applications": { args: { device: string }; result: Application[] };
  "device/acap-updates": { args: { device: string }; result: AcapUpdate[] };
  "device/acap-install-candidates": {
    args: { device: string };
    result: AcapCandidate[];
  };
  "device/application-sdks": { args: { device: string }; result: string[] };
  "device/application-policy": { args: { device: string }; result: boolean };
  "device/application-policy-set": {
    args: {
      device: string;
      previous: boolean;
      value: boolean;
      confirmed: true;
    };
    result: null;
  };
  "device/application-license-remove": {
    args: {
      device: string;
      package: string;
      version: string;
      status: string;
      license_status: string;
      confirmed: true;
    };
    result: null;
  };
  "device/application-action": {
    args: {
      device: string;
      action: ApplicationAction;
      package: string;
      version: string;
      status: string;
      confirmed: true;
    };
    result: null;
  };
};

type Response = {
  id?: number;
  type?: string;
  result?: unknown;
  device?: DiscoveredDevice;
  message?: string;
  error?: { code: string; message: string };
};

type Pending = {
  resolve: (value: unknown) => void;
  reject: (error: Error) => void;
  timer: ReturnType<typeof setTimeout>;
  onDiscovered?: (device: DiscoveredDevice) => void;
  onWarning?: (message: string) => void;
  unknownMessage?: string;
};

const RESTART_UNKNOWN =
  "Restart outcome is unknown. Check the device before trying again.";
const APPLICATION_UNKNOWN =
  "Application action outcome is unknown. Check the application before trying again.";
const INSTALL_UNKNOWN =
  "Installation outcome is unknown. Check applications before trying again.";
const POLICY_UNKNOWN =
  "Policy change outcome is unknown. Check the policy before trying again.";
const LICENSE_UNKNOWN =
  "License change outcome is unknown. Check the application before trying again.";

export type ConnectionStatus =
  "connecting" | "connected" | "reconnecting" | "denied";

export class AxisConnection {
  private socket: WebSocket | null = null;
  private connected = false;
  private token = "";
  private nextId = 0;
  private pending = new Map<number, Pending>();
  private reconnectTimer: ReturnType<typeof setTimeout> | undefined;

  constructor(private readonly onStatus: (status: ConnectionStatus) => void) {}

  connect(token: string): void {
    this.disconnect();
    this.onStatus("connecting");
    this.openSocket(token);
  }

  private openSocket(token: string): void {
    this.token = token;
    const socket = new WebSocket(`ws://${location.host}/api/websocket`);
    this.socket = socket;
    socket.onopen = () => {
      if (this.socket === socket) socket.send(JSON.stringify({ token }));
    };
    socket.onmessage = (event: MessageEvent<string>) => {
      if (this.socket !== socket) return;
      const message = JSON.parse(event.data) as Response;
      if (message.type === "ready") {
        this.connected = true;
        this.onStatus("connected");
        return;
      }
      if (message.id === undefined) return;
      const pending = this.pending.get(message.id);
      if (!pending) return;
      if (message.type === "discovery/device") {
        if (message.device) pending.onDiscovered?.(message.device);
        return;
      }
      if (message.type === "discovery/warning") {
        if (message.message) pending.onWarning?.(message.message);
        return;
      }
      clearTimeout(pending.timer);
      this.pending.delete(message.id);
      if (message.error) pending.reject(new Error(message.error.message));
      else pending.resolve(message.result);
    };
    socket.onclose = (event) => {
      if (this.socket !== socket) return;
      this.disconnect();
      if (event.code === 1008) {
        this.onStatus("denied");
        return;
      }
      this.onStatus("reconnecting");
      this.reconnectTimer = setTimeout(() => this.openSocket(token), 2000);
    };
  }

  disconnect(): void {
    clearTimeout(this.reconnectTimer);
    const socket = this.socket;
    this.socket = null;
    this.connected = false;
    this.token = "";
    socket?.close();
    for (const pending of this.pending.values()) {
      clearTimeout(pending.timer);
      pending.reject(
        new Error(
          pending.unknownMessage ??
            "Connection lost. Try again once reconnected.",
        ),
      );
    }
    this.pending.clear();
  }

  async installApplication(device: string, file: File): Promise<void> {
    return this.uploadFile(
      "/api/application-upload",
      device,
      file,
      {
        "X-Axis-Filename": encodeURIComponent(file.name),
      },
      INSTALL_UNKNOWN,
    );
  }

  async uploadLicense(
    device: string,
    app: Application,
    file: File,
  ): Promise<void> {
    return this.uploadFile(
      "/api/application-license",
      device,
      file,
      {
        "X-Axis-Package": encodeURIComponent(app.name),
        "X-Axis-Version": encodeURIComponent(app.version),
        "X-Axis-Status": encodeURIComponent(app.status),
        "X-Axis-License-Status": encodeURIComponent(app.license_status),
      },
      LICENSE_UNKNOWN,
    );
  }

  async updateApplication(
    device: string,
    app: Application,
    candidate: AcapCandidate,
  ): Promise<void> {
    return this.requestWrite(
      "/api/application-update",
      { "Content-Type": "application/json" },
      JSON.stringify({
        device,
        filename: candidate.package.filename,
        digest: candidate.package.digest,
        version: app.version,
        status: app.status,
        vendor: app.vendor,
        warnings: candidate.warnings,
        confirmed: true,
      }),
      INSTALL_UNKNOWN,
    );
  }

  async installCatalogApplication(
    device: string,
    candidate: AcapCandidate,
  ): Promise<void> {
    return this.requestWrite(
      "/api/application-catalog-install",
      { "Content-Type": "application/json" },
      JSON.stringify({
        device,
        filename: candidate.package.filename,
        digest: candidate.package.digest,
        warnings: candidate.warnings,
        confirmed: true,
      }),
      INSTALL_UNKNOWN,
    );
  }

  private async uploadFile(
    path: string,
    device: string,
    file: File,
    extraHeaders: Record<string, string>,
    unknownMessage: string,
  ): Promise<void> {
    return this.requestWrite(
      path,
      {
        "X-Axis-Device": encodeURIComponent(device),
        ...extraHeaders,
        "X-Axis-Confirmed": "true",
        "Content-Type": "application/octet-stream",
      },
      file,
      unknownMessage,
    );
  }

  private async requestWrite(
    path: string,
    headers: Record<string, string>,
    body: BodyInit,
    unknownMessage: string,
  ): Promise<void> {
    if (!this.connected || !this.token) throw new Error("Not connected.");
    let response: globalThis.Response;
    try {
      response = await fetch(path, {
        method: "POST",
        redirect: "error",
        headers: {
          "X-Axis-Token": this.token,
          ...headers,
        },
        body,
      });
    } catch {
      throw new Error(unknownMessage);
    }
    let payload: { result?: unknown; error?: { message?: unknown } };
    try {
      payload = (await response.json()) as typeof payload;
    } catch {
      throw new Error(unknownMessage);
    }
    if (!response.ok) {
      const message = payload?.error?.message;
      throw new Error(typeof message === "string" ? message : unknownMessage);
    }
    if (payload?.result !== null) throw new Error(unknownMessage);
  }

  callWS<T extends keyof Commands>(
    type: T,
    args: Commands[T]["args"],
    onDiscovered?: (device: DiscoveredDevice) => void,
    onWarning?: (message: string) => void,
  ): Promise<Commands[T]["result"]> {
    const socket = this.socket;
    if (socket?.readyState !== WebSocket.OPEN || !this.connected) {
      return Promise.reject(new Error("Not connected."));
    }
    const id = ++this.nextId;
    const unknownMessage =
      type === "device/restart"
        ? RESTART_UNKNOWN
        : type === "device/application-action"
          ? APPLICATION_UNKNOWN
          : type === "device/application-policy-set"
            ? POLICY_UNKNOWN
            : type === "device/application-license-remove"
              ? LICENSE_UNKNOWN
              : undefined;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(unknownMessage ?? "Request timed out."));
      }, 65000);
      this.pending.set(id, {
        resolve: (value) => resolve(value as Commands[T]["result"]),
        reject,
        timer,
        onDiscovered,
        onWarning,
        unknownMessage,
      });
      socket.send(JSON.stringify({ id, type, ...args }));
    });
  }
}
