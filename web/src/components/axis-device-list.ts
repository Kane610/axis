import { LitElement, html } from "lit";
import type { Device } from "../data/devices";
import { deviceName } from "../device-name";
import { contentStyles } from "../resources/theme";
import "./axis-button";
import "./axis-card";

export class AxisDeviceList extends LitElement {
  static properties = {
    devices: { attribute: false },
    selected: {},
    connected: { type: Boolean },
  };

  static styles = contentStyles;

  devices: Device[] = [];
  selected = "";
  connected = false;

  protected render() {
    return html`
      <axis-card>
        <h2>Saved devices</h2>
        <p>Saved details do not indicate whether a device is online.</p>
        <axis-button
          ?disabled=${!this.connected}
          @click=${() => this.dispatchEvent(new Event("axis-refresh"))}
          >Refresh list</axis-button
        >
        ${this.devices.length === 0 ? html`<p>No saved devices. Add one using the Axis CLI.</p>` : ""}
        <div class="actions">
          ${this.devices.map(
            (device) => html`
              <axis-button
                variant=${device.serial === this.selected ? "brand" : "neutral"}
                appearance=${device.serial === this.selected ? "accent" : "outlined"}
                .pressed=${device.serial === this.selected}
                ?disabled=${!this.connected}
                @click=${() => this.dispatchEvent(new CustomEvent("axis-select", { detail: device.serial }))}
              >
                ${deviceName(device)} (${device.host})
              </axis-button>
            `,
          )}
        </div>
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
