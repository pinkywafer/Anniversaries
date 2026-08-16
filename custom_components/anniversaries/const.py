""" Constants """
from typing import Optional
import voluptuous as vol
from datetime import datetime
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_NAME


# Base component constants
DOMAIN = "anniversaries"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "6.0.1g"
PLATFORM = "sensor"
ISSUE_URL = "https://github.com/pinkywafer/Anniversaries/issues"
ATTRIBUTION = "Sensor data calculated by Anniversaries Integration"

CALENDAR_NAME = "Anniversaries"
SENSOR_PLATFORM = "sensor"
CALENDAR_PLATFORM = "calendar"

ATTR_YEARS_NEXT = "years_at_next_anniversary"
ATTR_YEARS_CURRENT = "current_years"
ATTR_DATE = "date"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"

# Configuration
CONF_SENSOR = "sensor"
CONF_ENABLED = "enabled"
CONF_DATE = "date"
CONF_DATE_TEMPLATE = "date_template"
CONF_ICON_NORMAL = "icon_normal"
CONF_ICON_TODAY = "icon_today"
CONF_ICON_SOON = "icon_soon"
CONF_DATE_FORMAT = "date_format" # Deprecated
CONF_SENSORS = "sensors"
CONF_SOON = "days_as_soon"
CONF_HALF_ANNIVERSARY = "show_half_anniversary"
CONF_UNIT_OF_MEASUREMENT = "unit_of_measurement"
CONF_ID_PREFIX = "id_prefix"
CONF_ONE_TIME = "one_time"
CONF_COUNT_UP = "count_up"
CONF_CALENDAR_TYPE = "calendar_type"
CONF_EVENT_TYPE = "event_type"
CONF_DATE_EXCLUSION_ERROR = "Configuration cannot include both `date` and `date_template`. configure ONLY ONE"
CONF_DATE_REQD_ERROR = "Either `date` or `date_template` is Required"

# Calendar Types
CALENDAR_TYPE_GREGORIAN = "gregorian"
CALENDAR_TYPE_HEBREW = "hebrew"

# Event Types
EVENT_TYPE_BIRTHDAY = "birthday"
EVENT_TYPE_ANNIVERSARY = "anniversary"
EVENT_TYPE_YAHRZEIT = "yahrzeit"
EVENT_TYPE_BAR_BAT_MITZVAH = "bar_bat_mitzvah"

# Event Type Options (for selectors)
EVENT_TYPE_OPTIONS = [
    EVENT_TYPE_BIRTHDAY,
    EVENT_TYPE_ANNIVERSARY,
    EVENT_TYPE_YAHRZEIT,
    EVENT_TYPE_BAR_BAT_MITZVAH,
]

# Calendar Type Options (for selectors)
CALENDAR_TYPE_OPTIONS = [
    CALENDAR_TYPE_GREGORIAN,
    CALENDAR_TYPE_HEBREW,
]

# Defaults
DEFAULT_NAME = DOMAIN
DEFAULT_ICON_NORMAL = "mdi:calendar-blank"
DEFAULT_ICON_TODAY = "mdi:calendar-star"
DEFAULT_ICON_SOON = "mdi:calendar"

# Event type specific icons
EVENT_TYPE_ICONS = {
    EVENT_TYPE_BIRTHDAY: {
        "normal": "mdi:cake",
        "today": "mdi:party-popper",
        "soon": "mdi:cake-variant",
    },
    EVENT_TYPE_ANNIVERSARY: {
        "normal": "mdi:heart",
        "today": "mdi:heart-multiple",
        "soon": "mdi:calendar-heart",
    },
    EVENT_TYPE_YAHRZEIT: {
        "normal": "mdi:candle",
        "today": "mdi:candle",
        "soon": "mdi:candle",
    },
    EVENT_TYPE_BAR_BAT_MITZVAH: {
        "normal": "mdi:star-of-david",
        "today": "mdi:party-popper",
        "soon": "mdi:star-of-david",
    },
}
DEFAULT_DATE_FORMAT = "%Y-%m-%d" # Deprecated
DEFAULT_SOON = 1
DEFAULT_HALF_ANNIVERSARY = False
DEFAULT_UNIT_OF_MEASUREMENT = "Days"
DEFAULT_ID_PREFIX = "anniversary_"
DEFAULT_ONE_TIME = False
DEFAULT_COUNT_UP = False
DEFAULT_CALENDAR_TYPE = CALENDAR_TYPE_GREGORIAN
DEFAULT_EVENT_TYPE = EVENT_TYPE_BIRTHDAY

ICON = DEFAULT_ICON_NORMAL

def check_date(value):
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return value
    except ValueError:
        pass
    try:
        datetime.strptime(value, "%m-%d")
        return value
    except ValueError:
        raise vol.Invalid(f"Invalid date: {value}")

