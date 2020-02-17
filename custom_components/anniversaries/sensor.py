""" sensor """

from homeassistant.helpers.entity import Entity
import logging
from datetime import datetime, date, timedelta
from homeassistant.core import HomeAssistant, State

from homeassistant.const import (
    CONF_NAME,
)

from .const import (
    ATTRIBUTION,
    DEFAULT_NAME,
    DOMAIN,
    CONF_SENSOR,
    CONF_ENABLED,
    CONF_ICON_NORMAL,
    CONF_ICON_TODAY,
    CONF_ICON_SOON,
    CONF_DATE,
    CONF_DATE_FORMAT,
    CONF_SOON,
)

ATTR_YEARS_NEXT = "years_at_next_anniversary"
ATTR_YEARS_CURRENT = "current_years"
ATTR_DATE = "date"
ATTR_WEEKS = "weeks_remaining"

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Setup the sensor platform."""
    async_add_entities([anniversaries(hass, discovery_info)], True)

async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup sensor platform."""
    async_add_devices([anniversaries(hass, config_entry.data)], True)


class anniversaries(Entity):
    def __init__(self, hass, config):
        """Initialize the sensor."""
        self.config = config
        self._name = config.get(CONF_NAME)
        self._unknown_year = False
        self._date = ""
        try:
            self._date = datetime.strptime(config.get(CONF_DATE), "%Y-%m-%d")
        except:
            self._date = datetime.strptime(str(date.today().year) + "-" + config.get(CONF_DATE),  "%Y-%m-%d")
            self._unknown_year = True
        self._icon_normal = config.get(CONF_ICON_NORMAL)
        self._icon_today = config.get(CONF_ICON_TODAY)
        self._icon_soon = config.get(CONF_ICON_SOON)
        self._soon = config.get(CONF_SOON)
        self._date_format = config.get(CONF_DATE_FORMAT)
        self._icon = self._icon_normal
        self._years_next = 0
        self._years_current = 0
        self._state = 0
        self._weeks_remaining = 0

    @property
    def unique_id(self):
        """Return a unique ID to use for this sensor."""
        return self.config.get("unique_id", None)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the name of the sensor."""
        return self._state

    @property 
    def device_state_attributes(self):
        """Return the state attributes."""
        res = {}
        if not self._unknown_year:
            res[ATTR_YEARS_NEXT] = self._years_next
            res[ATTR_YEARS_CURRENT] = self._years_current
        res[ATTR_DATE] = datetime.strftime(self._date,self._date_format)
        res[ATTR_WEEKS] = self._weeks_remaining
        return res

    @property
    def icon(self):
        return self._icon
    
    @property
    def unit_of_measurement(self):
        """Return the unit this state is expressed in."""
        if self._state == 1:
            return "day"
        return "days"

    async def async_update(self):
        """update the sensor"""
        today = date.today()
        nextDate = date(today.year, self._date.month, self._date.day)
        if today < self._date.date():
            nextDate = self._date.date()
        daysRemaining = 0
        years = today.year - self._date.year
        if today < nextDate:
            daysRemaining = (nextDate - today).days
        elif today == nextDate:
            daysRemaining = 0
            years = years + 1
        elif today > nextDate:
            nextDate = date(today.year + 1, self._date.month, self._date.day)
            daysRemaining = (nextDate - today).days
            years = years + 1
            if self._unknown_year:
                self._date = datetime(nextDate.year, nextDate.month, nextDate.day)

        if daysRemaining == 0:
            self._icon = self._icon_today
        elif daysRemaining <= self._soon:
            self._icon = self._icon_soon
        else:
            self._icon = self._icon_normal
        self._state = daysRemaining
        self._years_next = years
        self._years_current = years - 1
        self._weeks_remaining = int(daysRemaining / 7)
