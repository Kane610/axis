import Card from "@home-assistant/webawesome/dist/components/card/card.js";
import { css, type CSSResultGroup } from "lit";

export class AxisCard extends Card {
  static override get styles(): CSSResultGroup {
    return [
      Card.styles,
      css`
        :host {
          --spacing: var(--axis-space-4);
          --wa-panel-border-radius: var(--axis-radius-card);
          --wa-panel-border-width: var(--axis-border-width);
          --wa-panel-border-style: solid;
          --wa-shadow-s: none;
          min-inline-size: 0;
        }
      `,
    ];
  }
}

customElements.define("axis-card", AxisCard);

declare global {
  interface HTMLElementTagNameMap {
    "axis-card": AxisCard;
  }
}
