import Button from "@home-assistant/webawesome/dist/components/button/button.js";
import {
  css,
  html,
  nothing,
  type CSSResultGroup,
  type PropertyValues,
} from "lit";

export class AxisButton extends Button {
  static properties = {
    pressed: { type: Boolean },
    busy: { type: Boolean, reflect: true },
  };

  override appearance: Button["appearance"] = "outlined";
  pressed: boolean | undefined = undefined;
  busy = false;

  protected override updated(changed: PropertyValues<this>): void {
    super.updated(changed);
    if (this.pressed === undefined) this.button.removeAttribute("aria-pressed");
    else this.button.setAttribute("aria-pressed", String(this.pressed));
    if (this.busy) this.button.setAttribute("aria-busy", "true");
    else this.button.removeAttribute("aria-busy");
  }

  override render() {
    return html`
      ${super.render()}
      ${
        this.busy
          ? html`<svg class="busy-outline" aria-hidden="true">
              <rect pathLength="100"></rect>
            </svg>`
          : nothing
      }
    `;
  }

  static override get styles(): CSSResultGroup {
    return [
      Button.styles,
      css`
        :host {
          position: relative;
          --wa-form-control-height: var(--axis-control-height);
          --wa-form-control-padding-inline: var(--axis-space-3);
          --wa-form-control-border-radius: var(--axis-radius-control);
          --wa-form-control-border-width: var(--axis-border-width);
          --wa-form-control-border-style: solid;
          --wa-font-weight-action: var(--axis-font-weight-medium);
          --wa-button-transform-hover: none;
          --wa-button-transform-active: none;
        }
        .button {
          min-block-size: var(--axis-control-height);
          block-size: auto;
          padding-block: var(--axis-space-2);
          white-space: normal;
          overflow-wrap: anywhere;
        }
        :host([busy]) .button {
          border-color: transparent;
        }
        .busy-outline {
          position: absolute;
          inset: 0;
          inline-size: 100%;
          block-size: 100%;
          pointer-events: none;
        }
        .busy-outline rect {
          x: 1px;
          y: 1px;
          width: calc(100% - 2px);
          height: calc(100% - 2px);
          rx: var(--axis-radius-control);
          fill: none;
          stroke: var(--axis-color-primary);
          stroke-width: 2px;
          stroke-dasharray: 3 2;
          animation: busy-dashes 650ms linear infinite;
        }
        @keyframes busy-dashes {
          to {
            stroke-dashoffset: -5;
          }
        }
        @media (prefers-reduced-motion: reduce) {
          .busy-outline rect {
            animation: none;
          }
        }
      `,
    ];
  }
}

customElements.define("axis-button", AxisButton);

declare global {
  interface HTMLElementTagNameMap {
    "axis-button": AxisButton;
  }
}
