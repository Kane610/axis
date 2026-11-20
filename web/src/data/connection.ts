import type {
  ConfiguredDevice,
  Device,
  DeviceApi,
  DeviceConnection,
  DeviceInterface,
  DeviceSettings,
  DiscoveredDevice,
  Health,
  SaveDevice,
} from "./devices";

type Commands = {
  "devices/list": { args: Record<string, never>; result: Device[] };
  "devices/discover": {
    args: { stream: true };
    result: DiscoveredDevice[];
  };
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
  "device/apis": { args: { device: string }; result: DeviceApi[] };
  "device/interfaces": { args: { device: string }; result: DeviceInterface[] };
  "device/read": { args: { device: string; name: string }; result: unknown };
};

type Response = {
  id?: number;
  type?: string;
  result?: unknown;
  device?: DiscoveredDevice;
  error?: { code: string; message: string };
};

type Pending = {
  resolve: (value: unknown) => void;
  reject: (error: Error) => void;
  timer: ReturnType<typeof setTimeout>;
  onDiscovered?: (device: DiscoveredDevice) => void;
};

export type ConnectionStatus =
  "connecting" | "connected" | "reconnecting" | "denied";

export class AxisConnection {
  private socket: WebSocket | null = null;
  private connected = false;
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
    socket?.close();
    for (const pending of this.pending.values()) {
      clearTimeout(pending.timer);
      pending.reject(new Error("Connection lost. Try again once reconnected."));
    }
    this.pending.clear();
  }

  callWS<T extends keyof Commands>(
    type: T,
    args: Commands[T]["args"],
    onDiscovered?: (device: DiscoveredDevice) => void,
  ): Promise<Commands[T]["result"]> {
    const socket = this.socket;
    if (socket?.readyState !== WebSocket.OPEN || !this.connected) {
      return Promise.reject(new Error("Not connected."));
    }
    const id = ++this.nextId;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error("Request timed out."));
      }, 65000);
      this.pending.set(id, {
        resolve: (value) => resolve(value as Commands[T]["result"]),
        reject,
        timer,
        onDiscovered,
      });
      socket.send(JSON.stringify({ id, type, ...args }));
    });
  }
}
