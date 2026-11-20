import { LitElement, css, html, nothing } from "lit";
import { AxisConnection, type ConnectionStatus } from "./data/connection";
import {
  discoverDevices,
  fetchApis,
  fetchDevices,
  fetchHealth,
  fetchInterfaces,
  readInterface,
  type Device,
  type DeviceInterface,
  type Health,
} from "./data/devices";
import { contentStyles } from "./resources/theme";
import "./components/axis-button";
import "./components/axis-card";
import "./components/axis-device-health";
import "./components/axis-device-list";
import type { DiscoveryState } from "./components/axis-device-list";

class AxisApp extends LitElement {
  static properties = {
    status: { state: true },
    devices: { state: true },
    discovery: { state: true },
    selected: { state: true },
    health: { state: true },
    interfaces: { state: true },
    data: { state: true },
    error: { state: true },
    loading: { state: true },
  };

  static styles = [
    contentStyles,
    css`
      main {
        max-inline-size: var(--axis-content-width);
        margin-inline: auto;
        padding: var(--axis-space-6);
      }
      header {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        align-items: baseline;
        gap: var(--axis-space-4);
      }
      .panels {
        display: grid;
        gap: var(--axis-space-4);
      }
      .error {
        color: var(--axis-color-danger);
      }
    `,
  ];

  private status = "Connecting";
  private devices: Device[] = [];
  private discovery: DiscoveryState | null = null;
  private selected = "";
  private health: Health | null = null;
  private interfaces: DeviceInterface[] = [];
  private data: unknown = null;
  private error = "";
  private loading = false;
  private operation = 0;
  private refreshId = 0;
  private readonly connection = new AxisConnection((status) =>
    this.connectionChanged(status),
  );

  connectedCallback(): void {
    super.connectedCallback();
    window.addEventListener("hashchange", this.openAccessLink);
    this.openAccessLink();
  }

  private openAccessLink = (): void => {
    const token =
      location.hash.slice(1) || sessionStorage.getItem("axis-token") || "";
    if (location.hash) {
      sessionStorage.setItem("axis-token", token);
      history.replaceState(null, "", location.pathname);
    }
    if (!token) {
      this.connection.disconnect();
      this.status = "Access link required";
      this.error = "Open the private URL printed when the server starts.";
      return;
    }
    this.connection.connect(token);
  };

  disconnectedCallback(): void {
    window.removeEventListener("hashchange", this.openAccessLink);
    this.connection.disconnect();
    super.disconnectedCallback();
  }

  private connectionChanged(status: ConnectionStatus): void {
    this.status = {
      connecting: "Connecting",
      connected: "Connected",
      disconnected: "Disconnected; reconnecting",
      denied: "Access denied",
    }[status];
    this.error =
      status === "denied"
        ? "Open the private URL printed by the running server."
        : "";
    if (status === "connected") {
      void this.refreshDevices();
      return;
    }
    ++this.operation;
    ++this.refreshId;
    this.discovery = null;
    this.health = null;
    this.interfaces = [];
    this.data = null;
    this.loading = false;
  }

  private async refreshDevices(): Promise<void> {
    const refreshId = ++this.refreshId;
    try {
      const devices = await fetchDevices(this.connection);
      if (this.refreshId !== refreshId) return;
      this.devices = devices;
      this.error = "";
      if (
        this.selected &&
        this.devices.some((device) => device.serial === this.selected)
      ) {
        await this.selectDevice(this.selected);
      } else {
        ++this.operation;
        this.selected = "";
        this.loading = false;
      }
    } catch (error) {
      if (this.refreshId === refreshId) this.error = (error as Error).message;
    }
  }

  private async scanLocalNetwork(): Promise<void> {
    if (this.status !== "Connected" || this.discovery?.status === "scanning")
      return;
    const scan = { status: "scanning" } as const;
    this.discovery = scan;
    try {
      const devices = await discoverDevices(this.connection);
      if (this.discovery === scan)
        this.discovery = { status: "complete", devices };
    } catch (error) {
      if (this.discovery === scan)
        this.discovery = { status: "error", message: (error as Error).message };
    }
  }

  private async selectDevice(serial: string): Promise<void> {
    const operation = ++this.operation;
    this.selected = serial;
    this.health = null;
    this.interfaces = [];
    this.data = null;
    this.error = "";
    this.loading = true;
    try {
      const health = await fetchHealth(this.connection, serial);
      if (this.operation === operation) this.health = health;
    } catch (error) {
      if (this.operation === operation) this.error = (error as Error).message;
    } finally {
      if (this.operation === operation) this.loading = false;
    }
  }

  private async browse<T>(
    load: () => Promise<T>,
    apply?: (result: T) => void,
  ): Promise<void> {
    const operation = ++this.operation;
    this.loading = true;
    this.error = "";
    try {
      const result = await load();
      if (this.operation !== operation) return;
      apply?.(result);
      this.data = result;
    } catch (error) {
      if (this.operation === operation) this.error = (error as Error).message;
    } finally {
      if (this.operation === operation) this.loading = false;
    }
  }

  protected render() {
    const device = this.devices.find((item) => item.serial === this.selected);
    const connected = this.status === "Connected";
    return html`
      <main>
        <header>
          <h1>Axis devices</h1>
          <span role="status">${this.status}</span>
        </header>
        ${this.error ? html`<p class="error" role="alert">${this.error}</p>` : nothing}
        <div class="panels">
          <axis-device-list
            .devices=${this.devices}
            .discovery=${this.discovery}
            .selected=${this.selected}
            .connected=${connected}
            @axis-refresh=${this.refreshDevices}
            @axis-scan=${this.scanLocalNetwork}
            @axis-select=${(event: CustomEvent<string>) => this.selectDevice(event.detail)}
          >
          </axis-device-list>
          ${
            device
              ? html`
                  <axis-device-health
                    .device=${device}
                    .health=${this.health}
                    .connected=${connected}
                    .loading=${this.loading}
                    @axis-refresh=${() => this.selectDevice(device.serial)}
                  >
                  </axis-device-health>
                  <axis-card>
                    <h2>APIs and interfaces</h2>
                    <div class="actions">
                      <axis-button
                        ?disabled=${this.loading || !connected}
                        @click=${() => this.browse(() => fetchApis(this.connection, device.serial))}
                        >List APIs</axis-button
                      >
                      <axis-button
                        ?disabled=${this.loading || !connected}
                        @click=${() =>
                          this.browse(
                            () =>
                              fetchInterfaces(this.connection, device.serial),
                            (interfaces) => {
                              this.interfaces = interfaces;
                            },
                          )}
                        >Check interfaces</axis-button
                      >
                      ${this.interfaces.map(
                        (item) => html`
                          <axis-button
                            ?disabled=${this.loading || !connected || !item.supported}
                            @click=${() => this.browse(() => readInterface(this.connection, device.serial, item.name))}
                          >
                            ${item.name}
                          </axis-button>
                        `,
                      )}
                    </div>
                    ${this.data !== null ? html`<pre>${JSON.stringify(this.data, null, 2)}</pre>` : nothing}
                  </axis-card>
                `
              : nothing
          }
        </div>
      </main>
    `;
  }
}

customElements.define("axis-app", AxisApp);
