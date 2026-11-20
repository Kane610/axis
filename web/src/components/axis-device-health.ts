import { LitElement, html, nothing } from "lit";
import type { Device, Health } from "../data/devices";
import { contentStyles } from "../resources/theme";
import "./axis-card";

export class AxisDeviceHealth extends LitElement {
  static properties = {
    device: { attribute: false },
    health: { attribute: false },
    loading: { type: Boolean },
  };

  static styles = contentStyles;

  device: Device | null = null;
  health: Health | null = null;
  loading = false;

  protected render() {
    if (!this.device) return nothing;
    const matches = this.health?.serial === this.device.serial;
    return html`
      <axis-card>
        <h3>Device health</h3>
        ${!this.loading && !this.health ? html`<p>No live health data available. Check the connection and select Health again to retry.</p>` : nothing}
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
