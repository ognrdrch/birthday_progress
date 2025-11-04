/**
 * Birthday Progress Card for Home Assistant Lovelace
 * 
 * A custom card that displays birthday information in a clean two-section layout
 * showing time since birth and time until next birthday.
 */

import { LitElement, html, css } from "https://cdn.jsdelivr.net/gh/lit/dist@2/core/lit-core.min.js";

class BirthdayProgressCard extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      config: { type: Object },
      _state: { type: Object, state: true },
    };
  }

  static get styles() {
    return css`
      :host {
        display: block;
        padding: 16px;
      }

      .card {
        background: var(--card-background-color, #424242);
        border-radius: 8px;
        padding: 0;
        overflow: hidden;
        color: var(--primary-text-color, #ffffff);
      }

      .section {
        padding: 20px;
      }

      .section-top {
        padding-bottom: 20px;
      }

      .section-bottom {
        padding-top: 20px;
        border-top: 1px solid var(--divider-color, rgba(255, 255, 255, 0.12));
      }

      .name {
        font-size: 20px;
        font-weight: 700;
        color: var(--primary-text-color, #ffffff);
        margin: 0 0 12px 0;
        line-height: 1.2;
      }

      .next-birthday-title {
        font-size: 20px;
        font-weight: 700;
        color: var(--primary-text-color, #ffffff);
        margin: 0 0 12px 0;
        line-height: 1.2;
      }

      .datetime {
        font-size: 16px;
        color: var(--primary-text-color, #ffffff);
        margin: 0 0 8px 0;
        font-family: monospace;
      }

      .time-label {
        font-size: 14px;
        color: var(--secondary-text-color, rgba(255, 255, 255, 0.7));
        margin: 8px 0 4px 0;
      }

      .time-value {
        font-size: 14px;
        color: var(--primary-text-color, #ffffff);
        line-height: 1.5;
      }

      .error {
        color: var(--error-color, #f44336);
        text-align: center;
        padding: 20px;
        background: var(--card-background-color, #424242);
        border-radius: 8px;
      }

      @media (max-width: 600px) {
        .section {
          padding: 16px;
        }

        .name,
        .next-birthday-title {
          font-size: 18px;
        }

        .datetime {
          font-size: 14px;
        }

        .time-value {
          font-size: 13px;
        }
      }
    `;
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error("Entity is required");
    }
    this.config = config;
  }

  getCardSize() {
    return 3;
  }

  connectedCallback() {
    super.connectedCallback();
    this._updateState();
  }

  updated(changedProperties) {
    if (changedProperties.has("hass")) {
      this._updateState();
    }
  }

  _updateState() {
    if (!this.hass || !this.config) return;

    const entityId = this.config.entity;
    const state = this.hass.states[entityId];

    if (!state) {
      this._state = null;
      return;
    }

    this._state = {
      state: state.state,
      attributes: state.attributes,
      entityId: entityId,
    };
  }

  _formatNextBirthdayTitle(name) {
    // Support German "nächster Geburtstag" or use config title
    if (this.config.next_birthday_title) {
      return this.config.next_birthday_title;
    }
    // Default to English
    return `${name}'s Next Birthday`;
  }

  render() {
    if (!this.config || !this.hass) {
      return html`<div class="error">Card not configured</div>`;
    }

    if (!this._state) {
      return html`
        <div class="error">
          Entity ${this.config.entity} not found
        </div>
      `;
    }

    const attributes = this._state.attributes;
    const name = attributes.name || this.config.name || "Unknown";
    const birthDatetime = attributes.birth_datetime || attributes.birth_date || "N/A";
    const nextBirthdayDatetime = attributes.next_birthday_datetime || attributes.next_birthday || "N/A";
    const timeSinceBirth = attributes.time_since_birth || "N/A";
    const timeUntilNext = attributes.time_until_next_detailed || attributes.time_until_next || "N/A";

    return html`
      <div class="card">
        <div class="section section-top">
          <div class="name">${name}</div>
          <div class="datetime">${birthDatetime}</div>
          <div class="time-label">Time since event:</div>
          <div class="time-value">${timeSinceBirth}</div>
        </div>
        
        <div class="section section-bottom">
          <div class="next-birthday-title">${this._formatNextBirthdayTitle(name)}</div>
          <div class="datetime">${nextBirthdayDatetime}</div>
          <div class="time-label">Time until event:</div>
          <div class="time-value">${timeUntilNext}</div>
        </div>
      </div>
    `;
  }
}

customElements.define("birthday-progress-card", BirthdayProgressCard);
