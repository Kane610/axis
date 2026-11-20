import { LitElement, css, html, nothing } from "lit";
import type { Device, DiscoveredDevice } from "../data/devices";
import { deviceName } from "../device-name";
import { contentStyles } from "../resources/theme";
import "./axis-button";
import "./axis-card";

export type DiscoveryState =
  | { status: "scanning" }
  | { status: "complete"; devices: DiscoveredDevice[] }
  | { status: "error"; message: string };

function macKey(value: string | undefined): string | undefined {
  const key = value
    ?.trim()
    .toLowerCase()
    .replace(/\*+$/, "")
    .replace(/[:-]/g, "");
  return key && /^[0-9a-f]{12}$/.test(key) ? key : undefined;
}

function isSavedDevice(
  announcement: DiscoveredDevice,
  devices: Device[],
): boolean {
  const mac = macKey(announcement.macaddress);
  return devices.some(
    (device) =>
      device.serial === announcement.serial ||
      (mac !== undefined &&
        (mac === macKey(device.serial) ||
          mac === macKey(device.discovery?.macaddress))),
  );
}

export class AxisDeviceList extends LitElement {
  static properties = {
    devices: { attribute: false },
    discovery: { attribute: false },
    selected: {},
    connected: { type: Boolean },
  };

  static styles = [
    contentStyles,
    css`
      ul {
        list-style: none;
        margin-block-end: 0;
        padding: 0;
        align-items: start;
      }
      li {
        min-inline-size: 0;
        max-inline-size: 100%;
      }
      .discovered {
        box-sizing: border-box;
        min-block-size: var(--axis-control-height);
        padding: var(--axis-space-2) var(--axis-space-3);
        border: var(--axis-border-width) solid var(--axis-color-warning);
        border-radius: var(--axis-radius-control);
        font-weight: var(--axis-font-weight-medium);
        overflow-wrap: anywhere;
      }
      .error {
        color: var(--axis-color-danger);
      }
    `,
  ];

  devices: Device[] = [];
  discovery: DiscoveryState | null = null;
  selected = "";
  connected = false;

  protected render() {
    const discovery = this.discovery;
    const announcements =
      discovery?.status === "complete" ? discovery.devices : [];
    const discovered = announcements.filter(
      (device) => !isSavedDevice(device, this.devices),
    );
    return html`
      <axis-card>
        <h2>Devices</h2>
        <p>
          Saved details are not a live health check. Discovered devices are
          unverified; use the Axis CLI to save them.
        </p>
        <div class="actions">
          <axis-button
            ?disabled=${!this.connected}
            @click=${() => this.dispatchEvent(new Event("axis-refresh"))}
            >Refresh list</axis-button
          >
          <axis-button
            ?disabled=${!this.connected || discovery?.status === "scanning"}
            @click=${() => this.dispatchEvent(new Event("axis-scan"))}
            >Scan local network</axis-button
          >
        </div>
        <div role="status">
          ${
            discovery?.status === "scanning"
              ? "Scanning the local network…"
              : discovery?.status === "complete"
                ? announcements.length === 0
                  ? "No Axis devices found."
                  : discovered.length === 0
                    ? "All discovered devices are already saved."
                    : `New devices found: ${discovered.length}`
                : nothing
          }
        </div>
        ${discovery?.status === "error" ? html`<p class="error" role="alert">${discovery.message}</p>` : nothing}
        ${this.devices.length === 0 ? html`<p>No saved devices. Add one using the Axis CLI.</p>` : ""}
        ${
          this.devices.length || discovered.length
            ? html`
                <ul class="actions" role="list" aria-label="Devices">
                  ${this.devices.map(
                    (device) => html`
                      <li>
                        <axis-button
                          variant=${device.serial === this.selected ? "brand" : "neutral"}
                          appearance=${device.serial === this.selected ? "accent" : "outlined"}
                          .pressed=${device.serial === this.selected}
                          ?disabled=${!this.connected}
                          @click=${() => this.dispatchEvent(new CustomEvent("axis-select", { detail: device.serial }))}
                        >
                          ${deviceName(device)} (${device.host})
                        </axis-button>
                      </li>
                    `,
                  )}
                  ${discovered.map(
                    (device) => html`
                      <li class="discovered">
                        ${device.name || device.host}
                        ${device.name ? html` (${device.host})` : nothing} —
                        ${device.macaddress}${device.model ? ` — ${device.model}` : ""}
                        <span class="warning">· Discovered</span>
                      </li>
                    `,
                  )}
                </ul>
              `
            : nothing
        }
      </axis-card>
    `;
  }
}

customElements.define("axis-device-list", AxisDeviceList);

declare global {
  interface HTMLElementTagNameMap {
    "axis-device-list": AxisDeviceList;
  }
}