def validate_hebrew_date(value):
    """Validate Hebrew date format and return it if valid."""
    try:
        from hdate import HebrewDate
    except ImportError:
        raise vol.Invalid("hdate library not available for Hebrew calendar support")
    
    # Try format: DD-MM-YYYY (Hebrew date)
    try:
        parts = value.split("-")
        if len(parts) == 3:
            day = int(parts[0])
            month = int(parts[1])
            year = int(parts[2])
            # Validate by creating HebrewDate object
            HebrewDate(year=year, month=month, day=day)
            return value
    except (ValueError, AttributeError):
        pass
    
    # Try format: DD-MM (Hebrew date without year)
    try:
        parts = value.split("-")
        if len(parts) == 2:
            day = int(parts[0])
            month = int(parts[1])
            # Validate month is in valid range (1-14 for hdate library)
            if 1 <= month <= 14 and 1 <= day <= 30:
                return value
    except (ValueError, AttributeError):
        pass
    
    # Try format: "DD MonthName YYYY" or "DD MonthName" (e.g., "15 Adar 5745")
    try:
        parts = value.split()
        if len(parts) >= 2:
            day = int(parts[0])
            month_name = parts[1]
            year = None
            
            # Handle "Adar I" and "Adar II" with space (e.g., "15 Adar I 5765" or "15 Adar II")
            if len(parts) >= 3 and parts[1].lower() == 'adar' and parts[2].lower() in ('i', 'ii', '1', '2', 'א', 'ב'):
                month_name = parts[1] + ' ' + parts[2]  # Combine "Adar" + "I" or "II"
                if len(parts) == 4:
                    year = int(parts[3])
            elif len(parts) == 3:
                year = int(parts[2])
            
            # Map month names to numbers (case-insensitive, supporting both Hebrew and English transliterations)
            # Using hdate library month numbering: Tishrei=1, ..., Adar=6, Adar_I=7, Adar_II=8, Nisan=9, ..., Elul=14
            month_map = {
                "tishrei": 1, "תשרי": 1,
                "cheshvan": 2, "marcheshvan": 2, "חשוון": 2, "מרחשוון": 2,
                "kislev": 3, "כסלו": 3,
                "tevet": 4, "טבת": 4,
                "shevat": 5, "shvat": 5, "שבט": 5,
                "adar": 6, "אדר": 6,
                "adar1": 7, "adar_i": 7, "adar i": 7, "אדר א": 7,
                "adar2": 8, "adar_ii": 8, "adar ii": 8, "אדר ב": 8,
                "nisan": 9, "ניסן": 9,
                "iyar": 10, "אייר": 10,
                "sivan": 11, "סיוון": 11,
                "tammuz": 12, "תמוז": 12,
                "av": 13, "אב": 13,
                "elul": 14, "אלול": 14,
            }
            
            # Convert month name to lowercase for case-insensitive matching
            month_name_lower = month_name.lower()
            month_num = month_map.get(month_name_lower)
            if month_num and year:
                # Validate by creating HebrewDate object
                HebrewDate(year=year, month=month_num, day=day)
                return value
            elif month_num and not year:
                # Valid month and day without year
                if 1 <= day <= 30:
                    return value
    except (ValueError, KeyError, AttributeError):
        pass
    
    raise vol.Invalid(f"Invalid Hebrew date: {value}. Use format DD-MM-YYYY, DD-MM, or 'DD MonthName YYYY'")

DATE_SCHEMA = vol.Schema(
    {
        vol.Required(
            vol.Any(CONF_DATE,CONF_DATE_TEMPLATE,msg=CONF_DATE_REQD_ERROR)
        ): object
    }, extra=vol.ALLOW_EXTRA
)

SENSOR_CONFIG_SCHEMA = vol.All(
    # Deprecated - will be removed in future version
    cv.deprecated(CONF_DATE_FORMAT),
    vol.Schema(
        {
            vol.Required(CONF_NAME): cv.string,
            vol.Exclusive(CONF_DATE, CONF_DATE, msg=CONF_DATE_EXCLUSION_ERROR): cv.string,
            vol.Exclusive(CONF_DATE_TEMPLATE, CONF_DATE, msg=CONF_DATE_EXCLUSION_ERROR): cv.string,
            vol.Optional(CONF_CALENDAR_TYPE, default=DEFAULT_CALENDAR_TYPE): vol.In(CALENDAR_TYPE_OPTIONS),
            vol.Optional(CONF_EVENT_TYPE, default=DEFAULT_EVENT_TYPE): vol.In(EVENT_TYPE_OPTIONS),
            vol.Optional(CONF_SOON, default=DEFAULT_SOON): cv.positive_int,
            vol.Optional(CONF_ICON_NORMAL, default=DEFAULT_ICON_NORMAL): cv.icon,
            vol.Optional(CONF_ICON_TODAY, default=DEFAULT_ICON_TODAY): cv.icon,
            vol.Optional(CONF_ICON_SOON, default=DEFAULT_ICON_SOON): cv.icon,
            vol.Optional(CONF_DATE_FORMAT, default=DEFAULT_DATE_FORMAT): cv.string,
            vol.Optional(CONF_HALF_ANNIVERSARY, default=DEFAULT_HALF_ANNIVERSARY): cv.boolean,
            vol.Optional(CONF_UNIT_OF_MEASUREMENT, default=DEFAULT_UNIT_OF_MEASUREMENT): cv.string,
            vol.Optional(CONF_ID_PREFIX, default=DEFAULT_ID_PREFIX): cv.string,
            vol.Optional(CONF_ONE_TIME, default=DEFAULT_ONE_TIME): cv.boolean,
            vol.Optional(CONF_COUNT_UP, default=DEFAULT_COUNT_UP): cv.boolean,
        }
    )
)

SENSOR_SCHEMA = vol.All(SENSOR_CONFIG_SCHEMA, DATE_SCHEMA)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {vol.Optional(CONF_SENSORS): vol.All(cv.ensure_list, [SENSOR_SCHEMA])}
        )
    },
    extra=vol.ALLOW_EXTRA,
)
