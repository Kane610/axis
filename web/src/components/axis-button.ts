import Button from "@home-assistant/webawesome/dist/components/button/button.js";
import { css, type CSSResultGroup, type PropertyValues } from "lit";

export class AxisButton extends Button {
  static properties = { pressed: { type: Boolean } };

  override appearance: Button["appearance"] = "outlined";
  pressed: boolean | undefined = undefined;

  protected override updated(changed: PropertyValues<this>): void {
    super.updated(changed);
    if (this.pressed === undefined) this.button.removeAttribute("aria-pressed");
    else this.button.setAttribute("aria-pressed", String(this.pressed));
  }

  static override get styles(): CSSResultGroup {
    return [
      Button.styles,
      css`
        :host {
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
