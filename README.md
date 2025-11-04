# Birthday Progress Integration for Home Assistant

A beautiful and feature-rich Home Assistant custom integration for tracking birthdays with real-time age calculation, progress toward the next birthday, and elegant Lovelace cards.

![Integration Quality Scale](https://img.shields.io/badge/Quality%20Scale-Silver-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

## Features

- 🎂 **Multiple Birthday Tracking**: Track unlimited birthdays through the GUI
- ⏱️ **Real-time Updates**: Updates every second for precise calculations
- 📊 **Progress Visualization**: Beautiful circular or horizontal progress bars
- 📅 **Exact Age Calculation**: Shows age down to the second (e.g., "27y 153d 04:12:10")
- ⏰ **Countdown Timer**: Time until next birthday with days, hours, minutes, and seconds
- 🎨 **Modern UI**: Polished Lovelace cards with theme support (light/dark mode)
- 📱 **Responsive Design**: Works perfectly on desktop and mobile devices
- 🔧 **GUI Configuration**: Full Config Flow support - no YAML required

## Installation

### HACS (Recommended)

**For detailed step-by-step instructions, see [HACS_SETUP.md](HACS_SETUP.md)**

Quick steps:
1. Make sure you have [HACS](https://hacs.xyz/) installed
2. Go to **HACS** → **Integrations**
3. Click the three dots menu (⋮) → **Custom repositories**
4. Add this repository:
   - **Repository**: `https://github.com/yourusername/birthday_progress`
   - **Category**: **Integration**
5. Search for "Birthday Progress" and install it
6. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/birthday_progress` folder to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "Birthday Progress"

## Configuration

### Adding a Birthday Entry

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **Birthday Progress**
4. Fill in the form:
   - **Name**: Person's name (e.g., "John Doe")
   - **Birth Date**: Date in YYYY-MM-DD format (e.g., "1995-03-15")
   - **Birth Time**: Optional time in HH:MM:SS format (e.g., "14:30:00")
5. Click **Submit**

### Editing a Birthday Entry

1. Go to **Settings** → **Devices & Services**
2. Find your **Birthday Progress** entry
3. Click the entry, then click **Options**
4. Update the birth date or time
5. Click **Submit**

### Removing a Birthday Entry

1. Go to **Settings** → **Devices & Services**
2. Find your **Birthday Progress** entry
3. Click the three dots menu (⋮) → **Delete**

## Sensor Entity

Each birthday entry creates a sensor entity named `sensor.<name>_birthday_progress`.

### State

The sensor's state is the **progress percentage** (0-100) toward the next birthday.

### Attributes

| Attribute | Description | Example |
|-----------|-------------|---------|
| `age_exact` | Exact age with years, days, and time | `27y 153d 04:12:10` |
| `next_birthday` | ISO timestamp of next birthday | `2024-03-15T14:30:00+00:00` |
| `time_until_next` | Human-readable time until next birthday | `45 days, 12:34:56` |
| `progress_percentage` | Progress percentage (same as state) | `12.3456` |
| `name` | Person's name | `John Doe` |
| `birth_date` | Birth date | `1995-03-15` |
| `birth_time` | Birth time (if provided) | `14:30:00` |

## Lovelace Card

### Installation

**For detailed HACS setup, see [HACS_SETUP.md](HACS_SETUP.md)**

Quick steps:
1. In HACS, go to **Frontend**
2. Add the same repository URL with category **Frontend**
3. Install "Birthday Progress Card"
4. Add resource in Lovelace: `/hacsfiles/birthday_progress_card/birthday-progress-card.js`

See the [card README](www/community/birthday_progress_card/README.md) for more details.

### Basic Usage

```yaml
type: custom:birthday-progress-card
entity: sensor.john_birthday_progress
```

### Circular Progress Bar

```yaml
type: custom:birthday-progress-card
entity: sensor.john_birthday_progress
name: John's Birthday
progress_type: circular
```

### Horizontal Progress Bar

```yaml
type: custom:birthday-progress-card
entity: sensor.jane_birthday_progress
progress_type: horizontal
```

### Dashboard Example

```yaml
title: Birthdays
path: birthdays
cards:
  - type: grid
    columns: 2
    square: false
    cards:
      - type: custom:birthday-progress-card
        entity: sensor.john_birthday_progress
        name: John
        progress_type: circular
      - type: custom:birthday-progress-card
        entity: sensor.jane_birthday_progress
        name: Jane
        progress_type: circular
      - type: custom:birthday-progress-card
        entity: sensor.bob_birthday_progress
        name: Bob
        progress_type: horizontal
      - type: custom:birthday-progress-card
        entity: sensor.alice_birthday_progress
        name: Alice
        progress_type: horizontal
```

## Automations

### Birthday Notification Example

Send a notification when someone's birthday is approaching:

```yaml
automation:
  - alias: "Birthday Reminder - 1 Day Before"
    trigger:
      - platform: template
        value_template: >
          {% set next_birthday = state_attr('sensor.john_birthday_progress', 'next_birthday') %}
          {% if next_birthday %}
            {% set days_until = (as_timestamp(next_birthday) - as_timestamp(now())) / 86400 %}
            {{ days_until <= 1 and days_until > 0 }}
          {% endif %}
    condition:
      - condition: time
        after: "08:00:00"
        before: "09:00:00"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "🎂 Birthday Reminder"
          message: "John's birthday is tomorrow!"
          data:
            actions:
              - action: "VIEW"
                title: "View Details"
```

### Birthday Automation with TTS

Announce the birthday with text-to-speech:

```yaml
automation:
  - alias: "Happy Birthday Announcement"
    trigger:
      - platform: state
        entity_id: sensor.john_birthday_progress
        to: "0"
        for:
          hours: 0
          minutes: 0
          seconds: 1
    action:
      - service: tts.google_translate_say
        data:
          entity_id: media_player.living_room
          message: "Happy Birthday to John! Today is John's special day!"
```

### Birthday Countdown Display

Show countdown in a persistent notification:

```yaml
script:
  show_birthday_countdown:
    sequence:
      - service: persistent_notification.create
        data:
          title: "Birthday Countdown"
          message: >
            {% set attrs = state_attr('sensor.john_birthday_progress', 'time_until_next') %}
            {{ attrs }}
          notification_id: birthday_countdown
```

## Advanced Usage

### Template Sensors

Create additional derived sensors:

```yaml
template:
  - sensor:
      - name: "John Age in Years"
        state: >
          {% set age = state_attr('sensor.john_birthday_progress', 'age_exact') %}
          {{ age.split('y')[0] if 'y' in age else '0' }}
        unit_of_measurement: "years"
      
      - name: "John Days Until Birthday"
        state: >
          {% set time_until = state_attr('sensor.john_birthday_progress', 'time_until_next') %}
          {{ time_until.split(' days')[0] if 'days' in time_until else '0' }}
        unit_of_measurement: "days"
```

### History Graph

Track progress over time:

```yaml
type: history-graph
entities:
  - sensor.john_birthday_progress
hours_to_show: 168
refresh_interval: 60
```

## Troubleshooting

### Entity Not Found

- Ensure the integration is properly installed
- Check that you've added a birthday entry through Config Flow
- Restart Home Assistant after installation

### Progress Not Updating

- The sensor updates every second automatically
- Check the entity's state in Developer Tools → States
- Verify the birth date/time is correct in the integration settings

### Card Not Displaying

- Ensure the card resource is loaded in Lovelace configuration
- Check browser console for JavaScript errors
- Verify the entity ID matches exactly (case-sensitive)

## Development

### Project Structure

```
custom_components/birthday_progress/
├── __init__.py          # Main integration setup
├── manifest.json        # Integration manifest
├── config_flow.py       # Config Flow handlers
├── sensor.py            # Sensor entity implementation
├── const.py             # Constants
├── strings.json         # UI strings
└── translations/
    └── en.json          # English translations

www/community/birthday_progress_card/
├── birthday-progress-card.js  # Lovelace card component
└── README.md                  # Card documentation
```

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

- Built for Home Assistant
- Uses LitElement for the Lovelace card
- Inspired by the need for better birthday tracking in home automation

## Support

For issues, feature requests, or questions:
- Open an issue on GitHub
- Check the documentation
- Join the Home Assistant community forums

---

**Made with ❤️ for the Home Assistant community**

