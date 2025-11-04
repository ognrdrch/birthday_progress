"""
Config Flow for Birthday Progress Integration.

Handles the setup flow for adding, editing, and removing birthday entries
through the Home Assistant UI.
"""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util import dt as dt_util

from .const import CONF_BIRTH_DATE, CONF_BIRTH_TIME, CONF_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)


def parse_german_date(date_str: str) -> str:
    """
    Parse German date format (DD.MM.YYYY) and convert to YYYY-MM-DD.

    Args:
        date_str: Date string in DD.MM.YYYY or YYYY-MM-DD format

    Returns:
        Date string in YYYY-MM-DD format

    Raises:
        ValueError: If date format is invalid
    """
    date_str = date_str.strip()
    
    # Try German format DD.MM.YYYY first
    if "." in date_str and len(date_str.split(".")) == 3:
        try:
            parts = date_str.split(".")
            if len(parts) != 3:
                raise ValueError("Invalid date format")
            day, month, year = parts
            # Convert to YYYY-MM-DD
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        except (ValueError, IndexError) as err:
            raise ValueError(f"Invalid German date format (DD.MM.YYYY): {err}") from err
    
    # Try ISO format YYYY-MM-DD (backwards compatibility)
    if "-" in date_str and len(date_str.split("-")) == 3:
        parts = date_str.split("-")
        if len(parts) == 3 and len(parts[0]) == 4:
            return date_str  # Already in YYYY-MM-DD format
    
    raise ValueError("Date must be in DD.MM.YYYY or YYYY-MM-DD format")


def validate_date(date_str: str) -> str:
    """
    Validate date string format (DD.MM.YYYY or YYYY-MM-DD) and convert to YYYY-MM-DD.

    Args:
        date_str: Date string to validate

    Returns:
        Date string in YYYY-MM-DD format

    Raises:
        ValueError: If date format is invalid or date is in the future
    """
    try:
        # Convert to YYYY-MM-DD format
        iso_date = parse_german_date(date_str)
        
        # Parse the ISO date
        date_obj = dt_util.parse_date(iso_date)
        if date_obj is None:
            raise ValueError("Invalid date format")
        
        # Check if date is in the future
        if date_obj > dt_util.now().date():
            raise ValueError("Birth date cannot be in the future")
        
        return iso_date
    except (ValueError, TypeError) as err:
        raise ValueError(f"Invalid date format: {err}") from err


def validate_time(time_str: str | None) -> bool:
    """
    Validate time string format (HH:MM:SS or HH:MM).

    Args:
        time_str: Time string to validate, or None

    Returns:
        True if valid or None, raises ValueError otherwise
    """
    if time_str is None or time_str == "":
        return True

    try:
        time_obj = dt_util.parse_time(time_str)
        if time_obj is None:
            raise ValueError("Invalid time format")
        return True
    except (ValueError, TypeError) as err:
        raise ValueError(f"Invalid time format: {err}") from err


class BirthdayProgressConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """
    Handle a config flow for Birthday Progress.
    """

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """
        Handle the initial step (user form).

        Args:
            user_input: User input from the form

        Returns:
            Flow result with next step or form
        """
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Validate name
                name = user_input.get(CONF_NAME, "").strip()
                if not name:
                    errors[CONF_NAME] = "name_required"

                # Validate date and convert to ISO format
                birth_date = user_input.get(CONF_BIRTH_DATE, "")
                if not birth_date:
                    errors[CONF_BIRTH_DATE] = "date_required"
                else:
                    try:
                        birth_date = validate_date(birth_date)  # Returns ISO format
                    except ValueError:
                        errors[CONF_BIRTH_DATE] = "invalid_date"

                # Validate time (optional)
                birth_time = user_input.get(CONF_BIRTH_TIME, "")
                if birth_time:
                    validate_time(birth_time)
                else:
                    birth_time = None

                # Check if entry already exists with this name
                await self.async_set_unique_id(name)
                self._abort_if_unique_id_configured()

                if not errors:
                    # Create the config entry
                    return self.async_create_entry(
                        title=name,
                        data={
                            CONF_NAME: name,
                            CONF_BIRTH_DATE: birth_date,
                            CONF_BIRTH_TIME: birth_time,
                        },
                    )

            except ValueError as err:
                _LOGGER.error("Validation error: %s", err)
                if "date" in str(err).lower():
                    errors[CONF_BIRTH_DATE] = "invalid_date"
                elif "time" in str(err).lower():
                    errors[CONF_BIRTH_TIME] = "invalid_time"
                elif "future" in str(err).lower():
                    errors[CONF_BIRTH_DATE] = "future_date"
            except Exception as err:
                _LOGGER.exception("Unexpected error: %s", err)
                errors["base"] = "unknown"

        # Show form
        # Convert stored ISO date back to German format for display
        display_date = ""
        if user_input and user_input.get(CONF_BIRTH_DATE):
            stored_date = user_input.get(CONF_BIRTH_DATE)
            # If it's in ISO format, convert to German format for display
            if "-" in stored_date and len(stored_date.split("-")) == 3:
                parts = stored_date.split("-")
                if len(parts[0]) == 4:  # YYYY-MM-DD
                    display_date = f"{parts[2]}.{parts[1]}.{parts[0]}"
                else:
                    display_date = stored_date
            else:
                display_date = stored_date
        
        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=user_input.get(CONF_NAME, "") if user_input else ""): str,
                vol.Required(CONF_BIRTH_DATE, default=display_date, description={"suffix": "Format: DD.MM.YYYY"}): str,
                vol.Optional(CONF_BIRTH_TIME, default=user_input.get(CONF_BIRTH_TIME, "") if user_input else ""): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_import(self, import_info: dict[str, Any]) -> FlowResult:
        """
        Handle import from configuration.yaml (for backwards compatibility).

        Args:
            import_info: Imported configuration data

        Returns:
            Flow result
        """
        return await self.async_step_user(import_info)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> BirthdayProgressOptionsFlow:
        """
        Get the options flow for this handler.

        Args:
            config_entry: Configuration entry

        Returns:
            Options flow handler
        """
        return BirthdayProgressOptionsFlow(config_entry)


class BirthdayProgressOptionsFlow(config_entries.OptionsFlow):
    """
    Handle options flow for Birthday Progress entries.
    """

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """
        Initialize options flow.

        Args:
            config_entry: Configuration entry being edited
        """
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """
        Handle options flow initialization.

        Args:
            user_input: User input from the form

        Returns:
            Flow result with next step or form
        """
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Validate date and convert to ISO format
                birth_date = user_input.get(CONF_BIRTH_DATE, "")
                if not birth_date:
                    errors[CONF_BIRTH_DATE] = "date_required"
                else:
                    try:
                        birth_date = validate_date(birth_date)  # Returns ISO format
                    except ValueError:
                        errors[CONF_BIRTH_DATE] = "invalid_date"

                # Validate time (optional)
                birth_time = user_input.get(CONF_BIRTH_TIME, "")
                if birth_time:
                    validate_time(birth_time)
                else:
                    birth_time = None

                if not errors:
                    # Update the config entry
                    self.hass.config_entries.async_update_entry(
                        self.config_entry,
                        data={
                            CONF_NAME: self.config_entry.data.get(CONF_NAME),
                            CONF_BIRTH_DATE: birth_date,
                            CONF_BIRTH_TIME: birth_time,
                        },
                    )
                    return self.async_create_entry(title="", data={})

            except ValueError as err:
                _LOGGER.error("Validation error: %s", err)
                if "date" in str(err).lower():
                    errors[CONF_BIRTH_DATE] = "invalid_date"
                elif "time" in str(err).lower():
                    errors[CONF_BIRTH_TIME] = "invalid_time"
                elif "future" in str(err).lower():
                    errors[CONF_BIRTH_DATE] = "future_date"
            except Exception as err:
                _LOGGER.exception("Unexpected error: %s", err)
                errors["base"] = "unknown"

        # Show form with current values
        current_data = self.config_entry.data
        # Convert stored ISO date back to German format for display
        stored_date = current_data.get(CONF_BIRTH_DATE, "")
        display_date = ""
        if stored_date and "-" in stored_date:
            parts = stored_date.split("-")
            if len(parts) == 3 and len(parts[0]) == 4:  # YYYY-MM-DD
                display_date = f"{parts[2]}.{parts[1]}.{parts[0]}"
            else:
                display_date = stored_date
        else:
            display_date = stored_date
        
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_BIRTH_DATE, default=display_date, description={"suffix": "Format: DD.MM.YYYY"}
                ): str,
                vol.Optional(
                    CONF_BIRTH_TIME, default=current_data.get(CONF_BIRTH_TIME, "")
                ): str,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
        )

