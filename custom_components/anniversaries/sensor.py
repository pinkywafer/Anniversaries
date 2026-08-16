""" Sensor """
from dateutil.relativedelta import relativedelta
from datetime import datetime, date

import logging

from homeassistant.helpers.entity import Entity, generate_entity_id
from homeassistant.components.sensor import ENTITY_ID_FORMAT
from homeassistant.helpers import template as templater
import homeassistant.util.dt as dt_util
from .calendar import EntitiesCalendarData
from homeassistant.helpers.discovery import async_load_platform

from homeassistant.const import (
    CONF_NAME,
    ATTR_ATTRIBUTION,
)

try:
    from hdate import HebrewDate, Months
    HDATE_AVAILABLE = True
except ImportError:
    HDATE_AVAILABLE = False

_LOGGER = logging.getLogger(__name__)

from .const import (
    ATTRIBUTION,
    DEFAULT_UNIT_OF_MEASUREMENT,
    CONF_ICON_NORMAL,
    CONF_ICON_TODAY,
    CONF_ICON_SOON,
    CONF_DATE,
    CONF_DATE_TEMPLATE,
    CONF_SOON,
    CONF_HALF_ANNIVERSARY,
    CONF_UNIT_OF_MEASUREMENT,
    CONF_ID_PREFIX,
    CONF_ONE_TIME,
    CONF_COUNT_UP,
    CONF_CALENDAR_TYPE,
    CONF_EVENT_TYPE,
    CALENDAR_TYPE_GREGORIAN,
    CALENDAR_TYPE_HEBREW,
    DEFAULT_CALENDAR_TYPE,
    DEFAULT_EVENT_TYPE,
    EVENT_TYPE_ICONS,
    DOMAIN,
    SENSOR_PLATFORM,
    CALENDAR_PLATFORM,
    CALENDAR_NAME,
)

ATTR_YEARS_NEXT = "years_at_anniversary"
ATTR_YEARS_CURRENT = "current_years"
ATTR_DATE = "date"
ATTR_NEXT_DATE = "next_date"
ATTR_WEEKS = "weeks_remaining"
ATTR_HALF_DATE = "half_anniversary_date"
ATTR_HALF_DAYS = "days_until_half_anniversary"
ATTR_HEBREW_DATE = "hebrew_date"
ATTR_HEBREW_NEXT_DATE = "hebrew_next_date"
ATTR_CALENDAR_TYPE = "calendar_type"
ATTR_EVENT_TYPE = "event_type"
ATTR_ICON = "icon"

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Setup the sensor platform."""
    async_add_entities([anniversaries(hass, discovery_info)], True)

async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup sensor platform."""
    async_add_devices([anniversaries(hass, config_entry.data)], True)

def validate_date(value, calendar_type=CALENDAR_TYPE_GREGORIAN):
    """Validate date based on calendar type."""
    if calendar_type == CALENDAR_TYPE_HEBREW:
        return validate_hebrew_date_sensor(value)
    else:
        # Gregorian validation
        try:
            return datetime.strptime(value, "%Y-%m-%d"), False
        except ValueError:
            pass
        try:
            return datetime.strptime(value, "%m-%d"), True
        except ValueError:
                return "Invalid Date", False

