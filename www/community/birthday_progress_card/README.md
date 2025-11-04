# Birthday Progress Card

A custom Lovelace card for displaying birthday progress with beautiful circular or horizontal progress bars.

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

### With Custom Name

```yaml
type: custom:birthday-progress-card
entity: sensor.john_birthday_progress
name: John's Birthday
```

### Horizontal Progress Bar

```yaml
type: custom:birthday-progress-card
entity: sensor.jane_birthday_progress
progress_type: horizontal
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `entity` | string | **Required** | Entity ID of the birthday progress sensor |
| `name` | string | Optional | Custom name to display (overrides entity name) |
| `progress_type` | string | `circular` | Type of progress bar: `circular` or `horizontal` |

## Features

- **Circular Progress Bar**: Beautiful animated circular progress indicator
- **Horizontal Progress Bar**: Linear progress bar option
- **Real-time Updates**: Automatically updates as the sensor changes
- **Theme Support**: Automatically adapts to light/dark mode
- **Responsive Design**: Works on mobile and desktop
- **Information Display**: Shows exact age, time until next birthday, and next birthday date

## Screenshots

_Add screenshots here showing the card in action_

## Support

For issues and feature requests, please visit the [GitHub repository](https://github.com/yourusername/birthday_progress).

