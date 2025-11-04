# Birthday Progress Card

A custom Lovelace card for displaying birthday information in a clean, two-section layout showing time since birth and time until next birthday.

## Installation

### HACS (Recommended)

1. Install HACS if you haven't already
2. Go to HACS → Frontend
3. Click the three dots menu (⋮) → Custom repositories
4. Add this repository
5. Search for "Birthday Progress Card" and install it
6. Refresh your browser

### Manual Installation

1. Copy the `birthday-progress-card.js` file to your `www/community/birthday_progress_card/` directory
2. Add the resource to your Lovelace configuration:

```yaml
resources:
  - url: /local/community/birthday_progress_card/birthday-progress-card.js
    type: module
```

## Usage

### Basic Example

```yaml
type: custom:birthday-progress-card
entity: sensor.john_birthday_progress
```

### With Custom Next Birthday Title

```yaml
type: custom:birthday-progress-card
entity: sensor.milan_birthday_progress
next_birthday_title: "Milan's nächster Geburtstag"
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `entity` | string | **Required** | Entity ID of the birthday progress sensor |
| `name` | string | Optional | Custom name to display (overrides entity name) |
| `next_birthday_title` | string | `"{name}'s Next Birthday"` | Custom title for next birthday section |

## Features

- **Two-Section Layout**: Clean design showing birth information and next birthday countdown
- **Detailed Time Breakdown**: Shows years, months, weeks, days, hours, minutes, and seconds
- **Real-time Updates**: Automatically updates every second as the sensor changes
- **Theme Support**: Automatically adapts to light/dark mode
- **Responsive Design**: Works on mobile and desktop
- **Date/Time Display**: Shows birth date/time and next birthday date/time

## Card Layout

The card displays two sections:

**Top Section:**
- Person's name
- Birth date and time (DD/MM/YYYY HH:MM:SS)
- Time since birth (detailed breakdown)

**Bottom Section:**
- Next birthday title (customizable)
- Next birthday date and time
- Time until next birthday (detailed breakdown)

## Example

```yaml
type: custom:birthday-progress-card
entity: sensor.milan_birthday_progress
next_birthday_title: "Milan's nächster Geburtstag"
```

This displays:
- **Milan**
- **23/08/2017 20:27:00**
- Time since event: 8 years, 2 months, 1 week, 4 days, 23 hours, 34 minutes, and 8 seconds
- **Milan's nächster Geburtstag**
- **23/08/2026 20:27:00**
- Time until event: 9 months, 2 weeks, 5 days, 25 minutes, and 52 seconds

## Support

For issues and feature requests, please visit the [GitHub repository](https://github.com/yourusername/birthday_progress).