def validate_hebrew_date_sensor(value):
    """Validate and parse Hebrew date."""
    if not HDATE_AVAILABLE:
        _LOGGER.warning(f"hdate library not available for Hebrew date validation: {value}")
        return "Invalid Date", False
    
    _LOGGER.debug(f"Validating Hebrew date: {value}")
    
    try:
        # Try format: DD-MM-YYYY (Hebrew date)
        parts = value.split("-")
        if len(parts) == 3:
            day = int(parts[0])
            month = int(parts[1])
            year = int(parts[2])
            hebrew_date = HebrewDate(year=year, month=month, day=day)
            # Convert to Gregorian datetime
            greg_date = hebrew_date.to_gdate()
            greg_datetime = datetime(greg_date.year, greg_date.month, greg_date.day)
            _LOGGER.debug(f"Successfully parsed Hebrew date (DD-MM-YYYY): {value} -> {greg_datetime}")
            return greg_datetime, False  # False = year is known
        
        # Try format: DD-MM (Hebrew date without year)
        if len(parts) == 2:
            day = int(parts[0])
            month = int(parts[1])
            # Use a reference year to validate
            hebrew_date = HebrewDate(year=5784, month=month, day=day)
            greg_date = hebrew_date.to_gdate()
            greg_datetime = datetime(greg_date.year, greg_date.month, greg_date.day)
            _LOGGER.debug(f"Successfully parsed Hebrew date (DD-MM): {value} -> {greg_datetime}")
            return greg_datetime, True  # True = year is unknown
    except (ValueError, AttributeError) as e:
        _LOGGER.debug(f"Failed to parse Hebrew date with dash format: {e}")
        pass
    
    # Try format: "DD MonthName YYYY" or "DD MonthName"
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
            
            # Map month names to numbers (case-insensitive)
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
            _LOGGER.debug(f"Parsed month name '{month_name}' -> '{month_name_lower}' -> {month_num}")
            if month_num:
                if year:
                    _LOGGER.debug(f"Creating HebrewDate with day={day}, month={month_num}, year={year}")
                    hebrew_date = HebrewDate(year=year, month=month_num, day=day)
                    greg_date = hebrew_date.to_gdate()
                    greg_datetime = datetime(greg_date.year, greg_date.month, greg_date.day)
                    _LOGGER.debug(f"Successfully parsed Hebrew date (DD MonthName YYYY): {value} -> {greg_datetime}")
                    return greg_datetime, False
                else:
                    # Use reference year
                    hebrew_date = HebrewDate(year=5784, month=month_num, day=day)
                    greg_date = hebrew_date.to_gdate()
                    greg_datetime = datetime(greg_date.year, greg_date.month, greg_date.day)
                    _LOGGER.debug(f"Successfully parsed Hebrew date (DD MonthName): {value} -> {greg_datetime}")
                    return greg_datetime, True
            else:
                _LOGGER.warning(f"Month name not found in map: '{month_name}' (lowercase: '{month_name_lower}')")
    except (ValueError, KeyError, AttributeError) as e:
        _LOGGER.error(f"Error parsing Hebrew date '{value}': {e}", exc_info=True)
        pass
    
    _LOGGER.warning(f"Could not validate Hebrew date: {value}")
    return "Invalid Date", False

