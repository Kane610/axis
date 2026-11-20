import { LitElement, html, nothing } from "lit";
import type { Device, Health } from "../data/devices";
import { deviceName } from "../device-name";
import { contentStyles } from "../resources/theme";
import "./axis-button";
import "./axis-card";

export class AxisDeviceHealth extends LitElement {
  static properties = {
    device: { attribute: false },
    health: { attribute: false },
    loading: { type: Boolean },
    connected: { type: Boolean },
  };

  static styles = contentStyles;

  device: Device | null = null;
  health: Health | null = null;
  loading = false;
  connected = false;

  protected render() {
    if (!this.device) return nothing;
    const matches = this.health?.serial === this.device.serial;
    return html`
      <axis-card>
        <h2>${deviceName(this.device)}</h2>
        <axis-button
          ?disabled=${this.loading || !this.connected}
          @click=${() => this.dispatchEvent(new Event("axis-refresh"))}
          >Refresh health</axis-button
        >
        ${this.loading ? html`<p role="status">Contacting the device. This may take up to 60 seconds.</p>` : nothing}
        ${!this.loading && !this.health ? html`<p>No live health data available. Check the connection and use Refresh health to try again.</p>` : nothing}
        ${
          this.health
            ? html`
                ${!matches ? html`<p class="warning">Warning: the connected device serial does not match the saved target.</p>` : nothing}
                <dl>
                  ${
                    matches
                      ? html`<dt>Serial</dt>
                          <dd>${this.health.serial}</dd>`
                      : html`<dt>Saved serial</dt>
                          <dd>${this.device.serial}</dd>
                          <dt>Reported serial</dt>
                          <dd>${this.health.serial}</dd>`
                  }
                  <dt>Product</dt>
                  <dd>${this.health.product}</dd>
                  <dt>Model</dt>
                  <dd>${this.health.model}</dd>
                  <dt>Firmware</dt>
                  <dd>${this.health.firmware_version}</dd>
                  <dt>Read at</dt>
                  <dd>${this.health.observed_at}</dd>
                </dl>
              `
            : nothing
        }
      </axis-card>
    `;
  }
}

customElements.define("axis-device-health", AxisDeviceHealth);

declare global {
  interface HTMLElementTagNameMap {
    "axis-device-health": AxisDeviceHealth;
  }
}
