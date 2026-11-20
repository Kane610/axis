import { LitElement, css, html, nothing } from "lit";
import type { Device, DiscoveredDevice } from "../data/devices";
import { deviceName } from "../device-name";
import { contentStyles } from "../resources/theme";
import "./axis-button";
import "./axis-card";

export type DiscoveryState =
  | { status: "scanning"; devices: DiscoveredDevice[] }
  | { status: "complete"; devices: DiscoveredDevice[] }
  | { status: "interrupted"; devices: DiscoveredDevice[] }
  | { status: "error"; devices: DiscoveredDevice[]; message: string };

export function macKey(value: string | undefined): string | undefined {
  const key = value
    ?.trim()
    .toLowerCase()
    .replace(/\*+$/, "")
    .replace(/[:-]/g, "");
  return key && /^[0-9a-f]{12}$/.test(key) ? key : undefined;
}

function deviceLabel(
  name: string,
  host: string,
  mac?: string,
  model?: string,
  discovered = false,
) {
  const details = [name ? host : "", mac, model].filter(Boolean).join(" — ");
  return html`
    <span class="device-info">
      <span class="device-heading">
        <span class="device-name">${name || host}</span>
        ${discovered ? html`<span class="warning">Discovered</span>` : nothing}
      </span>
      ${details ? html`<span class="device-meta">${details}</span>` : nothing}
    </span>
  `;
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
      .device-rows {
        display: grid;
        gap: var(--axis-space-2);
        list-style: none;
        margin-block: var(--axis-space-2) 0;
        padding: 0;
      }
      .device-rows li {
        min-inline-size: 0;
      }
      .device-rows axis-button {
        display: block;
        inline-size: 100%;
      }
      .device-rows axis-button::part(base) {
        justify-content: flex-start;
        text-align: start;
      }
      .device-info {
        display: grid;
        gap: var(--axis-space-1);
        min-inline-size: 0;
      }
      .device-heading {
        display: flex;
        flex-wrap: wrap;
        align-items: baseline;
        gap: var(--axis-space-2);
      }
      .device-meta {
        font-size: 0.875rem;
        font-weight: 400;
        opacity: 0.9;
      }
      .device-heading .warning {
        font-size: 0.75rem;
      }
      .discovered {
        --wa-color-neutral-border-quiet: var(--axis-color-warning);
      }
      .discovered::part(base) {
        border-color: var(--axis-color-warning);
      }
      .scan-control {
        position: relative;
        display: flex;
        justify-content: flex-end;
        margin-block-start: var(--axis-space-2);
      }
      .scan-control .failed::part(base) {
        border-color: var(--axis-color-danger);
      }
      .scan-status {
        position: absolute;
        inline-size: 1px;
        block-size: 1px;
        overflow: hidden;
        clip-path: inset(50%);
        white-space: nowrap;
      }
    `,
  ];

  devices: Device[] = [];
  discovery: DiscoveryState | null = null;
  selected = "";
  connected = false;

  protected render() {
    const discovery = this.discovery;
    const announcements = discovery?.devices ?? [];
    const discovered = announcements.filter(
      (device) => !isSavedDevice(device, this.devices),
    );
    const scanning = discovery?.status === "scanning";
    const failed = discovery?.status === "error";
    const scanLabel = scanning
      ? "Discovering devices…"
      : failed
        ? "Retry discovery · Failed"
        : discovery?.status === "complete"
          ? `Discover devices · ${discovered.length ? `${discovered.length} new` : "No new devices"}`
          : "Discover devices";
    const scanStatus = failed
      ? discovery.message
      : discovery?.status === "complete" && !discovered.length
        ? announcements.length
          ? "All discovered devices are already saved."
          : "No Axis devices found."
        : discovery
          ? scanLabel
          : "";
    return html`
      <axis-card>
        ${
          this.devices.length || discovered.length
            ? html`
                <ul class="device-rows" role="list" aria-label="Devices">
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
                          ${deviceLabel(
                            deviceName(device),
                            device.host,
                            device.discovery?.macaddress ||
                              macKey(device.serial)?.match(/../g)?.join(":"),
                          )}
                        </axis-button>
                      </li>
                    `,
                  )}
                  ${discovered.map(
                    (device) => html`
                      <li>
                        <axis-button
                          class="discovered"
                          ?disabled=${!this.connected}
                          @click=${() => this.dispatchEvent(new CustomEvent("axis-register", { detail: device }))}
                        >
                          ${deviceLabel(device.name, device.host, device.macaddress, device.model, true)}
                        </axis-button>
                      </li>
                    `,
                  )}
                </ul>
              `
            : nothing
        }
        <div class="scan-control">
          <axis-button
            class=${failed ? "failed" : ""}
            .busy=${scanning}
            ?disabled=${!this.connected}
            aria-disabled=${scanning ? "true" : "false"}
            title=${failed ? discovery.message : ""}
            @click=${() => {
              if (this.connected && !scanning)
                this.dispatchEvent(new Event("axis-scan"));
            }}
            >${scanLabel}</axis-button
          >
          <span class="scan-status" role="status">${scanStatus}</span>
        </div>
        ${this.devices.length === 0 ? html`<p>No saved devices. Use Discover devices to find devices on the local network.</p>` : ""}
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