class anniversaries(Entity):
    def __init__(self, hass, config):
        """Initialize the sensor."""
        self.config = config
        self._name = config.get(CONF_NAME)
        self._id_prefix = config.get(CONF_ID_PREFIX)
        if self._id_prefix is None:
            self._id_prefix = "anniversary_"
        self.entity_id = generate_entity_id(ENTITY_ID_FORMAT, self._id_prefix + self._name, [])
        self._unknown_year = False
        self._date = ""
        self._calendar_type = config.get(CONF_CALENDAR_TYPE, DEFAULT_CALENDAR_TYPE)
        self._hebrew_date = None  # Store original Hebrew date string
        self._hebrew_date_obj = None  # Store parsed Hebrew date components
        self._show_half_anniversary = config.get(CONF_HALF_ANNIVERSARY)
        self._half_days_remaining = 0
        self._half_date = ""
        self._template_sensor = False
        self._date_template = config.get(CONF_DATE_TEMPLATE)
        if self._date_template is not None:
            self._template_sensor = True
        else:
            date_str = config.get(CONF_DATE)
            self._date, self._unknown_year = validate_date(date_str, self._calendar_type)
            
            # Store Hebrew date information if using Hebrew calendar
            if self._calendar_type == CALENDAR_TYPE_HEBREW and self._date != "Invalid Date":
                self._hebrew_date = date_str
                self._parse_hebrew_date(date_str)
            
            if self._date != "Invalid Date":
                self._date = self._date.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)
                if self._show_half_anniversary:
                    self._half_date = self._date + relativedelta(months=+6)
        self._event_type = config.get(CONF_EVENT_TYPE, DEFAULT_EVENT_TYPE)
        # Get event-type specific icons as defaults
        event_icons = EVENT_TYPE_ICONS.get(self._event_type, EVENT_TYPE_ICONS[DEFAULT_EVENT_TYPE])
        self._icon_normal = config.get(CONF_ICON_NORMAL) or event_icons["normal"]
        self._icon_today = config.get(CONF_ICON_TODAY) or event_icons["today"]
        self._icon_soon = config.get(CONF_ICON_SOON) or event_icons["soon"]
        self._soon = config.get(CONF_SOON)
        self._icon = self._icon_normal
        self._years_next = 0
        self._years_current = 0
        self._state = 0
        self._weeks_remaining = 0
        self._unit_of_measurement = config.get(CONF_UNIT_OF_MEASUREMENT)
        if self._unit_of_measurement is None:
            self._unit_of_measurement = DEFAULT_UNIT_OF_MEASUREMENT
        self._one_time = config.get(CONF_ONE_TIME)
        self._count_up = config.get(CONF_COUNT_UP)

    def _parse_hebrew_date(self, date_str):
        """Parse Hebrew date string and store components."""
        if not HDATE_AVAILABLE:
            return
        
        try:
            # Try format: DD-MM-YYYY or DD-MM
            parts = date_str.split("-")
            if len(parts) >= 2:
                day = int(parts[0])
                month = int(parts[1])
                year = int(parts[2]) if len(parts) == 3 else None
                self._hebrew_date_obj = {"day": day, "month": month, "year": year}
                return
        except (ValueError, KeyError):
            pass
        
        try:
            # Try format: "DD MonthName YYYY" or "DD MonthName"
            parts = date_str.split()
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
                
                # Map month names to numbers (case-insensitive)
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
                if month_num:
                    self._hebrew_date_obj = {"day": day, "month": month_num, "year": year}
        except (ValueError, KeyError):
            pass

    def _calculate_next_hebrew_anniversary(self, today):
        """Calculate next occurrence of Hebrew anniversary."""
        if not HDATE_AVAILABLE or not self._hebrew_date_obj:
            return None
        
        try:
            # Get today's Hebrew date
            today_hdate = HebrewDate.from_gdate(today)
            current_hyear = today_hdate.year
            
            day = self._hebrew_date_obj["day"]
            month = self._hebrew_date_obj["month"]
            original_year = self._hebrew_date_obj["year"]
            
            # Handle Adar in leap years (edge case)
            target_month = self._handle_adar_month(month, current_hyear)
            
            # Try to create the anniversary for this Hebrew year
            try:
                # Handle day overflow (e.g., 30th of a 29-day month)
                max_day = self._get_max_day_in_month(target_month, current_hyear)
                actual_day = min(day, max_day)
                
                next_hdate = HebrewDate(year=current_hyear, month=target_month, day=actual_day)
                next_gdate = next_hdate.to_gdate()
                
                # If the date has passed this year, use next Hebrew year
                if next_gdate <= today:
                    next_hyear = current_hyear + 1
                    target_month = self._handle_adar_month(month, next_hyear)
                    max_day = self._get_max_day_in_month(target_month, next_hyear)
                    actual_day = min(day, max_day)
                    next_hdate = HebrewDate(year=next_hyear, month=target_month, day=actual_day)
                    next_gdate = next_hdate.to_gdate()
                
                return next_gdate, next_hdate
            except (ValueError, AttributeError):
                # If there's an error, try next year
                next_hyear = current_hyear + 1
                target_month = self._handle_adar_month(month, next_hyear)
                max_day = self._get_max_day_in_month(target_month, next_hyear)
                actual_day = min(day, max_day)
                next_hdate = HebrewDate(year=next_hyear, month=target_month, day=actual_day)
                next_gdate = next_hdate.to_gdate()
                return next_gdate, next_hdate
        except Exception as e:
            _LOGGER.error(f"Error calculating Hebrew anniversary: {e}")
            return None
    
    def _handle_adar_month(self, month, year):
        """Handle Adar month in leap years."""
        if not HDATE_AVAILABLE:
            return month
        
        # Check if it's a leap year using HebrewDate
        hd = HebrewDate(year=year, month=1, day=1)
        is_leap = hd.is_leap_year()
        
        # Month 6 is Adar in non-leap years, but in leap years we have Adar I (7) and Adar II (8)
        # For birthdays/anniversaries in Adar, halachic custom is to celebrate in Adar II in leap years
        if month == 6 and is_leap:
            return 8  # Adar II
        elif month == 7 and not is_leap:
            return 6  # Adar I becomes regular Adar in non-leap years
        elif month == 8 and not is_leap:
            return 6  # Adar II becomes regular Adar in non-leap years
        
        return month
    
    def _get_max_day_in_month(self, month, year):
        """Get maximum day in a Hebrew month."""
        if not HDATE_AVAILABLE:
            return 30
        
        try:
            # Use HebrewDate's days_in_month method with Months enum
            hd = HebrewDate(year=year, month=month, day=1)
            return hd.days_in_month(Months(month))
        except (ValueError, AttributeError):
            return 29
    
    def _format_hebrew_date(self, hdate_obj):
        """Format Hebrew date as string."""
        if not hdate_obj:
            return ""
        
        try:
            # Get Hebrew month name
            # Month numbering: Tishrei=1, Marcheshvan=2, ..., Adar=6, Adar_I=7, Adar_II=8, Nisan=9, ..., Elul=14
            month_names = {
                1: "Tishrei", 2: "Cheshvan", 3: "Kislev", 4: "Tevet", 5: "Shevat", 6: "Adar",
                7: "Adar I", 8: "Adar II",
                9: "Nisan", 10: "Iyar", 11: "Sivan", 12: "Tammuz", 13: "Av", 14: "Elul"
            }
            
            day = hdate_obj.day
            month_value = hdate_obj.month.value
            year = hdate_obj.year
            
            month_name = month_names.get(month_value, str(month_value))
            
            return f"{day} {month_name} {year}"
        except (AttributeError, IndexError):
            return ""

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
    def extra_state_attributes(self):
        """Return the state attributes."""
        res = {}
        res[ATTR_ATTRIBUTION] = ATTRIBUTION
        if self._state in ["Invalid Date", "Invalid Template"]:
            return res
        if not self._unknown_year:
            res[ATTR_YEARS_NEXT] = self._years_next
            res[ATTR_YEARS_CURRENT] = self._years_current
        
        # Convert datetime objects to simple date format (yyyy-mm-dd)
        res[ATTR_DATE] = self._date.strftime("%Y-%m-%d") if isinstance(self._date, datetime) else self._date
        res[ATTR_NEXT_DATE] = self._next_date.strftime("%Y-%m-%d") if isinstance(self._next_date, datetime) else self._next_date
        res[ATTR_WEEKS] = self._weeks_remaining
        res[ATTR_CALENDAR_TYPE] = self._calendar_type
        res[ATTR_EVENT_TYPE] = self._event_type
        res[ATTR_ICON] = self._icon
        
        # Add Hebrew calendar attributes - always include for consistency
        if self._calendar_type == CALENDAR_TYPE_HEBREW:
            res[ATTR_HEBREW_DATE] = self._hebrew_date if self._hebrew_date else ""
            res[ATTR_HEBREW_NEXT_DATE] = self._next_hebrew_date if hasattr(self, '_next_hebrew_date') and self._next_hebrew_date else ""
        else:
            res[ATTR_HEBREW_DATE] = ""
            res[ATTR_HEBREW_NEXT_DATE] = ""
        
        if self._show_half_anniversary:
            res[ATTR_HALF_DATE] = self._half_date.strftime("%Y-%m-%d") if isinstance(self._half_date, datetime) else self._half_date
            res[ATTR_HALF_DAYS] = self._half_days_remaining
        return res

    @property
    def icon(self):
        return self._icon

    @property
    def unit_of_measurement(self):
        """Return the unit this state is expressed in."""
        if self._state in ["Invalid Date", "Invalid Template"]:
            return
        return self._unit_of_measurement

    async def async_update(self):
        """update the sensor"""
        if self._template_sensor:
            try:
                template_date = templater.Template(self._date_template, self.hass).async_render()
                self._date, self._unknown_year = validate_date(template_date, self._calendar_type)
                if self._date == "Invalid Date":
                    self._state = self._date
                    return
                self._date = self._date.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)
            except:
                self._state = "Invalid Template"
                return
        
        # Check if date is invalid for non-template sensors
        if self._date == "Invalid Date":
            self._state = self._date
            return

        today = date.today()
        
        # Use Hebrew calendar calculation if calendar type is Hebrew
        if self._calendar_type == CALENDAR_TYPE_HEBREW and HDATE_AVAILABLE and self._hebrew_date_obj:
            result = self._calculate_next_hebrew_anniversary(today)
            if result:
                nextDate, next_hdate = result
                # Calculate years if original year is known
                if self._hebrew_date_obj["year"]:
                    years = next_hdate.year - self._hebrew_date_obj["year"]
                else:
                    years = 0
                    self._unknown_year = True
            else:
                # Fallback to Gregorian calculation
                years = today.year - self._date.year
                nextDate = self._date.date()
                next_hdate = None
                
                if today >= self._date.date() + relativedelta(year=today.year):
                    years = years + 1
                    
                if not self._one_time:
                    if today >= nextDate:
                        nextDate = self._date.date() + relativedelta(year=today.year)
                    if today > nextDate:
                        nextDate = self._date.date() + relativedelta(year=today.year + 1)
        else:
            # Gregorian calendar calculation (original logic)
            years = today.year - self._date.year
            nextDate = self._date.date()
            next_hdate = None

            if today >= self._date.date() + relativedelta(year=today.year):
                years = years + 1
                
            if not self._one_time:
                if today >= nextDate:
                    nextDate = self._date.date() + relativedelta(year=today.year)
                if today > nextDate:
                    nextDate = self._date.date() + relativedelta(year=today.year + 1)

        self._next_date = datetime.combine(nextDate, datetime.min.time())
        self._next_date = self._next_date.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)
        daysRemaining = (nextDate - today).days
        
        if self._unknown_year:
            self._date = datetime(nextDate.year, nextDate.month, nextDate.day)
            self._date = self._date.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)

        if daysRemaining == 0:
            self._icon = self._icon_today
        elif daysRemaining <= self._soon:
            self._icon = self._icon_soon
        else:
            self._icon = self._icon_normal

        self._state = daysRemaining
        if daysRemaining == 0:
            self._years_next = years - 1
        else:
            self._years_next = years
        self._years_current = years - 1
        self._weeks_remaining = int(daysRemaining / 7)

        if self._count_up:
            if daysRemaining > 0 and not self._one_time:
                nextDate = nextDate + relativedelta(years=-1)
            self._state = (today - nextDate).days

        if self._show_half_anniversary:
            nextHalfDate = self._half_date.date()
            if today > nextHalfDate:
                nextHalfDate = self._half_date.date() + relativedelta(year = today.year)
            if today > nextHalfDate:
                nextHalfDate = self._half_date.date() + relativedelta(year = today.year + 1)
            self._half_days_remaining = (nextHalfDate - today).days
            self._half_date = datetime(nextHalfDate.year, nextHalfDate.month, nextHalfDate.day)
            self._half_date = self._half_date.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)
        
        # Store the next Hebrew date if applicable
        if self._calendar_type == CALENDAR_TYPE_HEBREW and next_hdate:
            self._next_hebrew_date = self._format_hebrew_date(next_hdate)
        else:
            self._next_hebrew_date = None

    async def async_added_to_hass(self):
        """Once the entity is added we should update to get the initial data loaded. Then add it to the Calendar."""
        await super().async_added_to_hass()
        self.async_schedule_update_ha_state(True)
        if DOMAIN not in self.hass.data:
            self.hass.data[DOMAIN] = {}
        if SENSOR_PLATFORM not in self.hass.data[DOMAIN]:
            self.hass.data[DOMAIN][SENSOR_PLATFORM] = {}
        self.hass.data[DOMAIN][SENSOR_PLATFORM][self.entity_id] = self

        if CALENDAR_PLATFORM not in self.hass.data[DOMAIN]:
            self.hass.data[DOMAIN][
                CALENDAR_PLATFORM
            ] = EntitiesCalendarData(self.hass)
            _LOGGER.debug("Creating Anniversaries calendar")
            self.hass.async_create_task(
                async_load_platform(
                    self.hass,
                    CALENDAR_PLATFORM,
                    DOMAIN,
                    {"name": CALENDAR_NAME},
                    {"name": CALENDAR_NAME},
                )
            )
        else:
            _LOGGER.debug("Anniversaries calendar already exists")
        self.hass.data[DOMAIN][CALENDAR_PLATFORM].add_entity(self.entity_id)

    async def async_will_remove_from_hass(self):
        """When sensor is removed from hassio and there are no other sensors in the Anniversaries calendar, remove it."""
        await super().async_will_remove_from_hass()
        _LOGGER.debug("Removing: %s" % (self._name))
        del self.hass.data[DOMAIN][SENSOR_PLATFORM][self.entity_id]
        self.hass.data[DOMAIN][CALENDAR_PLATFORM].remove_entity(self.entity_id)
