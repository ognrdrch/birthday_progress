"""
Sensor platform for Birthday Progress Integration.

Provides sensor entities that calculate and display birthday-related metrics.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from . import BirthdayProgressCoordinator
from .const import (
    ATTR_AGE_EXACT,
    ATTR_NEXT_BIRTHDAY,
    ATTR_PROGRESS_PERCENTAGE,
    ATTR_TIME_UNTIL_NEXT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """
    Set up Birthday Progress sensors from a config entry.

    Args:
        hass: Home Assistant instance
        entry: Configuration entry
        async_add_entities: Callback to add entities
    """
    coordinator: BirthdayProgressCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([BirthdayProgressSensor(coordinator, entry)])


class BirthdayProgressSensor(
    CoordinatorEntity[BirthdayProgressCoordinator], SensorEntity
):
    """
    Sensor entity for Birthday Progress.

    Calculates and displays:
    - Current age (exact, to the second)
    - Time until next birthday
    - Progress percentage toward next birthday
    """

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "%"

    def __init__(
        self, coordinator: BirthdayProgressCoordinator, entry: ConfigEntry
    ) -> None:
        """
        Initialize the Birthday Progress sensor.

        Args:
            coordinator: Data update coordinator
            entry: Configuration entry
        """
        super().__init__(coordinator)
        self._entry = entry
        self._name = entry.data.get("name", "Unknown")
        self._birth_date_str = entry.data.get("birth_date")
        self._birth_time_str = entry.data.get("birth_time")

        # Parse birth datetime
        self._birth_datetime = self._parse_birth_datetime()

        # Entity attributes
        # Set name to generate entity_id: sensor.<name>_birthday_progress
        # Home Assistant will slugify the name to create the entity_id
        self._attr_name = f"{self._name} Birthday Progress"
        self._attr_unique_id = f"{entry.entry_id}_birthday_progress"
        self._attr_icon = "mdi:cake-variant"
        # Entity ID format: sensor.<slugified_name>_birthday_progress

    def _parse_birth_datetime(self) -> datetime:
        """
        Parse birth date and time into a datetime object.

        Returns:
            Datetime object representing birth date/time
        """
        birth_date = dt_util.parse_date(self._birth_date_str)
        if birth_date is None:
            raise ValueError(f"Invalid birth date: {self._birth_date_str}")

        birth_time = None
        if self._birth_time_str:
            birth_time = dt_util.parse_time(self._birth_time_str)
            if birth_time is None:
                _LOGGER.warning(
                    "Invalid birth time format: %s, using midnight", self._birth_time_str
                )

        # Combine date and time, defaulting to midnight if no time provided
        if birth_time is not None:
            return dt_util.as_local(
                datetime.combine(birth_date, birth_time)
            )
        return dt_util.as_local(datetime.combine(birth_date, datetime.min.time()))

    def _calculate_age_exact(self) -> str:
        """
        Calculate exact age as a formatted string.

        Returns:
            Formatted age string (e.g., "27y 153d 04:12:10")
        """
        now = dt_util.now()
        last_birthday = self._calculate_last_birthday()
        
        # Calculate time since last birthday
        time_since_last_birthday = now - last_birthday
        
        # Calculate years by counting birthdays
        years = last_birthday.year - self._birth_datetime.year
        
        # Extract days, hours, minutes, seconds
        days = time_since_last_birthday.days
        hours, remainder = divmod(time_since_last_birthday.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        return f"{years}y {days}d {hours:02d}:{minutes:02d}:{seconds:02d}"

    def _calculate_next_birthday(self) -> datetime:
        """
        Calculate the datetime of the next birthday.

        Returns:
            Datetime of next birthday
        """
        now = dt_util.now()
        current_year = now.year

        # Get birth month and day
        birth_month = self._birth_datetime.month
        birth_day = self._birth_datetime.day

        # Try current year first
        try:
            next_birthday = datetime(
                current_year,
                birth_month,
                birth_day,
                self._birth_datetime.hour,
                self._birth_datetime.minute,
                self._birth_datetime.second,
                tzinfo=self._birth_datetime.tzinfo,
            )
            if next_birthday <= now:
                # Birthday already passed this year, next year
                next_birthday = next_birthday.replace(year=current_year + 1)
        except ValueError:
            # Handle Feb 29 edge case
            if birth_month == 2 and birth_day == 29:
                # Find next valid Feb 29 or use Feb 28
                for year in [current_year, current_year + 1]:
                    try:
                        next_birthday = datetime(
                            year,
                            2,
                            29,
                            self._birth_datetime.hour,
                            self._birth_datetime.minute,
                            self._birth_datetime.second,
                            tzinfo=self._birth_datetime.tzinfo,
                        )
                        if next_birthday > now:
                            break
                    except ValueError:
                        continue
                else:
                    # No valid Feb 29 found, use Feb 28
                    next_birthday = datetime(
                        current_year + 1,
                        2,
                        28,
                        self._birth_datetime.hour,
                        self._birth_datetime.minute,
                        self._birth_datetime.second,
                        tzinfo=self._birth_datetime.tzinfo,
                    )
            else:
                next_birthday = datetime(
                    current_year + 1,
                    birth_month,
                    birth_day,
                    self._birth_datetime.hour,
                    self._birth_datetime.minute,
                    self._birth_datetime.second,
                    tzinfo=self._birth_datetime.tzinfo,
                )

        return dt_util.as_local(next_birthday)

    def _calculate_time_until_next(self) -> str:
        """
        Calculate time until next birthday as formatted string.

        Returns:
            Formatted time string (e.g., "45 days, 12:34:56")
        """
        now = dt_util.now()
        next_birthday = self._calculate_next_birthday()
        time_delta = next_birthday - now

        days = time_delta.days
        hours, remainder = divmod(time_delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        return f"{days} days, {hours:02d}:{minutes:02d}:{seconds:02d}"

    def _calculate_detailed_time_breakdown(self, time_delta: timedelta) -> dict[str, int]:
        """
        Calculate detailed time breakdown: years, months, weeks, days, hours, minutes, seconds.

        Args:
            time_delta: Time delta to break down

        Returns:
            Dictionary with years, months, weeks, days, hours, minutes, seconds
        """
        total_seconds = int(time_delta.total_seconds())
        total_days = time_delta.days

        # Calculate years (approximate)
        years = total_days // 365
        remaining_days = total_days % 365

        # Calculate months (approximate, using 30.44 days per month average)
        months = remaining_days // 30
        remaining_days_after_months = remaining_days % 30

        # Calculate weeks
        weeks = remaining_days_after_months // 7
        days = remaining_days_after_months % 7

        # Calculate hours, minutes, seconds
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        return {
            "years": years,
            "months": months,
            "weeks": weeks,
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
        }

    def _format_detailed_time(self, breakdown: dict[str, int]) -> str:
        """
        Format detailed time breakdown as human-readable string.

        Args:
            breakdown: Dictionary with time components

        Returns:
            Formatted string (e.g., "8 years, 2 months, 1 week, 4 days, 23 hours, 34 minutes, and 8 seconds")
        """
        parts = []
        
        if breakdown["years"] > 0:
            parts.append(f"{breakdown['years']} year{'s' if breakdown['years'] != 1 else ''}")
        if breakdown["months"] > 0:
            parts.append(f"{breakdown['months']} month{'s' if breakdown['months'] != 1 else ''}")
        if breakdown["weeks"] > 0:
            parts.append(f"{breakdown['weeks']} week{'s' if breakdown['weeks'] != 1 else ''}")
        if breakdown["days"] > 0:
            parts.append(f"{breakdown['days']} day{'s' if breakdown['days'] != 1 else ''}")
        if breakdown["hours"] > 0:
            parts.append(f"{breakdown['hours']} hour{'s' if breakdown['hours'] != 1 else ''}")
        if breakdown["minutes"] > 0:
            parts.append(f"{breakdown['minutes']} minute{'s' if breakdown['minutes'] != 1 else ''}")
        if breakdown["seconds"] > 0 or len(parts) == 0:
            parts.append(f"{breakdown['seconds']} second{'s' if breakdown['seconds'] != 1 else ''}")

        if len(parts) == 0:
            return "0 seconds"
        elif len(parts) == 1:
            return parts[0]
        elif len(parts) == 2:
            return f"{parts[0]} and {parts[1]}"
        else:
            return ", ".join(parts[:-1]) + ", and " + parts[-1]

    def _calculate_progress_percentage(self) -> float:
        """
        Calculate progress percentage toward next birthday (0-100).

        Returns:
            Progress percentage as float (0.0-100.0)
        """
        now = dt_util.now()
        next_birthday = self._calculate_next_birthday()

        # Calculate last birthday
        last_birthday = self._calculate_last_birthday()

        # Total time between last and next birthday
        total_time = (next_birthday - last_birthday).total_seconds()

        # Time elapsed since last birthday
        elapsed_time = (now - last_birthday).total_seconds()

        # Calculate percentage
        if total_time > 0:
            progress = (elapsed_time / total_time) * 100.0
            return round(progress, 4)
        return 0.0

    def _calculate_last_birthday(self) -> datetime:
        """
        Calculate the datetime of the last birthday.

        Returns:
            Datetime of last birthday
        """
        now = dt_util.now()
        current_year = now.year

        birth_month = self._birth_datetime.month
        birth_day = self._birth_datetime.day

        # Try current year first
        try:
            last_birthday = datetime(
                current_year,
                birth_month,
                birth_day,
                self._birth_datetime.hour,
                self._birth_datetime.minute,
                self._birth_datetime.second,
                tzinfo=self._birth_datetime.tzinfo,
            )
            if last_birthday > now:
                # Birthday hasn't occurred this year yet, last year
                last_birthday = last_birthday.replace(year=current_year - 1)
        except ValueError:
            # Handle Feb 29 edge case
            if birth_month == 2 and birth_day == 29:
                # Find last valid Feb 29 or use Feb 28
                for year in range(current_year, current_year - 2, -1):
                    try:
                        last_birthday = datetime(
                            year,
                            2,
                            29,
                            self._birth_datetime.hour,
                            self._birth_datetime.minute,
                            self._birth_datetime.second,
                            tzinfo=self._birth_datetime.tzinfo,
                        )
                        if last_birthday <= now:
                            break
                    except ValueError:
                        continue
                else:
                    # No valid Feb 29 found, use Feb 28
                    last_birthday = datetime(
                        current_year - 1,
                        2,
                        28,
                        self._birth_datetime.hour,
                        self._birth_datetime.minute,
                        self._birth_datetime.second,
                        tzinfo=self._birth_datetime.tzinfo,
                    )
            else:
                last_birthday = datetime(
                    current_year - 1,
                    birth_month,
                    birth_day,
                    self._birth_datetime.hour,
                    self._birth_datetime.minute,
                    self._birth_datetime.second,
                    tzinfo=self._birth_datetime.tzinfo,
                )

        return dt_util.as_local(last_birthday)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()

    @property
    def native_value(self) -> float:
        """
        Return the current progress percentage.

        Returns:
            Progress percentage (0-100)
        """
        return self._calculate_progress_percentage()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """
        Return extra state attributes.

        Returns:
            Dictionary of extra attributes
        """
        now = dt_util.now()
        next_birthday = self._calculate_next_birthday()
        last_birthday = self._calculate_last_birthday()
        
        # Calculate time since birth
        time_since_birth = now - self._birth_datetime
        time_since_breakdown = self._calculate_detailed_time_breakdown(time_since_birth)
        
        # Calculate time until next birthday
        time_until_next = next_birthday - now
        time_until_breakdown = self._calculate_detailed_time_breakdown(time_until_next)
        
        return {
            ATTR_AGE_EXACT: self._calculate_age_exact(),
            ATTR_NEXT_BIRTHDAY: next_birthday.isoformat(),
            ATTR_TIME_UNTIL_NEXT: self._calculate_time_until_next(),
            ATTR_PROGRESS_PERCENTAGE: self._calculate_progress_percentage(),
            "name": self._name,
            "birth_date": self._birth_date_str,
            "birth_time": self._birth_time_str or "Not specified",
            "birth_datetime": self._birth_datetime.strftime("%d/%m/%Y %H:%M:%S"),
            "next_birthday_datetime": next_birthday.strftime("%d/%m/%Y %H:%M:%S"),
            "time_since_birth": self._format_detailed_time(time_since_breakdown),
            "time_until_next_detailed": self._format_detailed_time(time_until_breakdown),
        }

    @property
    def device_info(self) -> DeviceInfo:
        """
        Return device information.

        Returns:
            Device information dictionary
        """
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self._name,
            manufacturer="Birthday Progress",
            model="Birthday Tracker",
        )

