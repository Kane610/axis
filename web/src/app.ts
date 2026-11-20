import { LitElement, css, html, nothing } from "lit";
import { keyed } from "lit/directives/keyed.js";
import { AxisConnection, type ConnectionStatus } from "./data/connection";
import {
  discoverDevices,
  fetchApis,
  fetchDevices,
  fetchHealth,
  fetchInterfaces,
  readInterface,
  saveDevice,
  type Device,
  type DeviceApi,
  type DeviceInterface,
  type DiscoveredDevice,
  type Health,
} from "./data/devices";
import { deviceName } from "./device-name";
import { contentStyles } from "./resources/theme";
import "./components/axis-button";
import "./components/axis-card";
import "./components/axis-device-health";
import "./components/axis-device-list";
import type { DiscoveryState } from "./components/axis-device-list";

const DEVICE_VIEWS = ["Health", "APIs", "Interfaces"] as const;
type DeviceView = (typeof DEVICE_VIEWS)[number];

type DeviceViewData = {
  health?: Health;
  apis?: DeviceApi[];
  interfaces?: DeviceInterface[];
  interfaceResults?: ReadonlyMap<string, unknown>;
};

class AxisApp extends LitElement {
  static properties = {
    status: { state: true },
    devices: { state: true },
    discovery: { state: true },
    selected: { state: true },
    deviceView: { state: true },
    viewData: { state: true },
    selectedInterface: { state: true },
    error: { state: true },
    loading: { state: true },
    registration: { state: true },
    saving: { state: true },
    saveError: { state: true },
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
      dialog {
        box-sizing: border-box;
        inline-size: min(
          var(--axis-content-width),
          calc(100% - var(--axis-space-4))
        );
        max-inline-size: none;
        inset-block: var(--axis-dialog-top) auto;
        margin-block: 0;
        max-block-size: calc(
          100dvh - var(--axis-dialog-top) - var(--axis-space-2)
        );
        padding: 0;
        border: var(--axis-border-width) solid var(--axis-color-border);
        border-radius: var(--axis-radius-card);
        background: var(--axis-color-background);
        color: var(--axis-color-text);
        overflow: hidden;
      }
      dialog[open] {
        display: grid;
        grid-template-rows: auto minmax(0, 1fr);
      }
      dialog::backdrop {
        background: rgb(0 0 0 / 55%);
      }
      .dialog-header {
        padding: var(--axis-space-4);
        border-block-end: var(--axis-border-width) solid
          var(--axis-color-border);
      }
      .dialog-heading {
        flex-wrap: nowrap;
        align-items: start;
      }
      .dialog-header h2 {
        margin: 0;
        min-inline-size: 0;
      }
      .dialog-content {
        overflow: auto;
        overscroll-behavior: contain;
        padding: var(--axis-space-4);
      }
      .error {
        color: var(--axis-color-danger);
      }
      fieldset {
        display: grid;
        gap: var(--axis-space-3);
        border: 0;
        padding: 0;
        margin: 0;
        min-inline-size: 0;
      }
      label {
        display: grid;
        gap: var(--axis-space-1);
        max-inline-size: 28rem;
      }
      .certificate {
        display: block;
      }
      input,
      button {
        font: inherit;
        color: inherit;
      }
      input:not([type="checkbox"]),
      button {
        min-block-size: var(--axis-control-height);
        padding-inline: var(--axis-space-3);
        border: var(--axis-border-width) solid var(--axis-color-border);
        border-radius: var(--axis-radius-control);
        background: var(--axis-color-surface);
      }
      button[type="submit"] {
        background: var(--axis-color-primary);
        color: var(--axis-color-on-primary);
      }
      .registration-target {
        overflow-wrap: anywhere;
      }
    `,
  ];

  private status = "Connecting";
  private devices: Device[] = [];
  private discovery: DiscoveryState | null = null;
  private selected = "";
  private deviceView: DeviceView = "Health";
  private viewData: DeviceViewData = {};
  private selectedInterface: string | null = null;
  private error = "";
  private loading: "view" | "interface" | null = null;
  private registration: DiscoveredDevice | null = null;
  private saving = false;
  private saveError = "";
  private operation = 0;
  private refreshId = 0;
  private readonly connection = new AxisConnection((status) =>
    this.connectionChanged(status),
  );

  connectedCallback(): void {
    super.connectedCallback();
    window.addEventListener("hashchange", this.openAccessLink);
    window.addEventListener("resize", this.alignDeviceDialog);
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
    window.removeEventListener("resize", this.alignDeviceDialog);
    this.connection.disconnect();
    super.disconnectedCallback();
  }

  private alignDeviceDialog = (): void => {
    const dialog = this.renderRoot.querySelector("dialog");
    const list = this.renderRoot.querySelector("axis-device-list");
    if (dialog && list) {
      const top = list.getBoundingClientRect().top + window.scrollY;
      dialog.style.setProperty("--axis-dialog-top", `${top}px`);
    }
  };

  protected updated(): void {
    const dialog = this.renderRoot.querySelector("dialog");
    if (!dialog) return;
    const hasView = this.registration !== null || this.selected !== "";
    if (hasView) {
      this.alignDeviceDialog();
      if (!dialog.open) dialog.showModal();
    } else if (dialog.open) {
      dialog.close();
      if (!this.shadowRoot?.activeElement)
        this.renderRoot.querySelector("h1")?.focus();
    }
  }

  private dismissDevice(event?: Event): void {
    event?.preventDefault();
    if (this.saving) return;
    ++this.operation;
    this.registration = null;
    this.selected = "";
    this.viewData = {};
    this.selectedInterface = null;
    this.loading = null;
    this.error = "";
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
    this.registration = null;
    this.saving = false;
    this.saveError = "";
    this.viewData = {};
    this.selectedInterface = null;
    this.loading = null;
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
        await this.showDeviceView(this.selected, this.deviceView);
      } else {
        ++this.operation;
        this.selected = "";
        this.viewData = {};
        this.selectedInterface = null;
        this.loading = null;
      }
    } catch (error) {
      if (this.refreshId === refreshId) this.error = (error as Error).message;
    }
  }

  private async scanLocalNetwork(): Promise<void> {
    if (
      this.status !== "Connected" ||
      this.saving ||
      this.discovery?.status === "scanning"
    )
      return;
    this.registration = null;
    const scan = {
      status: "scanning",
      devices:
        this.discovery?.status === "complete" ? this.discovery.devices : [],
    } as const;
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

  private openRegistration(device: DiscoveredDevice): void {
    this.registration = device;
    this.saveError = "";
    this.selected = "";
    ++this.operation;
  }

  private async submitRegistration(event: SubmitEvent): Promise<void> {
    event.preventDefault();
    const form = event.currentTarget;
    const target = this.registration;
    if (!(form instanceof HTMLFormElement) || !target || this.saving) return;
    const values = new FormData(form);
    const password = form.querySelector<HTMLInputElement>(
      'input[name="password"]',
    );
    if (password) password.value = "";
    this.saving = true;
    this.saveError = "";
    try {
      const serial = await saveDevice(this.connection, {
        host: target.host,
        username: String(values.get("username") ?? ""),
        password: String(values.get("password") ?? ""),
        alias: String(values.get("alias") ?? ""),
        verify_ssl: !values.has("selfSigned"),
      });
      if (this.registration !== target) return;
      this.registration = null;
      this.saving = false;
      this.selected = serial;
      this.deviceView = "Health";
      await this.refreshDevices();
    } catch (error) {
      if (this.registration === target)
        this.saveError = (error as Error).message;
    } finally {
      if (this.registration === target) this.saving = false;
    }
  }

  private renderRegistration(target: DiscoveredDevice) {
    return keyed(
      target.host,
      html`
        <axis-card>
          <p class="registration-target">
            Connect over HTTPS to ${target.name || target.host}
            ${target.name ? `(${target.host})` : ""}.
          </p>
          <form method="post" @submit=${this.submitRegistration}>
            <fieldset ?disabled=${this.saving}>
              <label
                >Username
                <input name="username" autocomplete="username" required
              /></label>
              <label
                >Password
                <input
                  name="password"
                  type="password"
                  autocomplete="current-password"
                  required
              /></label>
              <label>Alias (optional) <input name="alias" /></label>
              <label class="certificate">
                <input name="selfSigned" type="checkbox" checked />
                Allow a self-signed certificate
              </label>
              <p class="warning">
                Allowing self-signed certificates skips server identity
                verification. Check the address and only continue if you trust
                this device and network.
              </p>
              <div class="actions">
                <button type="submit">Save device</button>
                <button type="button" @click=${this.dismissDevice}>
                  Cancel
                </button>
              </div>
            </fieldset>
          </form>
          <div role="status">
            ${this.saving ? "Verifying and saving device…" : nothing}
          </div>
          ${this.saveError ? html`<p class="error" role="alert">${this.saveError}</p>` : nothing}
        </axis-card>
      `,
    );
  }

  private async showDeviceView(
    serial: string,
    view: DeviceView,
    refresh = false,
  ): Promise<void> {
    if (this.deviceView !== view) {
      const content = this.renderRoot.querySelector(".dialog-content");
      if (content) content.scrollTop = 0;
    }
    this.selected = serial;
    this.deviceView = view;
    if (
      !refresh &&
      ((view === "Health" && this.viewData.health) ||
        (view === "APIs" && this.viewData.apis) ||
        (view === "Interfaces" && this.viewData.interfaces))
    ) {
      this.useCachedView();
      return;
    }
    if (view === "Health") {
      return this.browse(
        () => fetchHealth(this.connection, serial),
        (health) => {
          this.viewData = { ...this.viewData, health };
        },
      );
    }
    if (view === "APIs")
      return this.browse(
        () => fetchApis(this.connection, serial),
        (apis) => {
          this.viewData = { ...this.viewData, apis };
        },
      );
    return this.browse(
      () => fetchInterfaces(this.connection, serial),
      (interfaces) => {
        this.viewData = { ...this.viewData, interfaces };
        if (refresh) this.selectedInterface = null;
      },
    );
  }

  private async showInterface(serial: string, name: string): Promise<void> {
    const refresh = this.selectedInterface === name;
    this.selectedInterface = name;
    if (!refresh && this.viewData.interfaceResults?.has(name)) {
      this.useCachedView();
      return;
    }
    return this.browse(
      () => readInterface(this.connection, serial, name),
      (result) => {
        const interfaceResults = new Map(this.viewData.interfaceResults);
        interfaceResults.set(name, result);
        this.viewData = { ...this.viewData, interfaceResults };
      },
      "interface",
    );
  }

  private useCachedView(): void {
    ++this.operation;
    this.loading = null;
    this.error = "";
  }

  private async browse<T>(
    load: () => Promise<T>,
    apply: (result: T) => void,
    target: "view" | "interface" = "view",
  ): Promise<void> {
    const operation = ++this.operation;
    this.loading = target;
    this.error = "";
    try {
      const result = await load();
      if (this.operation !== operation) return;
      apply(result);
    } catch (error) {
      if (this.operation === operation) this.error = (error as Error).message;
    } finally {
      if (this.operation === operation) this.loading = null;
    }
  }

  private renderSavedView(device: Device, connected: boolean) {
    if (this.deviceView === "Health") {
      return html`
        <axis-device-health
          .device=${device}
          .health=${this.viewData.health ?? null}
          .loading=${this.loading === "view"}
        ></axis-device-health>
      `;
    }
    const { apis, interfaces, interfaceResults } = this.viewData;
    const data =
      this.deviceView === "APIs"
        ? apis
        : this.selectedInterface === null
          ? interfaces
          : interfaceResults?.get(this.selectedInterface);
    return html`
      <axis-card>
        <h3>${this.deviceView}</h3>
        ${
          this.deviceView === "Interfaces" && interfaces?.length
            ? html`<div class="actions">
                ${interfaces.map(
                  (item) => html`
                    <axis-button
                      .pressed=${this.selectedInterface === item.name}
                      .busy=${this.loading === "interface" && this.selectedInterface === item.name}
                      ?disabled=${!connected || !item.supported}
                      @click=${() => this.showInterface(device.serial, item.name)}
                    >
                      ${item.name}
                    </axis-button>
                  `,
                )}
              </div>`
            : nothing
        }
        ${data !== undefined ? html`<pre>${JSON.stringify(data, null, 2)}</pre>` : nothing}
      </axis-card>
    `;
  }

  protected render() {
    const device = this.devices.find((item) => item.serial === this.selected);
    const connected = this.status === "Connected";
    const hasView = this.registration !== null || this.selected !== "";
    const error = this.error
      ? html`<p class="error" role="alert">${this.error}</p>`
      : nothing;
    return html`
      <main>
        <header>
          <h1 tabindex="-1">Axis devices</h1>
          <span role="status" ?hidden=${hasView && !connected}
            >${this.status}</span
          >
        </header>
        ${hasView ? nothing : error}
        <axis-device-list
          .devices=${this.devices}
          .discovery=${this.discovery}
          .selected=${this.selected}
          .connected=${connected && !this.saving}
          @axis-refresh=${this.refreshDevices}
          @axis-scan=${this.scanLocalNetwork}
          @axis-select=${(event: CustomEvent<string>) => {
            this.registration = null;
            void this.showDeviceView(event.detail, "Health");
          }}
          @axis-register=${(event: CustomEvent<DiscoveredDevice>) => this.openRegistration(event.detail)}
        >
        </axis-device-list>
      </main>
      <dialog
        aria-labelledby="device-dialog-title"
        @cancel=${this.dismissDevice}
      >
        <div class="dialog-header">
          <header class="dialog-heading">
            <h2 id="device-dialog-title">
              ${this.registration ? "Save device" : device ? deviceName(device) : "Device details"}
            </h2>
            <button
              type="button"
              autofocus
              ?disabled=${this.saving}
              @click=${this.dismissDevice}
            >
              Close
            </button>
          </header>
          ${
            device
              ? html`<nav class="actions" aria-label="Device views">
                  ${DEVICE_VIEWS.map(
                    (view) => html`
                      <axis-button
                        variant=${this.deviceView === view ? "brand" : "neutral"}
                        .pressed=${this.deviceView === view}
                        .busy=${this.loading === "view" && this.deviceView === view}
                        ?disabled=${!connected}
                        @click=${() => this.showDeviceView(device.serial, view, this.deviceView === view)}
                        >${view}</axis-button
                      >
                    `,
                  )}
                </nav>`
              : nothing
          }
        </div>
        <div class="panels dialog-content">
          ${!connected && hasView ? html`<span role="status">${this.status}</span>` : nothing}
          ${hasView ? error : nothing}
          ${this.registration ? this.renderRegistration(this.registration) : nothing}
          ${device ? this.renderSavedView(device, connected) : nothing}
        </div>
      </dialog>
    `;
  }
}

customElements.define("axis-app", AxisApp);
