import { LitElement, css, html, nothing } from "lit";
import { keyed } from "lit/directives/keyed.js";
import { AxisConnection, type ConnectionStatus } from "./data/connection";
import {
  configureDevice,
  discoverDevices,
  fetchApis,
  fetchDevices,
  fetchDeviceSettings,
  fetchHealth,
  fetchInterfaces,
  readInterface,
  saveDevice,
  type Device,
  type DeviceApi,
  type DeviceConnection,
  type DeviceInterface,
  type DeviceSettings,
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

const defaultPort = (protocol: string): number =>
  protocol === "https" ? 443 : 80;

function submittedPort(values: FormData, original?: Device): number {
  const port = Number(values.get("port"));
  const protocol = String(values.get("web_proto") ?? "");
  if (original?.web_proto === protocol && original.port === port) return port;
  return port === defaultPort(protocol) ? 0 : port;
}

function connectionDraft(
  values: FormData,
  original?: Device,
): DeviceConnection {
  const text = (name: string) => String(values.get(name) ?? "");
  return {
    host: text("host"),
    port: submittedPort(values, original),
    username: text("username"),
    password: text("password"),
    web_proto: text("web_proto"),
    verify_ssl: values.has("verify_ssl"),
  };
}

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
    settings: { state: true },
    settingsPending: { state: true },
    settingsError: { state: true },
    connectionEdited: { state: true },
    connectionTest: { state: true },
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
        overflow-wrap: anywhere;
      }
      .dialog-controls {
        display: flex;
        flex-wrap: wrap;
        justify-content: flex-end;
        gap: var(--axis-space-2);
      }
      .settings-form input::placeholder {
        color: color-mix(
          in srgb,
          var(--axis-color-text) 70%,
          var(--axis-color-surface)
        );
        opacity: 1;
      }
      .settings-form fieldset + fieldset {
        margin-block-start: var(--axis-space-4);
      }
      .settings-form legend {
        font-weight: var(--axis-font-weight-medium);
        margin-block-end: var(--axis-space-2);
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
      select,
      button {
        font: inherit;
        color: inherit;
      }
      input:not([type="checkbox"]),
      select,
      button {
        min-block-size: var(--axis-control-height);
        padding-inline: var(--axis-space-3);
        border: var(--axis-border-width) solid var(--axis-color-border);
        border-radius: var(--axis-radius-control);
        background: var(--axis-color-surface);
      }
      .form-status {
        position: absolute;
        clip-path: inset(50%);
        inline-size: 1px;
        block-size: 1px;
        overflow: hidden;
        white-space: nowrap;
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
  private settings: { serial: string; value?: DeviceSettings } | null = null;
  private settingsPending = false;
  private settingsError = "";
  private connectionEdited = false;
  private connectionTest: {
    pending: boolean;
    message?: string;
    failed?: boolean;
    draft?: DeviceConnection;
  } | null = null;
  private operation = 0;
  private refreshId = 0;
  private readonly portDrafts = new WeakMap<
    HTMLSelectElement,
    { protocol: string; ports: Map<string, string> }
  >();
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
    if (this.saving || this.settingsPending) return;
    ++this.operation;
    this.registration = null;
    this.settings = null;
    this.connectionTest = null;
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
    this.settings = null;
    this.connectionTest = null;
    this.settingsPending = false;
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
    this.connectionTest = null;
    this.registration = device;
    this.saveError = "";
    this.selected = "";
    ++this.operation;
  }

  private async submitRegistration(event: SubmitEvent): Promise<void> {
    event.preventDefault();
    const form = event.currentTarget;
    const target = this.registration;
    if (
      !(form instanceof HTMLFormElement) ||
      !target ||
      this.saving ||
      this.connectionTest?.pending
    )
      return;
    const values = new FormData(form);
    const draft = connectionDraft(values);
    if (!this.connectionVerified(draft)) return;
    const password = form.querySelector<HTMLInputElement>(
      'input[name="password"]',
    );
    if (password) password.value = "";
    this.connectionTest = null;
    this.saving = true;
    this.saveError = "";
    try {
      const serial = await saveDevice(this.connection, {
        ...draft,
        host: target.host,
        alias: String(values.get("alias") ?? ""),
      });
      if (this.registration !== target) return;
      this.registration = null;
      this.saving = false;
      this.selected = serial;
      this.deviceView = "Health";
      const content = this.renderRoot.querySelector(".dialog-content");
      if (content) content.scrollTop = 0;
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
          <h3>Save discovered device</h3>
          <p>
            Enter the device credentials to read its identity and save it
            locally.
          </p>
          ${this.renderSettingsForm(target)}
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

  private async openSettings(serial: string): Promise<void> {
    this.connectionTest = null;
    this.connectionEdited = false;
    const request = { serial };
    this.settingsError = "";
    this.settings = request;
    try {
      const value = await fetchDeviceSettings(this.connection, serial);
      if (this.settings !== request) return;
      this.settings = { serial, value };
      await this.updateComplete;
      this.renderRoot
        .querySelector<HTMLInputElement>(".settings-form input")
        ?.focus();
    } catch (error) {
      if (this.settings === request)
        this.settingsError = (error as Error).message;
    }
  }

  private async closeSettings(): Promise<void> {
    this.settings = null;
    this.connectionTest = null;
    await this.updateComplete;
    this.renderRoot
      .querySelector<HTMLButtonElement>(".settings-trigger")
      ?.focus();
  }

  private async submitSettings(event: SubmitEvent): Promise<void> {
    event.preventDefault();
    const target = this.settings;
    const form = event.currentTarget;
    if (
      !target?.value ||
      this.settingsPending ||
      this.connectionTest?.pending ||
      !(form instanceof HTMLFormElement)
    )
      return;
    const values = new FormData(form);
    const draft = connectionDraft(values, target.value.device);
    if (
      this.needsConnectionTest(draft, target.value) &&
      !this.connectionVerified(draft)
    )
      return;
    this.settingsError = "";
    this.settingsPending = true;
    try {
      const result = await configureDevice(this.connection, target.serial, {
        ...draft,
        alias: String(values.get("alias") ?? ""),
      });
      if (this.settings !== target) return;
      this.devices = this.devices.map((device) =>
        device.serial === target.serial ? result.device : device,
      );
      this.settingsPending = false;
      void this.closeSettings();
      if (result.connection_changed) {
        this.viewData = {};
        this.selectedInterface = null;
        void this.showDeviceView(target.serial, this.deviceView);
      }
    } catch (error) {
      if (this.settings === target)
        this.settingsError = (error as Error).message;
    } finally {
      if (this.settings === target) this.settingsPending = false;
    }
  }

  private renderSettings() {
    const value = this.settings?.value;
    return html`
      <axis-card>
        <h3>Device settings</h3>
        <p>These settings affect how Axis connects, not the device itself.</p>
        ${!value && this.settingsError ? html`<p class="error" role="alert">${this.settingsError}</p>` : nothing}
        ${
          value
            ? this.renderSettingsForm(value)
            : this.settingsError
              ? html`<button type="button" @click=${this.closeSettings}>
                  Back
                </button>`
              : html`<p role="status">Loading settings…</p>`
        }
      </axis-card>
    `;
  }

  private async testConnection(event: Event): Promise<void> {
    const button = event.currentTarget;
    const form = button instanceof HTMLElement ? button.closest("form") : null;
    if (!form || this.connectionTest?.pending || !form.reportValidity()) return;
    const registration = this.registration;
    const saved = this.settings?.value?.device;
    if (!registration && !saved) return;
    const draft = connectionDraft(new FormData(form), saved);
    const request = { pending: true };
    this.connectionTest = request;
    this.settingsError = "";
    this.saveError = "";
    try {
      const serial = saved
        ? await this.connection.callWS("device/test-connection", {
            ...draft,
            device: saved.serial,
          })
        : await this.connection.callWS("devices/test-connection", draft);
      if (this.connectionTest === request) {
        this.connectionTest = {
          pending: false,
          draft,
          message: `Connection successful (serial: ${serial}).`,
        };
      }
    } catch (error) {
      if (this.connectionTest === request) {
        this.connectionTest = {
          pending: false,
          failed: true,
          message: (error as Error).message,
        };
      }
    }
  }

  private connectionVerified(draft: DeviceConnection): boolean {
    const verified = this.connectionTest?.draft;
    return (
      verified !== undefined &&
      JSON.stringify(verified) === JSON.stringify(draft)
    );
  }

  private needsConnectionTest(
    draft: DeviceConnection,
    original: DeviceSettings,
  ): boolean {
    const { device, username } = original;
    return (
      draft.host.trim() !== device.host ||
      draft.port !== device.port ||
      draft.web_proto !== device.web_proto ||
      draft.verify_ssl !== device.verify_ssl ||
      draft.username.trim() !== username ||
      draft.password !== ""
    );
  }

  private updateConnectionTest(event: Event): void {
    if (
      this.connectionTest?.pending ||
      !(
        event.target instanceof HTMLInputElement ||
        event.target instanceof HTMLSelectElement
      ) ||
      event.target.name === "alias" ||
      !(event.currentTarget instanceof HTMLFormElement)
    )
      return;
    // The protocol change handler restores the port before this event reaches the form.
    if (event.type === "input" && event.target instanceof HTMLSelectElement)
      return;
    this.connectionTest = null;
    this.saveError = "";
    this.settingsError = "";
    const saved = this.settings?.value;
    if (saved) {
      this.connectionEdited = this.needsConnectionTest(
        connectionDraft(new FormData(event.currentTarget), saved.device),
        saved,
      );
    }
  }

  private switchPortProtocol(event: Event, initialProtocol: string): void {
    const select = event.currentTarget;
    if (!(select instanceof HTMLSelectElement)) return;
    const port = select.form?.elements.namedItem("port");
    if (!(port instanceof HTMLInputElement)) return;
    const draft = this.portDrafts.get(select) ?? {
      protocol: initialProtocol,
      ports: new Map<string, string>(),
    };
    draft.ports.set(draft.protocol, port.value);
    draft.protocol = select.value;
    port.value =
      draft.ports.get(draft.protocol) ?? String(defaultPort(draft.protocol));
    this.portDrafts.set(select, draft);
  }

  private renderSettingsForm(target: DeviceSettings | DiscoveredDevice) {
    const registering = !("device" in target);
    const pending = registering ? this.saving : this.settingsPending;
    const testing = this.connectionTest?.pending ?? false;
    const saveLabel = registering ? "Save device" : "Save settings";
    const test = this.connectionTest;
    const mustTest = (registering || this.connectionEdited) && !test?.draft;
    const saveError = registering ? this.saveError : this.settingsError;
    const defaultName = registering
      ? target.name.trim() || target.host
      : deviceName({ ...target.device, alias: "" });
    const protocol = registering ? "https" : target.device.web_proto;
    const port =
      (registering ? 0 : target.device.port) || defaultPort(protocol);
    return html`
      <form
        class="settings-form"
        method="post"
        @submit=${registering ? this.submitRegistration : this.submitSettings}
        @input=${this.updateConnectionTest}
        @change=${this.updateConnectionTest}
        @keydown=${(event: KeyboardEvent) => {
          if (
            event.key !== "Enter" ||
            event.isComposing ||
            !(event.target instanceof HTMLInputElement) ||
            event.target.type === "checkbox"
          )
            return;
          event.preventDefault();
          if (
            !pending &&
            !testing &&
            !mustTest &&
            event.currentTarget instanceof HTMLFormElement
          )
            event.currentTarget.requestSubmit();
        }}
      >
        <fieldset ?disabled=${pending || testing}>
          <legend>General</legend>
          <label>
            Alias
            <input
              name="alias"
              .value=${registering ? "" : target.device.alias}
              placeholder=${defaultName}
            />
          </label>
        </fieldset>
        <fieldset ?disabled=${pending || testing}>
          <legend>Connection</legend>
          <label>
            Address
            <input
              name="host"
              .value=${registering ? target.host : target.device.host}
              ?readonly=${registering}
              required
            />
          </label>
          <label>
            Port
            <input
              name="port"
              type="number"
              min="1"
              max="65535"
              .value=${String(port)}
              required
            />
          </label>
          <label>
            Username
            <input
              name="username"
              autocomplete="username"
              .value=${registering ? "" : target.username}
              required
            />
          </label>
          <label>
            ${registering ? "Password" : "New password"}
            <input
              name="password"
              type="password"
              autocomplete=${registering ? "current-password" : "new-password"}
              placeholder=${registering ? nothing : "Keep current password"}
              ?required=${registering}
            />
          </label>
        </fieldset>
        <fieldset ?disabled=${pending || testing}>
          <legend>Advanced</legend>
          <label>
            Protocol
            <select
              name="web_proto"
              @change=${(event: Event) => this.switchPortProtocol(event, protocol)}
            >
              <option value="https" ?selected=${protocol === "https"}>
                HTTPS
              </option>
              <option value="http" ?selected=${protocol === "http"}>
                HTTP
              </option>
            </select>
          </label>
          <label class="certificate">
            <input
              name="verify_ssl"
              type="checkbox"
              .checked=${!registering && target.device.verify_ssl}
            />
            Verify HTTPS certificates
          </label>
          ${
            registering
              ? html`<small class="warning">
                  Turning verification off allows self-signed certificates but
                  skips certificate checks. HTTP is not encrypted. Verify the
                  address and only continue if you trust the device and network.
                </small>`
              : html`<small>
                  Use HTTPS with certificate verification when possible. HTTP is
                  not encrypted.
                </small>`
          }
        </fieldset>
        <div class="actions">
          <axis-button
            type="submit"
            variant=${saveError ? "danger" : "brand"}
            .busy=${pending}
            ?disabled=${pending || testing || mustTest}
            title=${saveError || (mustTest ? "Test the connection before saving." : "")}
          >
            ${saveLabel}
          </axis-button>
          <axis-button
            type="button"
            variant=${test?.failed ? "danger" : test?.draft ? "success" : "neutral"}
            .busy=${testing}
            ?disabled=${pending || testing}
            title=${test?.message ?? ""}
            @click=${this.testConnection}
          >
            Test connection
          </axis-button>
          <axis-button
            type="button"
            ?disabled=${pending}
            @click=${registering ? this.dismissDevice : this.closeSettings}
          >
            Cancel
          </axis-button>
        </div>
        <div class="form-status" role="status">
          ${test?.draft ? test.message : ""}
        </div>
        <div class="form-status" role="alert">
          ${saveError || (test?.failed ? test.message : "")}
        </div>
      </form>
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
        @cancel=${(event: Event) => {
          if (!this.settings) {
            this.dismissDevice(event);
            return;
          }
          event.preventDefault();
          if (!this.settingsPending) void this.closeSettings();
        }}
      >
        <div class="dialog-header">
          <header class="dialog-heading">
            <h2 id="device-dialog-title">
              ${this.registration ? this.registration.name.trim() || this.registration.host : device ? deviceName(device) : "Device details"}
            </h2>
            <div class="dialog-controls">
              ${
                device
                  ? html`<button
                      type="button"
                      class="settings-trigger"
                      aria-pressed=${String(this.settings !== null)}
                      ?disabled=${!connected || this.settingsPending}
                      @click=${() => (this.settings ? this.closeSettings() : this.openSettings(device.serial))}
                    >
                      Settings
                    </button>`
                  : nothing
              }
              <button
                type="button"
                autofocus
                ?disabled=${this.saving || this.settingsPending}
                @click=${this.dismissDevice}
              >
                Close
              </button>
            </div>
          </header>
          ${
            device
              ? html`<nav class="actions" aria-label="Device views">
                  ${DEVICE_VIEWS.map(
                    (view) => html`
                      <axis-button
                        variant=${this.deviceView === view ? "brand" : "neutral"}
                        .pressed=${!this.settings && this.deviceView === view}
                        .busy=${this.loading === "view" && this.deviceView === view}
                        ?disabled=${!connected || this.settingsPending}
                        @click=${() => {
                          const refresh =
                            !this.settings && this.deviceView === view;
                          this.settings = null;
                          this.connectionTest = null;
                          void this.showDeviceView(
                            device.serial,
                            view,
                            refresh,
                          );
                        }}
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
          ${this.settings ? this.renderSettings() : device ? this.renderSavedView(device, connected) : nothing}
        </div>
      </dialog>
    `;
  }
}

customElements.define("axis-app", AxisApp);
