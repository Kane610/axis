import { LitElement, css, html, nothing } from "lit";
import { keyed } from "lit/directives/keyed.js";
import { AxisConnection, type ConnectionStatus } from "./data/connection";
import {
  configureDevice,
  controlApplication,
  discoverDevices,
  fetchArchitecture,
  fetchApis,
  fetchApplications,
  fetchApplicationPolicy,
  fetchApplicationSdks,
  fetchDevices,
  fetchDeviceSettings,
  fetchHealth,
  fetchInterfaces,
  installApplication,
  readInterface,
  removeApplicationLicense,
  restartDevice,
  saveDevice,
  setApplicationPolicy,
  uploadApplicationLicense,
  type Device,
  type Application,
  type ApplicationAction,
  type DeviceApi,
  type DeviceConnection,
  type DeviceInterface,
  type DeviceSettings,
  type DiscoveredDevice,
  type Health,
  type ServerSettings,
} from "./data/devices";
import { deviceName } from "./device-name";
import { contentStyles } from "./resources/theme";
import "./components/axis-button";
import "./components/axis-card";
import "./components/axis-device-health";
import { macKey, type DiscoveryState } from "./components/axis-device-list";

const DEVICE_VIEWS = ["Health", "APIs", "Interfaces"] as const;
type DeviceView = (typeof DEVICE_VIEWS)[number];

