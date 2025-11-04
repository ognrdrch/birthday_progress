/**
 * Birthday Progress Card for Home Assistant Lovelace
 * 
 * A custom card that displays birthday progress with a circular or horizontal
 * progress bar, showing age, time until next birthday, and progress percentage.
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
        background: var(--card-background-color, #ffffff);
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
      }

      .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      }

      .card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;
      }

      .name {
        font-size: 24px;
        font-weight: 600;
        color: var(--primary-text-color, #000000);
        margin: 0;
      }

      .progress-container {
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 20px 0;
      }

      .circular-progress {
        position: relative;
        width: 200px;
        height: 200px;
      }

      .circular-progress svg {
        transform: rotate(-90deg);
        width: 100%;
        height: 100%;
      }

      .circular-progress-circle-bg {
        fill: none;
        stroke: var(--divider-color, #e0e0e0);
        stroke-width: 12;
      }

      .circular-progress-circle {
        fill: none;
        stroke: var(--accent-color, #03a9f4);
        stroke-width: 12;
        stroke-linecap: round;
        stroke-dasharray: 565.48;
        transition: stroke-dashoffset 0.5s ease;
        filter: drop-shadow(0 0 8px rgba(3, 169, 244, 0.5));
      }

      .circular-progress-text {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
      }

      .progress-percentage {
        font-size: 36px;
        font-weight: 700;
        color: var(--primary-text-color, #000000);
        line-height: 1;
      }

      .progress-label {
        font-size: 14px;
        color: var(--secondary-text-color, #666666);
        margin-top: 4px;
      }

      .horizontal-progress {
        width: 100%;
        height: 24px;
        background: var(--divider-color, #e0e0e0);
        border-radius: 12px;
        overflow: hidden;
        position: relative;
        margin: 20px 0;
      }

      .horizontal-progress-bar {
        height: 100%;
        background: linear-gradient(
          90deg,
          var(--accent-color, #03a9f4) 0%,
          var(--accent-color, #03a9f4) 50%,
          var(--primary-color, #2196f3) 100%
        );
        border-radius: 12px;
        transition: width 0.5s ease;
        box-shadow: 0 2px 8px rgba(3, 169, 244, 0.3);
      }

      .info-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin-top: 24px;
      }

      .info-item {
        background: var(--secondary-background-color, #f5f5f5);
        padding: 16px;
        border-radius: 8px;
        text-align: center;
      }

      .info-label {
        font-size: 12px;
        color: var(--secondary-text-color, #666666);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
      }

      .info-value {
        font-size: 18px;
        font-weight: 600;
        color: var(--primary-text-color, #000000);
      }

      .age-exact {
        font-family: 'Courier New', monospace;
        font-size: 16px;
      }

      .error {
        color: var(--error-color, #f44336);
        text-align: center;
        padding: 20px;
      }

      @media (max-width: 600px) {
        .circular-progress {
          width: 150px;
          height: 150px;
        }

        .progress-percentage {
          font-size: 28px;
        }

        .info-grid {
          grid-template-columns: 1fr;
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
    return 4;
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

  _calculateCircumference(radius) {
    return 2 * Math.PI * radius;
  }

  _calculateProgressOffset(percentage, circumference) {
    return circumference - (percentage / 100) * circumference;
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

    const progress = parseFloat(this._state.state) || 0;
    const attributes = this._state.attributes;
    const progressType = this.config.progress_type || "circular";
    const radius = 90;
    const circumference = this._calculateCircumference(radius);
    const offset = this._calculateProgressOffset(progress, circumference);

    return html`
      <div class="card">
        <div class="card-header">
          <h2 class="name">${attributes.name || this.config.name || "Birthday"}</h2>
        </div>

        ${progressType === "circular"
          ? html`
              <div class="progress-container">
                <div class="circular-progress">
                  <svg viewBox="0 0 200 200">
                    <circle
                      class="circular-progress-circle-bg"
                      cx="100"
                      cy="100"
                      r="${radius}"
                    ></circle>
                    <circle
                      class="circular-progress-circle"
                      cx="100"
                      cy="100"
                      r="${radius}"
                      stroke-dashoffset="${offset}"
                      stroke-dasharray="${circumference}"
                    ></circle>
                  </svg>
                  <div class="circular-progress-text">
                    <div class="progress-percentage">${progress.toFixed(2)}%</div>
                    <div class="progress-label">Progress</div>
                  </div>
                </div>
              </div>
            `
          : html`
              <div class="horizontal-progress">
                <div
                  class="horizontal-progress-bar"
                  style="width: ${progress}%"
                ></div>
              </div>
              <div style="text-align: center; margin-top: 8px;">
                <span class="progress-percentage">${progress.toFixed(2)}%</span>
              </div>
            `}

        <div class="info-grid">
          <div class="info-item">
            <div class="info-label">Exact Age</div>
            <div class="info-value age-exact">${attributes.age_exact || "N/A"}</div>
          </div>
          <div class="info-item">
            <div class="info-label">Time Until Next</div>
            <div class="info-value">${attributes.time_until_next || "N/A"}</div>
          </div>
          <div class="info-item">
            <div class="info-label">Next Birthday</div>
            <div class="info-value">
              ${attributes.next_birthday
                ? new Date(attributes.next_birthday).toLocaleDateString()
                : "N/A"}
            </div>
          </div>
        </div>
      </div>
    `;
  }
}

customElements.define("birthday-progress-card", BirthdayProgressCard);

