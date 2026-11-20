import { LitElement, css, html, nothing } from "lit";
import type { Device, DiscoveredDevice } from "../data/devices";
import { deviceName } from "../device-name";
import { contentStyles } from "../resources/theme";
import "./axis-button";
import "./axis-card";

export type DiscoveryState =
  | { status: "scanning"; devices: DiscoveredDevice[] }
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

function deviceLabel(name: string, host: string, mac?: string, model?: string) {
  return [name ? `${name} (${host})` : host, mac, model]
    .filter(Boolean)
    .join(" — ");
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
      .discovered {
        --wa-color-neutral-border-quiet: var(--axis-color-warning);
      }
      .discovered::part(base) {
        border-color: var(--axis-color-warning);
      }
      .scan-control {
        position: relative;
        display: inline-flex;
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
    const announcements =
      discovery && discovery.status !== "error" ? discovery.devices : [];
    const discovered = announcements.filter(
      (device) => !isSavedDevice(device, this.devices),
    );
    const scanning = discovery?.status === "scanning";
    const failed = discovery?.status === "error";
    const scanLabel = scanning
      ? "Scanning…"
      : failed
        ? "Retry scan · Scan failed"
        : discovery?.status === "complete"
          ? `Scan again · ${discovered.length ? `${discovered.length} new` : "No new devices"}`
          : "Scan local network";
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
        <h2>Devices</h2>
        <p>
          Saved details are not a live health check. Discovered devices are
          unverified; select one to save it.
        </p>
        <div class="actions">
          <axis-button
            ?disabled=${!this.connected}
            @click=${() => this.dispatchEvent(new Event("axis-refresh"))}
            >Refresh list</axis-button
          >
          <span class="scan-control">
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
          </span>
        </div>
        ${this.devices.length === 0 ? html`<p>No saved devices. Scan the local network to find devices to save.</p>` : ""}
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
                          ?disabled=${!this.connected || scanning}
                          @click=${() => this.dispatchEvent(new CustomEvent("axis-register", { detail: device }))}
                        >
                          ${deviceLabel(device.name, device.host, device.macaddress, device.model)}
                          <span class="warning">· Discovered</span>
                        </axis-button>
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