const CONNECTION_LABELS = {
  connecting: "Connecting to Axis…",
  connected: "Connected to Axis",
  reconnecting: "Reconnecting to Axis…",
  denied: "Access link rejected",
  "link-required": "Access link required",
} as const;

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
    serverSettingsOpen: { state: true },
    serverSettings: { state: true },
    serverPending: { state: true },
    serverError: { state: true },
    serverAutomatic: { state: true },
    serverSelection: { state: true },
    discoveryWarning: { state: true },
    restartConfirming: { state: true },
    restartPending: { state: true },
    restartMessage: { state: true },
    restartFailed: { state: true },
    applicationsOpen: { state: true },
    applications: { state: true },
    applicationLoading: { state: true },
    applicationPending: { state: true },
    applicationConfirmation: { state: true },
    installationOpen: { state: true },
    installationFile: { state: true },
    installationError: { state: true },
    installationDragging: { state: true },
    applicationMessage: { state: true },
    applicationFailed: { state: true },
    applicationArchitecture: { state: true },
    applicationSdks: { state: true },
    applicationPolicy: { state: true },
    applicationPolicyError: { state: true },
    licenseSelection: { state: true },
    licenseOpen: { state: true },
    licenseAppName: { state: true },
    licenseFile: { state: true },
    licenseError: { state: true },
    licenseDragging: { state: true },
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
      .app-heading {
        display: flex;
        margin-block-end: var(--axis-space-4);
      }
      .app-heading h1 {
        margin-block-end: 0;
      }
      .connection-heading {
        display: inline-block;
        min-inline-size: 0;
        max-inline-size: 100%;
      }
      .connection-status {
        display: block;
        block-size: 3px;
        margin-block-start: var(--axis-space-1);
        border-radius: var(--axis-radius-control);
        background-color: var(--axis-color-danger);
      }
      .connection-status[data-state="connected"] {
        background-color: var(--axis-color-success);
      }
      .connection-status:is(
        [data-state="connecting"],
        [data-state="reconnecting"]
      ) {
        background-color: light-dark(#a94c00, #ffd08a);
        animation: connection-pulse 1.6s ease-in-out infinite alternate;
      }
      @keyframes connection-pulse {
        to {
          opacity: 0.55;
        }
      }
      @media (prefers-reduced-motion: reduce) {
        .connection-status:is(
          [data-state="connecting"],
          [data-state="reconnecting"]
        ) {
          animation: none;
        }
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
      dialog.installation-dialog,
      dialog.license-dialog {
        inline-size: min(36rem, calc(100% - var(--axis-space-4)));
        inset: 0;
        margin: auto;
        max-block-size: calc(100dvh - var(--axis-space-4));
      }
      .license-dialog select {
        box-sizing: border-box;
        inline-size: 100%;
        min-inline-size: 0;
        max-inline-size: 100%;
      }
      .installation-drop {
        display: grid;
        justify-items: center;
        gap: var(--axis-space-3);
        padding: var(--axis-space-4);
        border: 2px dashed var(--axis-color-border);
        border-radius: var(--axis-radius-card);
        background: var(--axis-color-surface);
        text-align: center;
      }
      .installation-drop[data-dragging] {
        border-color: var(--axis-color-primary);
        background: var(--axis-color-surface-muted);
      }
      .installation-drop p {
        margin: 0;
        overflow-wrap: anywhere;
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
      .dialog-controls button:not(:disabled),
      .server-settings-trigger:not(:disabled) {
        cursor: pointer;
      }
      .dialog-controls button:not(:disabled):hover,
      .server-settings-trigger:not(:disabled):hover {
        background: var(--axis-color-surface-muted);
      }
      .server-interfaces label {
        display: flex;
        align-items: baseline;
        gap: var(--axis-space-2);
      }
      .server-interface-detail {
        font-size: 0.875rem;
        font-weight: 400;
      }
      .application-list {
        display: grid;
        gap: var(--axis-space-3);
      }
      .application-heading {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        align-items: baseline;
        gap: var(--axis-space-3);
      }
      .application-heading h4 {
        margin: 0;
        overflow-wrap: anywhere;
      }
      .policy-toggle {
        display: inline-flex;
        align-items: center;
        gap: var(--axis-space-2);
      }
      .policy-toggle input {
        appearance: none;
        box-sizing: border-box;
        inline-size: 2.75rem;
        block-size: 1.5rem;
        border: 1px solid var(--axis-color-border);
        border-radius: 1rem;
        background: var(--axis-color-surface-muted);
        cursor: pointer;
      }
      .policy-toggle input::before {
        content: "";
        display: block;
        inline-size: 1rem;
        block-size: 1rem;
        margin: 0.1875rem;
        border-radius: 50%;
        background: var(--axis-color-text);
      }
      .policy-toggle input:checked {
        background: var(--axis-color-primary);
      }
      .policy-toggle input:checked::before {
        transform: translateX(1.25rem);
        background: var(--axis-color-on-primary);
      }
      .policy-toggle input:focus-visible {
        outline: var(--axis-focus-ring);
        outline-offset: 2px;
      }
      .policy-toggle input:disabled {
        cursor: not-allowed;
        opacity: 0.6;
      }
      .application-status {
        font-weight: var(--axis-font-weight-medium);
        color: var(--axis-color-warning);
      }
      .application-status[data-status="Running"] {
        color: var(--axis-color-success);
      }
      .application-list dl {
        margin-block: var(--axis-space-2);
      }
      .device-views axis-button::part(base) {
        border-color: transparent;
        background: transparent;
      }
      .device-views axis-button.active::part(base) {
        border-color: var(--axis-color-border);
        background: var(--axis-color-surface-muted);
        color: var(--axis-color-primary);
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
      .form-status,
      .connection-status [role="status"] {
        position: absolute;
        clip-path: inset(50%);
        inline-size: 1px;
        block-size: 1px;
        overflow: hidden;
        white-space: nowrap;
      }
    `,
  ];

  private status: ConnectionStatus | "link-required" = "connecting";
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
  private serverSettingsOpen = false;
  private serverSettings: ServerSettings | null = null;
  private serverPending = false;
  private serverError = "";
  private serverAutomatic = true;
  private serverSelection: string[] = [];
  private discoveryWarning = "";
  private restartConfirming = false;
  private restartPending = false;
  private restartMessage = "";
  private restartFailed = false;
  private applicationsOpen = false;
  private applications: Application[] | null = null;
  private applicationLoading = false;
  private applicationPending = false;
  private applicationConfirmation: {
    app: Application;
    action: ApplicationAction;
  } | null = null;
  private installationOpen = false;
  private installationFile: File | null = null;
  private installationError = "";
  private installationDragging = false;
  private applicationMessage = "";
  private applicationFailed = false;
  private applicationArchitecture = "";
  private applicationSdks = "";
  private applicationPolicy: boolean | null = null;
  private applicationPolicyError = "";
  private licenseSelection: Application | null = null;
  private licenseOpen = false;
  private licenseAppName = "";
  private licenseFile: File | null = null;
  private licenseError = "";
  private licenseDragging = false;
  private architectureRequest = 0;
  private applicationInfoRequest = 0;
  private applicationPolicyRequest = 0;
  private operation = 0;
  private refreshId = 0;
  private backdropPressed = false;
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
    window.addEventListener("dragover", this.preventInstallationDrop);
    window.addEventListener("drop", this.preventInstallationDrop);
    this.openAccessLink();
  }

  private preventInstallationDrop = (event: DragEvent): void => {
    if (this.installationOpen || this.licenseOpen) event.preventDefault();
  };

  private openAccessLink = (): void => {
    const token =
      location.hash.slice(1) || sessionStorage.getItem("axis-token") || "";
    if (location.hash) {
      sessionStorage.setItem("axis-token", token);
      history.replaceState(null, "", location.pathname);
    }
    if (!token) {
      this.connection.disconnect();
      this.status = "link-required";
      this.error = "Open the private URL printed when the server starts.";
      return;
    }
    this.connection.connect(token);
  };

  disconnectedCallback(): void {
    window.removeEventListener("hashchange", this.openAccessLink);
    window.removeEventListener("resize", this.alignDeviceDialog);
    window.removeEventListener("dragover", this.preventInstallationDrop);
    window.removeEventListener("drop", this.preventInstallationDrop);
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
    const hasView =
      this.serverSettingsOpen ||
      this.registration !== null ||
      this.selected !== "";
    if (hasView) {
      this.alignDeviceDialog();
      if (!dialog.open) dialog.showModal();
    } else if (dialog.open) {
      dialog.close();
      if (!this.shadowRoot?.activeElement)
        this.renderRoot.querySelector("h1")?.focus();
    }
    const installation = this.renderRoot.querySelector<HTMLDialogElement>(
      ".installation-dialog",
    );
    if (installation) {
      if (this.installationOpen && !installation.open) installation.showModal();
      else if (!this.installationOpen && installation.open)
        installation.close();
    }
    const license =
      this.renderRoot.querySelector<HTMLDialogElement>(".license-dialog");
    if (license) {
      if (this.licenseOpen && !license.open) license.showModal();
      else if (!this.licenseOpen && license.open) license.close();
    }
  }

  private dismissDevice(event?: Event): void {
    event?.preventDefault();
    if (
      this.saving ||
      this.settingsPending ||
      this.serverPending ||
      this.restartPending ||
      this.applicationPending
    )
      return;
    const serverWasOpen = this.serverSettingsOpen;
    ++this.operation;
    this.registration = null;
    this.serverSettingsOpen = false;
    this.settings = null;
    this.connectionTest = null;
    this.selected = "";
    this.viewData = {};
    this.selectedInterface = null;
    this.loading = null;
    this.applicationLoading = false;
    this.error = "";
    this.restartConfirming = false;
    this.restartMessage = "";
    this.applicationsOpen = false;
    this.applications = null;
    ++this.architectureRequest;
    this.applicationArchitecture = "";
    this.applicationSdks = "";
    this.applicationPolicy = null;
    this.licenseSelection = null;
    this.licenseOpen = false;
    this.licenseAppName = "";
    this.licenseFile = null;
    this.licenseError = "";
    this.licenseDragging = false;
    this.applicationConfirmation = null;
    this.installationOpen = false;
    this.installationFile = null;
    this.installationError = "";
    this.installationDragging = false;
    this.applicationMessage = "";
    if (serverWasOpen)
      void this.updateComplete.then(() =>
        this.renderRoot
          .querySelector<HTMLButtonElement>(".server-settings-trigger")
          ?.focus(),
      );
  }

  private connectionChanged(status: ConnectionStatus): void {
    if (this.status === status && status === "reconnecting") return;
    this.status = status;
    this.error =
      status === "denied"
        ? "Open the private URL printed by the running server."
        : "";
    if (status === "connected") {
      void this.refreshDevices();
      void this.scanLocalNetwork();
      if (this.applicationsOpen && this.selected)
        void this.loadArchitecture(this.selected);
      return;
    }
    ++this.operation;
    ++this.refreshId;
    if (this.discovery)
      this.discovery = {
        status: "interrupted",
        devices: this.discovery.devices,
      };
    this.registration = null;
    this.serverSettingsOpen = false;
    this.serverPending = false;
    this.settings = null;
    this.connectionTest = null;
    this.settingsPending = false;
    this.saving = false;
    this.saveError = "";
    if (status !== "reconnecting") {
      this.viewData = {};
      this.selectedInterface = null;
    }
    this.loading = null;
    this.applicationLoading = false;
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
        if (!this.applicationPending)
          await this.showDeviceView(this.selected, this.deviceView);
      } else if (!this.applicationPending) {
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
      this.status !== "connected" ||
      this.saving ||
      this.discovery?.status === "scanning"
    )
      return;
    this.registration = null;
    let scan = {
      status: "scanning",
      devices: this.discovery?.devices ?? [],
    } as const;
    this.discovery = scan;
    this.discoveryWarning = "";
    try {
      const devices = await discoverDevices(
        this.connection,
        (device) => {
          if (this.discovery !== scan) return;
          const byHost = new Map(scan.devices.map((item) => [item.host, item]));
          byHost.set(device.host, device);
          scan = { status: "scanning", devices: [...byHost.values()] };
          this.discovery = scan;
        },
        (warning) => {
          if (this.discovery === scan) this.discoveryWarning = warning;
        },
      );
      if (this.discovery === scan) {
        const final = new Map(devices.map((device) => [device.host, device]));
        const ordered = scan.devices.flatMap(({ host }) => {
          const device = final.get(host);
          final.delete(host);
          return device ? [device] : [];
        });
        this.discovery = {
          status: "complete",
          devices: [...ordered, ...final.values()],
        };
      }
    } catch (error) {
      if (this.discovery === scan)
        this.discovery = {
          status: "error",
          devices: scan.devices,
          message: (error as Error).message,
        };
    }
  }

  private openRegistration(device: DiscoveredDevice): void {
    this.connectionTest = null;
    this.registration = device;
    this.saveError = "";
    this.selected = "";
    ++this.operation;
  }

  private registrationBlock(target: DiscoveredDevice): string {
    if (this.discovery?.status === "scanning")
      return "Wait for discovery to finish before testing the connection.";
    const mac = macKey(target.macaddress) ?? target.macaddress;
    const confirmed =
      this.discovery?.status === "complete" &&
      this.discovery.devices.some(
        (device) =>
          device.host === target.host &&
          (macKey(device.macaddress) ?? device.macaddress) === mac,
      );
    return confirmed
      ? ""
      : "This device was not confirmed. Close this form and run discovery again.";
  }

  private async submitRegistration(event: SubmitEvent): Promise<void> {
    event.preventDefault();
    const form = event.currentTarget;
    const target = this.registration;
    if (
      !(form instanceof HTMLFormElement) ||
      !target ||
      this.registrationBlock(target) ||
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
    const blocked = this.registrationBlock(target);
    return keyed(
      target.host,
      html`
        <axis-card>
          <h3>Save discovered device</h3>
          <p>
            ${
              blocked && this.discovery?.status !== "scanning"
                ? blocked
                : "Enter the device credentials to read its identity and save it locally."
            }
          </p>
          ${this.renderSettingsForm(target, blocked)}
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
    if (name === "applications") {
      this.applicationsOpen = true;
      this.restartConfirming = false;
      this.applications = null;
      this.error = "";
      this.applicationMessage = "";
      this.applicationConfirmation = null;
      this.installationOpen = false;
      this.installationFile = null;
      this.installationError = "";
      void this.loadArchitecture(serial);
      void this.loadApplicationInfo(serial);
      void this.updateComplete.then(() =>
        this.renderRoot
          .querySelector<HTMLButtonElement>(".application-back")
          ?.focus(),
      );
      await this.loadApplications(serial);
      return;
    }
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

  private async loadApplications(serial: string): Promise<void> {
    const operation = ++this.operation;
    this.applicationLoading = true;
    try {
      const applications = await fetchApplications(this.connection, serial);
      if (this.operation === operation && this.applicationsOpen)
        this.applications = applications;
    } catch (error) {
      if (this.operation === operation && this.applicationsOpen) {
        this.applicationFailed = true;
        this.applicationMessage = this.applicationMessage
          ? `${this.applicationMessage} Refresh failed: ${(error as Error).message}`
          : (error as Error).message;
      }
    } finally {
      if (this.operation === operation) this.applicationLoading = false;
    }
  }

  private async loadArchitecture(serial: string): Promise<void> {
    const request = ++this.architectureRequest;
    this.applicationArchitecture = "Loading…";
    try {
      const architecture = await fetchArchitecture(this.connection, serial);
      if (request === this.architectureRequest && this.applicationsOpen)
        this.applicationArchitecture = architecture;
    } catch (error) {
      if (request === this.architectureRequest && this.applicationsOpen)
        this.applicationArchitecture = `Unavailable: ${(error as Error).message}`;
    }
  }

  private async loadApplicationInfo(serial: string): Promise<void> {
    const request = this.architectureRequest;
    const infoRequest = ++this.applicationInfoRequest;
    const policyRequest = ++this.applicationPolicyRequest;
    this.applicationSdks = "Loading…";
    this.applicationPolicy = null;
    this.applicationPolicyError = "Loading…";
    void fetchApplicationSdks(this.connection, serial).then(
      (sdks) => {
        if (
          request === this.architectureRequest &&
          infoRequest === this.applicationInfoRequest &&
          this.applicationsOpen
        )
          this.applicationSdks = sdks.length
            ? sdks.join(", ")
            : "None reported";
      },
      (error: Error) => {
        if (
          request === this.architectureRequest &&
          infoRequest === this.applicationInfoRequest &&
          this.applicationsOpen
        )
          this.applicationSdks = `Unavailable: ${error.message}`;
      },
    );
    try {
      const policy = await fetchApplicationPolicy(this.connection, serial);
      if (
        request === this.architectureRequest &&
        policyRequest === this.applicationPolicyRequest &&
        this.applicationsOpen
      ) {
        this.applicationPolicy = policy;
        this.applicationPolicyError = "";
      }
    } catch (error) {
      if (
        request === this.architectureRequest &&
        policyRequest === this.applicationPolicyRequest &&
        this.applicationsOpen
      )
        this.applicationPolicyError = `Unavailable: ${(error as Error).message}`;
    }
  }

  private async applyPolicy(device: Device): Promise<void> {
    const previous = this.applicationPolicy;
    if (
      previous === null ||
      this.applicationPending ||
      this.status !== "connected"
    )
      return;
    ++this.applicationPolicyRequest;
    this.applicationPending = true;
    try {
      await setApplicationPolicy(
        this.connection,
        device.serial,
        previous,
        !previous,
      );
      this.applicationPolicy = !previous;
      this.applicationPolicyError = "";
    } catch (error) {
      this.applicationPolicy = null;
      this.applicationPolicyError = (error as Error).message;
    } finally {
      this.applicationPending = false;
    }
  }

  private async applyLicense(device: Device): Promise<void> {
    const selection = this.licenseSelection;
    if (
      !selection ||
      this.licenseAppName !== selection.name ||
      !this.applications?.includes(selection) ||
      this.applicationPending ||
      this.status !== "connected"
    )
      return;
    this.applicationPending = true;
    this.applicationMessage = "";
    this.licenseError = "";
    try {
      await removeApplicationLicense(this.connection, device.serial, selection);
      this.licenseSelection = null;
      this.licenseOpen = false;
      this.licenseAppName = "";
      this.licenseFile = null;
      this.applicationFailed = false;
      this.applicationMessage = "License change accepted.";
      this.viewData = {};
      await this.loadApplications(device.serial);
    } catch (error) {
      this.licenseSelection = null;
      this.licenseAppName = "";
      this.licenseFile = null;
      this.licenseError = (error as Error).message;
      this.applicationFailed = true;
      this.applicationMessage = (error as Error).message;
      this.applications = null;
      this.viewData = {};
    } finally {
      this.applicationPending = false;
      if (!this.licenseOpen)
        void this.updateComplete.then(() =>
          this.renderRoot
            .querySelector<HTMLElement>(".license-trigger")
            ?.focus(),
        );
    }
  }

  private closeLicense(event?: Event): void {
    event?.preventDefault();
    event?.stopPropagation();
    if (this.applicationPending) return;
    this.licenseOpen = false;
    this.licenseSelection = null;
    this.licenseAppName = "";
    this.licenseFile = null;
    this.licenseError = "";
    this.licenseDragging = false;
    void this.updateComplete.then(() =>
      this.renderRoot.querySelector<HTMLElement>(".license-trigger")?.focus(),
    );
  }

  private selectLicenseFile(files: FileList | null): void {
    if (!files || files.length === 0 || this.applicationPending) return;
    this.licenseFile = null;
    this.licenseError = "";
    if (files.length !== 1) {
      this.licenseError = "Choose one license file.";
      return;
    }
    const file = files[0];
    if (!file.size || file.size > 1024 * 1024) {
      this.licenseError = "Choose a non-empty license file up to 1 MiB.";
      return;
    }
    this.licenseFile = file;
  }

  private async uploadLicense(device: Device): Promise<void> {
    const file = this.licenseFile;
    const app = this.applications?.find(
      (item) => item.name === this.licenseAppName,
    );
    if (
      !file ||
      !app ||
      this.licenseSelection ||
      this.applicationPending ||
      this.status !== "connected"
    )
      return;
    this.applicationPending = true;
    this.applicationMessage = "";
    this.licenseError = "";
    try {
      await uploadApplicationLicense(this.connection, device.serial, app, file);
      this.licenseOpen = false;
      this.licenseFile = null;
      this.licenseAppName = "";
      this.applicationFailed = false;
      this.applicationMessage = "License change accepted.";
      this.viewData = {};
      await this.loadApplications(device.serial);
    } catch (error) {
      this.licenseFile = null;
      this.licenseAppName = "";
      this.licenseError = (error as Error).message;
      this.applicationFailed = true;
      this.applicationMessage = (error as Error).message;
      this.applications = null;
      this.viewData = {};
    } finally {
      this.applicationPending = false;
      if (!this.licenseOpen)
        void this.updateComplete.then(() =>
          this.renderRoot
            .querySelector<HTMLElement>(".license-trigger")
            ?.focus(),
        );
    }
  }

  private closeApplications(): void {
    if (this.applicationPending) return;
    ++this.operation;
    this.applicationsOpen = false;
    ++this.architectureRequest;
    this.applicationArchitecture = "";
    this.applicationSdks = "";
    this.applicationPolicy = null;
    this.licenseSelection = null;
    this.licenseOpen = false;
    this.licenseAppName = "";
    this.licenseFile = null;
    this.licenseError = "";
    this.licenseDragging = false;
    this.applicationLoading = false;
    this.applicationConfirmation = null;
    this.installationOpen = false;
    this.installationFile = null;
    this.installationError = "";
    this.installationDragging = false;
    this.applicationMessage = "";
    void this.updateComplete.then(() =>
      (
        this.renderRoot.querySelector<HTMLElement>(".application-trigger") ??
        this.renderRoot.querySelector<HTMLElement>(
          ".device-views axis-button.active",
        )
      )?.focus(),
    );
    if (
      this.selected &&
      !this.viewData.interfaces &&
      this.status === "connected"
    )
      void this.showDeviceView(this.selected, "Interfaces");
  }

  private async applyApplicationAction(device: Device): Promise<void> {
    const selection = this.applicationConfirmation;
    if (!selection || this.applicationPending) return;
    this.applicationPending = true;
    this.applicationMessage = "";
    try {
      await controlApplication(
        this.connection,
        device.serial,
        selection.app,
        selection.action,
      );
      this.applicationConfirmation = null;
      this.applicationFailed = false;
      this.applicationMessage = "Application action accepted.";
      this.viewData = {};
      await this.loadApplications(device.serial);
    } catch (error) {
      this.applicationConfirmation = null;
      this.applicationFailed = true;
      this.applicationMessage = (error as Error).message;
      this.applications = null;
      this.viewData = {};
    } finally {
      this.applicationPending = false;
    }
  }

  private closeInstallation(event?: Event): void {
    event?.preventDefault();
    event?.stopPropagation();
    if (this.applicationPending) return;
    this.installationOpen = false;
    this.installationFile = null;
    this.installationError = "";
    this.installationDragging = false;
    void this.updateComplete.then(() =>
      this.renderRoot
        .querySelector<HTMLElement>(".installation-trigger")
        ?.focus(),
    );
  }

  private selectInstallationFile(files: FileList | null): void {
    if (!files || files.length === 0 || this.applicationPending) return;
    this.installationFile = null;
    this.installationError = "";
    if (files.length !== 1) {
      this.installationError = "Choose one application package.";
      return;
    }
    const file = files[0];
    if (
      !file.name.toLowerCase().endsWith(".eap") ||
      file.size === 0 ||
      file.size > 1024 * 1024 * 1024
    ) {
      this.installationError =
        "Choose a non-empty .eap file up to 1024 MB (1 GiB).";
      return;
    }
    this.installationFile = file;
  }

  private async applyInstallation(device: Device): Promise<void> {
    const file = this.installationFile;
    if (!file || this.applicationPending || this.status !== "connected") return;
    this.applicationPending = true;
    this.applicationMessage = "";
    this.installationError = "";
    try {
      await installApplication(this.connection, device.serial, file);
      this.installationOpen = false;
      this.installationFile = null;
      this.applicationFailed = false;
      this.applicationMessage = "Application installed.";
      this.viewData = {};
      await this.loadApplications(device.serial);
    } catch (error) {
      this.installationFile = null;
      this.applicationFailed = true;
      this.applicationMessage = (error as Error).message;
      this.installationError = (error as Error).message;
      this.applications = null;
      this.viewData = {};
    } finally {
      this.applicationPending = false;
      if (!this.installationOpen)
        void this.updateComplete.then(() =>
          this.renderRoot
            .querySelector<HTMLElement>(".installation-trigger")
            ?.focus(),
        );
    }
  }

  private applicationUrl(device: Device, app: Application): string | null {
    const path = app.configuration_page;
    if (!path || path.includes("\\") || !/^\/?local\//.test(path)) return null;
    try {
      const port = device.port ? `:${device.port}` : "";
      const origin = new URL(`${device.web_proto}://${device.host}${port}`);
      if (
        (origin.protocol !== "http:" && origin.protocol !== "https:") ||
        origin.username ||
        origin.password
      )
        return null;
      const url = new URL(path.startsWith("/") ? path : `/${path}`, origin);
      return url.origin === origin.origin && url.pathname.startsWith("/local/")
        ? url.href
        : null;
    } catch {
      return null;
    }
  }

  private renderApplications(device: Device, connected: boolean) {
    const controlsDisabled =
      !connected ||
      this.applicationLoading ||
      this.applicationPending ||
      this.applicationConfirmation !== null ||
      this.licenseSelection !== null ||
      this.installationOpen ||
      this.licenseOpen;
    return html`
      <axis-card>
        <div class="application-heading">
          <h3>Installed applications</h3>
          <div class="actions">
            <axis-button
              class="installation-trigger"
              variant="brand"
              ?disabled=${controlsDisabled}
              @click=${() => {
                this.applicationMessage = "";
                this.installationError = "";
                this.installationOpen = true;
              }}
              >Install application</axis-button
            >
            <axis-button
              class="license-trigger"
              ?disabled=${controlsDisabled || !this.applications?.length}
              @click=${() => {
                this.applicationMessage = "";
                this.licenseError = "";
                this.licenseOpen = true;
              }}
              >Manage licenses</axis-button
            >
          </div>
        </div>
        <div>
          <label class="policy-toggle">
            <input
              type="checkbox"
              role="switch"
              .checked=${this.applicationPolicy === true}
              ?disabled=${controlsDisabled || this.applicationPolicy === null}
              @change=${(event: Event) => {
                const input = event.currentTarget as HTMLInputElement;
                input.checked = this.applicationPolicy === true;
                void this.applyPolicy(device);
              }}
            />
            Allow unsigned applications (AllowUnsigned)
          </label>
          ${
            this.applicationPolicy === null
              ? html`<p role="status">Policy: ${this.applicationPolicyError}</p>
                  <axis-button
                    ?disabled=${!connected || this.applicationPending || this.installationOpen || this.licenseOpen}
                    @click=${() => this.loadApplicationInfo(device.serial)}
                    >Refresh application information</axis-button
                  >`
              : nothing
          }
        </div>
        ${
          this.applicationMessage
            ? html`<p role=${this.applicationFailed ? "alert" : "status"}>
                ${this.applicationMessage}
              </p>`
            : nothing
        }
        ${this.applications?.length === 0 ? html`<p>No applications installed.</p>` : nothing}
        <div class="application-list">
          ${this.applications?.map((app) => {
            const confirmation = this.applicationConfirmation;
            const url = this.applicationUrl(device, app);
            const canOpenConfiguration =
              app.status === "Running" && connected && !controlsDisabled;
            return html`
              <axis-card>
                <div class="application-heading">
                  <h4>${app.nice_name || app.name}</h4>
                  <span class="application-status" data-status=${app.status}
                    >${app.status}</span
                  >
                </div>
                <dl>
                  <dt>Package</dt>
                  <dd>${app.name}</dd>
                  <dt>Version</dt>
                  <dd>${app.version || "Unknown"}</dd>
                  <dt>Vendor</dt>
                  <dd>${app.vendor || "Unknown"}</dd>
                  <dt>License</dt>
                  <dd>${app.license_status}</dd>
                  ${
                    app.bundled
                      ? html`<dt>Bundled</dt>
                          <dd>${app.bundled}</dd>`
                      : nothing
                  }
                  ${
                    app.signature_status
                      ? html`<dt>Signature</dt>
                          <dd>${app.signature_status}</dd>`
                      : nothing
                  }
                  ${
                    app.resources?.length
                      ? html`<dt>Resources</dt>
                          <dd>
                            ${app.resources.map((resource) => `${resource.name || "Unknown"}: ${resource.used || "Unknown"}`).join(", ")}
                          </dd>`
                      : nothing
                  }
                  ${
                    app.compatible_os_versions?.length
                      ? html`<dt>Compatible OS versions</dt>
                          <dd>
                            ${app.compatible_os_versions.map((range) => `${range.Min || "Any"} – ${range.Max || "Any"}`).join(", ")}
                          </dd>`
                      : nothing
                  }
                  ${
                    app.application_id
                      ? html`<dt>Application ID</dt>
                          <dd>${app.application_id}</dd>`
                      : nothing
                  }
                  ${
                    app.license_expiration_date
                      ? html`<dt>License expires</dt>
                          <dd>${app.license_expiration_date}</dd>`
                      : nothing
                  }
                </dl>
                ${
                  confirmation?.app === app
                    ? html` <p>
                          ${
                            confirmation.action === "remove"
                              ? `Uninstall ${app.nice_name || app.name} and remove its data?`
                              : `${confirmation.action === "start" ? "Start" : confirmation.action === "restart" ? "Restart" : "Stop"} ${app.nice_name || app.name}?`
                          }
                        </p>
                        <div class="actions">
                          <axis-button
                            variant=${confirmation.action === "remove" ? "danger" : "brand"}
                            .busy=${this.applicationPending}
                            ?disabled=${!connected || this.applicationPending}
                            @click=${() => this.applyApplicationAction(device)}
                            >Confirm
                            ${confirmation.action === "remove" ? "uninstall" : confirmation.action}</axis-button
                          >
                          <axis-button
                            ?disabled=${this.applicationPending}
                            @click=${() => (this.applicationConfirmation = null)}
                            >Cancel</axis-button
                          >
                        </div>`
                    : html` <div class="actions">
                        ${
                          app.status === "Running" || app.status === "Stopped"
                            ? html`<axis-button
                                ?disabled=${controlsDisabled}
                                @click=${() => {
                                  this.applicationMessage = "";
                                  this.applicationConfirmation = {
                                    app,
                                    action:
                                      app.status === "Running"
                                        ? "stop"
                                        : "start",
                                  };
                                }}
                                >${app.status === "Running" ? "Stop" : "Start"}</axis-button
                              >`
                            : nothing
                        }
                        ${
                          app.status === "Running"
                            ? html`<axis-button
                                ?disabled=${controlsDisabled}
                                @click=${() => {
                                  this.applicationMessage = "";
                                  this.applicationConfirmation = {
                                    app,
                                    action: "restart",
                                  };
                                }}
                                >Restart</axis-button
                              >`
                            : nothing
                        }
                        ${
                          url
                            ? html`<axis-button
                                href=${canOpenConfiguration ? url : nothing}
                                target="_blank"
                                rel="noopener noreferrer"
                                ?disabled=${!canOpenConfiguration}
                                >Open configuration</axis-button
                              >`
                            : app.configuration_page
                              ? html`<span
                                  >Configuration link unavailable</span
                                >`
                              : nothing
                        }
                        <axis-button
                          variant="danger"
                          ?disabled=${controlsDisabled}
                          @click=${() => {
                            this.applicationMessage = "";
                            this.applicationConfirmation = {
                              app,
                              action: "remove",
                            };
                          }}
                          >Uninstall</axis-button
                        >
                      </div>`
                }
              </axis-card>
            `;
          })}
        </div>
      </axis-card>
    `;
  }

  private renderInstallationDialog(device: Device, connected: boolean) {
    return html`
      <dialog
        class="installation-dialog"
        aria-labelledby="installation-dialog-title"
        @cancel=${this.closeInstallation}
        @dragover=${(event: DragEvent) => event.preventDefault()}
        @drop=${(event: DragEvent) => event.preventDefault()}
      >
        <div class="dialog-header">
          <header class="dialog-heading">
            <h2 id="installation-dialog-title">Install application</h2>
            <div class="dialog-controls">
              <button
                type="button"
                ?disabled=${this.applicationPending}
                @click=${this.closeInstallation}
              >
                Close
              </button>
            </div>
          </header>
        </div>
        <div class="dialog-content">
          <p>Hardware architecture: ${this.applicationArchitecture}</p>
          <p>Supported SDKs: ${this.applicationSdks}</p>
          <p>
            Unsigned applications:
            ${this.applicationPolicy === null ? this.applicationPolicyError : this.applicationPolicy ? "Allowed" : "Not allowed"}
          </p>
          <p>
            Choose a compatible .eap package up to 1024 MB (1 GiB).
            Administrator credentials are required.
          </p>
          <p>
            A matching application may be upgraded or downgraded. If an upgrade
            fails or is interrupted, both versions may be removed. A running
            application restarts after an upgrade; a new installation is not
            started automatically.
          </p>
          <p>
            Signed packages may temporarily require approximately twice their
            size in available device RAM during installation.
          </p>
          <div
            class="installation-drop"
            role="region"
            aria-label="Application package drop area"
            ?data-dragging=${this.installationDragging}
            @dragover=${(event: DragEvent) => {
              event.preventDefault();
              if (!connected || this.applicationPending) return;
              if (event.dataTransfer?.types.includes("Files")) {
                event.dataTransfer.dropEffect = "copy";
                this.installationDragging = true;
              }
            }}
            @dragleave=${(event: DragEvent) => {
              if (
                !(event.relatedTarget instanceof Node) ||
                !(event.currentTarget as HTMLElement).contains(
                  event.relatedTarget,
                )
              )
                this.installationDragging = false;
            }}
            @drop=${(event: DragEvent) => {
              event.preventDefault();
              this.installationDragging = false;
              if (!connected || this.applicationPending) return;
              if (!event.dataTransfer?.files.length) {
                this.installationFile = null;
                this.installationError = "Drop one application package.";
                return;
              }
              this.selectInstallationFile(event.dataTransfer.files);
            }}
          >
            <p>Drag and drop an application package here</p>
            <span>or</span>
            <axis-button
              ?disabled=${!connected || this.applicationPending}
              @click=${() =>
                this.renderRoot
                  .querySelector<HTMLInputElement>(".installation-file")
                  ?.click()}
              >Choose file</axis-button
            >
            <input
              class="installation-file"
              type="file"
              accept=".eap"
              hidden
              ?disabled=${!connected || this.applicationPending}
              @change=${(event: Event) => {
                const input = event.target as HTMLInputElement;
                this.selectInstallationFile(input.files);
                input.value = "";
              }}
            />
            ${
              this.installationFile
                ? html`<p>Selected: ${this.installationFile.name}</p>`
                : nothing
            }
          </div>
          ${
            this.installationError
              ? html`<p class="error" role="alert">
                  ${this.installationError}
                </p>`
              : nothing
          }
          ${
            this.applicationPending
              ? html`<p role="status">Uploading and installing application…</p>`
              : nothing
          }
          <div class="actions">
            <axis-button
              variant="brand"
              .busy=${this.applicationPending}
              ?disabled=${!connected || this.applicationPending || this.installationFile === null}
              @click=${() => this.applyInstallation(device)}
              >Confirm installation</axis-button
            >
            <axis-button
              ?disabled=${this.applicationPending}
              @click=${this.closeInstallation}
              >Cancel</axis-button
            >
          </div>
        </div>
      </dialog>
    `;
  }

  private renderLicenseDialog(device: Device, connected: boolean) {
    const app = this.applications?.find(
      (item) => item.name === this.licenseAppName,
    );
    return html`
      <dialog
        class="license-dialog"
        aria-labelledby="license-dialog-title"
        @cancel=${this.closeLicense}
        @dragover=${(event: DragEvent) => event.preventDefault()}
        @drop=${(event: DragEvent) => event.preventDefault()}
      >
        <div class="dialog-header">
          <header class="dialog-heading">
            <h2 id="license-dialog-title">Manage licenses</h2>
            <div class="dialog-controls">
              <button
                type="button"
                ?disabled=${this.applicationPending}
                @click=${this.closeLicense}
              >
                Close
              </button>
            </div>
          </header>
        </div>
        <div class="dialog-content">
          <p>
            Choose an application and a license file up to 1 MiB. Administrator
            credentials are required. Uploading a license may replace an
            existing key.
          </p>
          <label>
            Application
            <select
              aria-label="Application"
              .value=${this.licenseAppName}
              ?disabled=${!connected || this.applicationPending}
              @change=${(event: Event) => {
                this.licenseAppName = (
                  event.currentTarget as HTMLSelectElement
                ).value;
                this.licenseSelection = null;
              }}
            >
              <option value="">Select an application</option>
              ${this.applications?.map((app) => html`<option value=${app.name}>${app.nice_name || app.name} (${app.name})</option>`)}
            </select>
          </label>
          ${app ? html`<p>License status: ${app.license_status}</p>` : nothing}
          ${
            app &&
            (app.license_status === "Valid" || app.license_status === "Invalid")
              ? this.licenseSelection === app
                ? html`<p>
                      Remove the license for ${app.nice_name || app.name}?
                    </p>
                    <div class="actions">
                      <axis-button
                        variant="danger"
                        .busy=${this.applicationPending}
                        ?disabled=${!connected || this.applicationPending}
                        @click=${() => this.applyLicense(device)}
                        >Confirm license removal</axis-button
                      >
                      <axis-button
                        ?disabled=${this.applicationPending}
                        @click=${() => (this.licenseSelection = null)}
                        >Cancel removal</axis-button
                      >
                    </div>`
                : html`<axis-button
                    variant="danger"
                    ?disabled=${!connected || this.applicationPending}
                    @click=${() => (this.licenseSelection = app)}
                    >Remove license</axis-button
                  >`
              : nothing
          }
          <div
            class="installation-drop"
            role="region"
            aria-label="License file drop area"
            ?data-dragging=${this.licenseDragging}
            @dragover=${(event: DragEvent) => {
              event.preventDefault();
              if (
                !connected ||
                this.applicationPending ||
                this.licenseSelection
              )
                return;
              if (event.dataTransfer?.types.includes("Files")) {
                event.dataTransfer.dropEffect = "copy";
                this.licenseDragging = true;
              }
            }}
            @dragleave=${(event: DragEvent) => {
              if (
                !(event.relatedTarget instanceof Node) ||
                !(event.currentTarget as HTMLElement).contains(
                  event.relatedTarget,
                )
              )
                this.licenseDragging = false;
            }}
            @drop=${(event: DragEvent) => {
              event.preventDefault();
              this.licenseDragging = false;
              if (
                !connected ||
                this.applicationPending ||
                this.licenseSelection
              )
                return;
              if (!event.dataTransfer?.files.length) {
                this.licenseFile = null;
                this.licenseError = "Drop one license file.";
                return;
              }
              this.selectLicenseFile(event.dataTransfer.files);
            }}
          >
            <p>Drag and drop a license file here</p>
            <span>or</span>
            <axis-button
              ?disabled=${!connected || this.applicationPending || this.licenseSelection !== null}
              @click=${() => this.renderRoot.querySelector<HTMLInputElement>(".license-file")?.click()}
              >Choose file</axis-button
            >
            <input
              class="license-file"
              type="file"
              accept=".xml"
              hidden
              ?disabled=${!connected || this.applicationPending || this.licenseSelection !== null}
              @change=${(event: Event) => {
                const input = event.target as HTMLInputElement;
                this.selectLicenseFile(input.files);
                input.value = "";
              }}
            />
            ${this.licenseFile ? html`<p>Selected: ${this.licenseFile.name}</p>` : nothing}
          </div>
          ${this.licenseError ? html`<p class="error" role="alert">${this.licenseError}</p>` : nothing}
          ${this.applicationPending ? html`<p role="status">${this.licenseSelection ? "Removing license…" : "Uploading license file…"}</p>` : nothing}
          <div class="actions">
            <axis-button
              variant="brand"
              .busy=${this.applicationPending}
              ?disabled=${!connected || this.applicationPending || this.licenseSelection !== null || !this.licenseAppName || this.licenseFile === null}
              @click=${() => this.uploadLicense(device)}
              >Confirm license upload</axis-button
            >
            <axis-button
              ?disabled=${this.applicationPending}
              @click=${this.closeLicense}
              >Cancel</axis-button
            >
          </div>
        </div>
      </dialog>
    `;
  }

  private async restart(device: Device): Promise<void> {
    if (this.restartPending || !this.restartConfirming) return;
    this.restartPending = true;
    this.restartMessage = "";
    ++this.operation;
    this.loading = null;
    try {
      await restartDevice(this.connection, device.serial);
      this.restartMessage = "Restart requested.";
      this.restartFailed = false;
    } catch (error) {
      this.restartMessage = (error as Error).message;
      this.restartFailed = true;
    } finally {
      this.viewData = {};
      this.selectedInterface = null;
      this.restartConfirming = false;
      this.restartPending = false;
    }
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
          this.deviceView === "Interfaces"
            ? html`
                ${
                  this.restartConfirming
                    ? html`<p>
                          Restart ${deviceName(device)} (${device.serial})?
                        </p>
                        <div class="actions">
                          <axis-button
                            variant="brand"
                            .busy=${this.restartPending}
                            ?disabled=${this.restartPending || !connected}
                            @click=${() => this.restart(device)}
                            >Confirm restart</axis-button
                          >
                          <axis-button
                            ?disabled=${this.restartPending}
                            @click=${() => (this.restartConfirming = false)}
                            >Cancel</axis-button
                          >
                        </div>`
                    : html`<axis-button
                        ?disabled=${!connected || this.restartPending}
                        @click=${() => {
                          this.restartMessage = "";
                          this.restartConfirming = true;
                        }}
                        >Restart device</axis-button
                      >`
                }
                ${
                  this.restartMessage
                    ? html`<p role=${this.restartFailed ? "alert" : "status"}>
                        ${this.restartMessage}
                      </p>`
                    : nothing
                }
              `
            : nothing
        }
        ${
          this.deviceView === "Interfaces" && interfaces?.length
            ? html`<div class="actions">
                ${interfaces.map(
                  (item) => html`
                    <axis-button
                      class=${item.name === "applications" ? "application-trigger" : ""}
                      .pressed=${this.selectedInterface === item.name}
                      .busy=${this.loading === "interface" && this.selectedInterface === item.name}
                      ?disabled=${!connected || !item.supported || this.restartPending}
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
    if (registration && this.registrationBlock(registration)) return;
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

  private renderSettingsForm(
    target: DeviceSettings | DiscoveredDevice,
    blocked = "",
  ) {
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
            !blocked &&
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
            ?disabled=${pending || testing || mustTest || Boolean(blocked)}
            title=${blocked || saveError || (mustTest ? "Test the connection before saving." : "")}
          >
            ${saveLabel}
          </axis-button>
          <axis-button
            type="button"
            variant=${test?.failed ? "danger" : test?.draft ? "success" : "neutral"}
            .busy=${testing}
            ?disabled=${pending || testing || Boolean(blocked)}
            title=${blocked || test?.message || ""}
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
          ${blocked || (test?.draft ? test.message : "")}
        </div>
        <div class="form-status" role="alert">
          ${saveError || (test?.failed ? test.message : "")}
        </div>
      </form>
    `;
  }

  private async openServerSettings(): Promise<void> {
    this.serverSettingsOpen = true;
    this.serverSettings = null;
    this.serverError = "";
    this.serverPending = true;
    try {
      const settings = await this.connection.callWS("server/settings", {});
      if (!this.serverSettingsOpen) return;
      this.serverSettings = settings;
      this.serverAutomatic = settings.selected === null;
      this.serverSelection =
        settings.selected ??
        settings.interfaces
          .filter((item) => item.up && item.addresses.length)
          .map((item) => item.name);
    } catch (error) {
      if (this.serverSettingsOpen) this.serverError = (error as Error).message;
    } finally {
      this.serverPending = false;
    }
  }

  private async saveServerSettings(event: SubmitEvent): Promise<void> {
    event.preventDefault();
    if (!this.serverAutomatic && !this.serverSelection.length) {
      this.serverError =
        "Select at least one interface, or use automatic discovery.";
      return;
    }
    this.serverPending = true;
    this.serverError = "";
    try {
      await this.connection.callWS("server/configure", {
        interfaces: this.serverAutomatic ? null : this.serverSelection,
      });
      this.serverPending = false;
      this.dismissDevice();
    } catch (error) {
      if (this.serverSettingsOpen) this.serverError = (error as Error).message;
    } finally {
      this.serverPending = false;
    }
  }

  private renderServerSettings() {
    const settings = this.serverSettings;
    return html`
      <axis-card>
        <h3>Discovery network interfaces</h3>
        <p>Changes apply to the next web discovery scan.</p>
        ${this.serverError ? html`<p class="error" role="alert">${this.serverError}</p>` : nothing}
        ${
          settings
            ? html`
                <form @submit=${this.saveServerSettings}>
                  <fieldset
                    class="server-interfaces"
                    ?disabled=${this.serverPending}
                  >
                    <label>
                      <input
                        type="radio"
                        name="mode"
                        .checked=${this.serverAutomatic}
                        @change=${() => (this.serverAutomatic = true)}
                      />
                      Use all interfaces automatically
                    </label>
                    <label>
                      <input
                        type="radio"
                        name="mode"
                        .checked=${!this.serverAutomatic}
                        @change=${() => (this.serverAutomatic = false)}
                      />
                      Use selected interfaces
                    </label>
                    ${settings.interfaces.map(
                      (item) => html`
                        <label>
                          <input
                            type="checkbox"
                            .checked=${this.serverSelection.includes(item.name)}
                            ?disabled=${this.serverAutomatic}
                            @change=${(event: Event) => {
                              const checked = (event.target as HTMLInputElement)
                                .checked;
                              this.serverSelection = checked
                                ? [...this.serverSelection, item.name]
                                : this.serverSelection.filter(
                                    (name) => name !== item.name,
                                  );
                            }}
                          />
                          <span>
                            ${item.label}${item.label !== item.name ? ` (${item.name})` : ""}
                            <span class="server-interface-detail">
                              —
                              ${
                                item.up === false
                                  ? "Down"
                                  : item.up === null
                                    ? "Unavailable"
                                    : item.addresses.join(", ") ||
                                      "No IPv4 address"
                              }
                            </span>
                          </span>
                        </label>
                      `,
                    )}
                  </fieldset>
                  <div class="actions">
                    <axis-button
                      type="submit"
                      variant="brand"
                      .busy=${this.serverPending}
                      ?disabled=${this.serverPending}
                      >Save settings</axis-button
                    >
                    <axis-button
                      type="button"
                      ?disabled=${this.serverPending}
                      @click=${this.dismissDevice}
                      >Cancel</axis-button
                    >
                  </div>
                </form>
              `
            : nothing
        }
      </axis-card>
    `;
  }

  private renderConnectionStatus(label: string) {
    return html`
      <span class="connection-status" data-state=${this.status}>
        <span role="status">${label}</span>
      </span>
    `;
  }

  protected render() {
    const device = this.devices.find((item) => item.serial === this.selected);
    const connected = this.status === "connected";
    const status = CONNECTION_LABELS[this.status];
    const hasView =
      this.serverSettingsOpen ||
      this.registration !== null ||
      this.selected !== "";
    const error = this.error
      ? html`<p class="error" role="alert">${this.error}</p>`
      : nothing;
    return html`
      <main>
        <header class="app-heading">
          <div class="connection-heading" title=${status}>
            <h1 tabindex="-1">Axis devices</h1>
            ${this.renderConnectionStatus(status)}
          </div>
          <button
            type="button"
            class="server-settings-trigger"
            ?disabled=${!connected || this.saving}
            @click=${this.openServerSettings}
          >
            Server settings
          </button>
        </header>
        ${hasView ? nothing : error}
        <axis-device-list
          .devices=${this.devices}
          .discovery=${this.discovery}
          .selected=${this.selected}
          .connected=${connected && !this.saving}
          .warning=${this.discoveryWarning}
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
        @pointerdown=${(event: PointerEvent) => {
          const dialog = event.currentTarget;
          this.backdropPressed = false;
          if (event.target === dialog && dialog instanceof HTMLDialogElement) {
            const rect = dialog.getBoundingClientRect();
            this.backdropPressed =
              event.clientX < rect.left ||
              event.clientX >= rect.right ||
              event.clientY < rect.top ||
              event.clientY >= rect.bottom;
          }
        }}
        @pointercancel=${() => {
          this.backdropPressed = false;
        }}
        @click=${(event: MouseEvent) => {
          const dialog = event.currentTarget;
          if (
            this.backdropPressed &&
            event.target === dialog &&
            dialog instanceof HTMLDialogElement
          ) {
            const rect = dialog.getBoundingClientRect();
            if (
              event.clientX < rect.left ||
              event.clientX >= rect.right ||
              event.clientY < rect.top ||
              event.clientY >= rect.bottom
            )
              this.dismissDevice(event);
          }
          this.backdropPressed = false;
        }}
        @cancel=${(event: Event) => {
          if (this.applicationsOpen) {
            event.preventDefault();
            this.closeApplications();
            return;
          }
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
              ${this.serverSettingsOpen ? "Server settings" : this.registration ? this.registration.name.trim() || this.registration.host : this.applicationsOpen ? "Applications" : device ? deviceName(device) : "Device details"}
            </h2>
            <div class="dialog-controls">
              ${
                device && this.applicationsOpen
                  ? html`<button
                      type="button"
                      class="application-back"
                      ?disabled=${this.applicationPending}
                      @click=${this.closeApplications}
                    >
                      Back
                    </button>`
                  : device
                    ? html`<button
                        type="button"
                        class="settings-trigger"
                        aria-pressed=${String(this.settings !== null)}
                        ?disabled=${!connected || this.settingsPending || this.restartPending}
                        @click=${() => (this.settings ? this.closeSettings() : this.openSettings(device.serial))}
                      >
                        Settings
                      </button>`
                    : nothing
              }
              <button
                type="button"
                autofocus
                ?disabled=${this.saving || this.settingsPending || this.serverPending || this.restartPending || this.applicationPending}
                @click=${this.dismissDevice}
              >
                Close
              </button>
            </div>
          </header>
          ${
            device && !this.applicationsOpen
              ? html`<nav
                  class="actions device-views"
                  aria-label="Device views"
                >
                  ${DEVICE_VIEWS.map(
                    (view) => html`
                      <axis-button
                        class=${!this.settings && this.deviceView === view ? "active" : ""}
                        variant="neutral"
                        .pressed=${!this.settings && this.deviceView === view}
                        .busy=${this.loading === "view" && this.deviceView === view}
                        ?disabled=${!connected || this.settingsPending || this.restartPending}
                        @click=${() => {
                          const refresh =
                            !this.settings && this.deviceView === view;
                          this.settings = null;
                          this.connectionTest = null;
                          this.restartConfirming = false;
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
          ${hasView ? error : nothing}
          ${this.serverSettingsOpen ? this.renderServerSettings() : nothing}
          ${this.registration ? this.renderRegistration(this.registration) : nothing}
          ${this.settings ? this.renderSettings() : device && this.applicationsOpen ? this.renderApplications(device, connected) : device ? this.renderSavedView(device, connected) : nothing}
        </div>
      </dialog>
      ${device && this.applicationsOpen ? this.renderInstallationDialog(device, connected) : nothing}
      ${device && this.applicationsOpen ? this.renderLicenseDialog(device, connected) : nothing}
    `;
  }
}

customElements.define("axis-app", AxisApp);
