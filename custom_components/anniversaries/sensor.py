"""Platform for sensor integration."""

import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_NAME,
)

from homeassistant.helpers.entity import Entity
from datetime import datetime, date, timedelta

CONF_DATE = "date"
ATTR_YEARS = "years"
ATTR_DATE = "date"
CONF_ICON_NORMAL = "icon_normal"
CONF_ICON_TODAY = "icon_today"
CONF_ICON_TOMORROW = "icon_tomorrow"

DEFAULT_ICON_NORMAL = "mdi:calendar-blank"
DEFAULT_ICON_TODAY = "mdi:calendar-star"
DEFAULT_ICON_TOMORROW = "mdi:calendar"


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_DATE): cv.date,
    vol.Required(CONF_NAME): cv.string,
    vol.Optional(CONF_ICON_NORMAL, default=DEFAULT_ICON_NORMAL): cv.icon,
    vol.Optional(CONF_ICON_TODAY, default=DEFAULT_ICON_TODAY): cv.icon,
    vol.Optional(CONF_ICON_TOMORROW, default=DEFAULT_ICON_TOMORROW): cv.icon,

})

TRACKABLE_DOMAINS = ["sensor"]

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Setup the sensor platform."""
    async_add_entities([anniversaries(config)],True)  

class anniversaries(Entity):
    def __init__(self, config):
        """Initialize the sensor."""
        self._name = config.get(CONF_NAME)
        self._date = config.get(CONF_DATE)
        self._icon_normal = config.get(CONF_ICON_NORMAL)
        self._icon_today = config.get(CONF_ICON_TODAY)
        self._icon_tomorrow = config.get(CONF_ICON_TOMORROW)
        self._icon = self._icon_normal
        self._years = 0
        self._state = 0

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
        res[ATTR_YEARS] = self._years
        res[ATTR_DATE] = datetime.strftime(self._date,"%Y-%m-%d")
        return res

    @property
    def icon(self):
        return self._icon

    async def async_update(self):
        today = date.today()
        nextDate = date(today.year, self._date.month, self._date.day)
        daysRemaining = 0
        years = today.year - self._date.year
        if today < nextDate:
            daysRemaining = (nextDate - today).days
        elif today == nextDate:
            daysRemaining = 0
        elif today > nextDate:
            nextDate = date(today.year + 1, self._date.month, self._date.day)
            daysRemaining = (nextDate - today).days
            years = years + 1

        if daysRemaining == 0:
            self._icon = self._icon_today
        elif daysRemaining == 1:
            self._icon = self._icon_tomorrow
        else:
            self._icon = self._icon_normal
        self._state = daysRemaining
        self._years = years