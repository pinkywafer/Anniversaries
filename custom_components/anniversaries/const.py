""" Constants """
import voluptuous as vol
from datetime import datetime, date
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_NAME


# Base component constants
DOMAIN = "anniversaries"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "1.0.0"
PLATFORM = "sensor"
ISSUE_URL = "https://github.com/pinkywafer/Anniversaries/issues"
ATTRIBUTION = "Data from this is provided by Anniversaries"

ATTR_YEARS_NEXT = "years_at_next_anniversary"
ATTR_YEARS_CURRENT = "current_years"
ATTR_DATE = "date"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"

# Configuration
CONF_SENSOR = "sensor"
CONF_ENABLED = "enabled"
CONF_DATE = "date"
CONF_ICON_NORMAL = "icon_normal"
CONF_ICON_TODAY = "icon_today"
CONF_ICON_SOON = "icon_soon"
CONF_DATE_FORMAT = "date_format"
CONF_SENSORS = "sensors"
CONF_SOON = "days_as_soon"

# Defaults
DEFAULT_NAME = DOMAIN

# Icons
DEFAULT_ICON_NORMAL = "mdi:calendar-blank"
DEFAULT_ICON_TODAY = "mdi:calendar-star"
DEFAULT_ICON_SOON = "mdi:calendar"
DEFAULT_DATE_FORMAT = "%Y-%m-%d"
ICON = DEFAULT_ICON_NORMAL
DEFAULT_SOON = 1

def check_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date().strftime("%Y-%m-%d")
    except ValueError:
        raise vol.Invalid(f"Invalid date: {value}")


SENSOR_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_DATE): check_date,
        vol.Optional(CONF_SOON, default=DEFAULT_SOON): cv.positive_int,
        vol.Optional(CONF_ICON_NORMAL, default=DEFAULT_ICON_NORMAL): cv.icon,
        vol.Optional(CONF_ICON_TODAY, default=DEFAULT_ICON_TODAY): cv.icon,
        vol.Optional(CONF_ICON_SOON, default=DEFAULT_ICON_SOON): cv.icon,
        vol.Optional(CONF_DATE_FORMAT, default=DEFAULT_DATE_FORMAT): cv.string,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {vol.Optional(CONF_SENSORS): vol.All(cv.ensure_list, [SENSOR_SCHEMA])}
        )
    },
    extra=vol.ALLOW_EXTRA,
)
