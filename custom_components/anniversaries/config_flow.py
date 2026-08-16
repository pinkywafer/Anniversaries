""" Config flow """
from collections import OrderedDict
from homeassistant.core import callback
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)
from datetime import datetime
import uuid

from .const import (
    DEFAULT_COUNT_UP,
    DOMAIN,
    DEFAULT_ICON_NORMAL,
    DEFAULT_ICON_SOON,
    DEFAULT_ICON_TODAY,
    DEFAULT_SOON,
    DEFAULT_HALF_ANNIVERSARY,
    DEFAULT_UNIT_OF_MEASUREMENT,
    DEFAULT_ID_PREFIX,
    DEFAULT_ONE_TIME,
    DEFAULT_COUNT_UP,
    DEFAULT_CALENDAR_TYPE,
    DEFAULT_EVENT_TYPE,
    CONF_ICON_NORMAL,
    CONF_ICON_TODAY,
    CONF_ICON_SOON,
    CONF_DATE,
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
    CALENDAR_TYPE_OPTIONS,
    EVENT_TYPE_OPTIONS,
    EVENT_TYPE_ICONS,
)

from homeassistant.const import CONF_NAME


@config_entries.HANDLERS.register(DOMAIN)
class AnniversariesFlowHandler(config_entries.ConfigFlow):
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        self._errors = {}
        self._data = {}
        self._data["unique_id"] = str(uuid.uuid4())

    async def async_step_user(self, user_input=None):   # pylint: disable=unused-argument
        self._errors = {}
        if user_input is not None:
            self._data.update(user_input)
            calendar_type = user_input.get(CONF_CALENDAR_TYPE, DEFAULT_CALENDAR_TYPE)
            if is_not_date(user_input[CONF_DATE], user_input[CONF_ONE_TIME], calendar_type):
                self._errors["base"] = "invalid_date"
            if self._errors == {}:
                self.init_info = user_input
                return await self.async_step_icons()
        return await self._show_user_form(user_input)

    async def async_step_icons(self, user_input=None):
        self._errors = {}
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(title=self._data["name"], data=self._data)
        return await self._show_icon_form(user_input)

    async def _show_user_form(self, user_input):
        name = ""
        date = ""
        count_up = DEFAULT_COUNT_UP
        one_time = DEFAULT_ONE_TIME
        half_anniversary = DEFAULT_HALF_ANNIVERSARY
        unit_of_measurement = DEFAULT_UNIT_OF_MEASUREMENT
        id_prefix = DEFAULT_ID_PREFIX
        calendar_type = DEFAULT_CALENDAR_TYPE
        event_type = DEFAULT_EVENT_TYPE
        if user_input is not None:
            if CONF_NAME in user_input:
                name = user_input[CONF_NAME]
            if CONF_DATE in user_input:
                date = user_input[CONF_DATE]
            if CONF_COUNT_UP in user_input:
                count_up = user_input[CONF_COUNT_UP]
            if CONF_ONE_TIME in user_input:
                one_time = user_input[CONF_ONE_TIME]
            if CONF_HALF_ANNIVERSARY in user_input:
                half_anniversary = user_input[CONF_HALF_ANNIVERSARY]
            if CONF_UNIT_OF_MEASUREMENT in user_input:
                unit_of_measurement = user_input[CONF_UNIT_OF_MEASUREMENT]
            if CONF_ID_PREFIX in user_input:
                id_prefix = user_input[CONF_ID_PREFIX]
            if CONF_CALENDAR_TYPE in user_input:
                calendar_type = user_input[CONF_CALENDAR_TYPE]
            if CONF_EVENT_TYPE in user_input:
                event_type = user_input[CONF_EVENT_TYPE]
        data_schema = OrderedDict()
        data_schema[vol.Required(CONF_NAME, default=name)] = str
        data_schema[vol.Required(CONF_CALENDAR_TYPE, default=calendar_type)] = SelectSelector(
            SelectSelectorConfig(
                options=CALENDAR_TYPE_OPTIONS,
                mode=SelectSelectorMode.DROPDOWN,
                translation_key="calendar_type",
            )
        )
        data_schema[vol.Required(CONF_EVENT_TYPE, default=event_type)] = SelectSelector(
            SelectSelectorConfig(
                options=EVENT_TYPE_OPTIONS,
                mode=SelectSelectorMode.DROPDOWN,
                translation_key="event_type",
            )
        )
        data_schema[vol.Required(CONF_DATE, default=date)] = str
        data_schema[vol.Required(CONF_COUNT_UP, default=count_up)] = bool
        data_schema[vol.Required(CONF_ONE_TIME, default=one_time)] = bool
        data_schema[vol.Required(CONF_HALF_ANNIVERSARY, default=half_anniversary)] = bool
        data_schema[vol.Required(CONF_UNIT_OF_MEASUREMENT, default=unit_of_measurement)] = str
        data_schema[vol.Optional(CONF_ID_PREFIX, default=id_prefix)] = str
        return self.async_show_form(step_id="user", data_schema=vol.Schema(data_schema), errors=self._errors)

    async def _show_icon_form(self, user_input):
        # Get event type-specific icons
        event_type = self._data.get(CONF_EVENT_TYPE, DEFAULT_EVENT_TYPE)
        event_icons = EVENT_TYPE_ICONS.get(event_type, EVENT_TYPE_ICONS[DEFAULT_EVENT_TYPE])
        
        icon_normal = event_icons["normal"]
        icon_today = event_icons["today"]
        days_as_soon = DEFAULT_SOON
        icon_soon = event_icons["soon"]
        if user_input is not None:
            if CONF_ICON_NORMAL in user_input:
                icon_normal = user_input[CONF_ICON_NORMAL]
            if CONF_ICON_TODAY in user_input:
                icon_today = user_input[CONF_ICON_TODAY]
            if CONF_SOON in user_input:
                days_as_soon = user_input[CONF_SOON]
            if CONF_ICON_SOON in user_input:
                icon_soon = user_input[CONF_ICON_SOON]
        data_schema = OrderedDict()
        data_schema[vol.Required(CONF_ICON_NORMAL, default=icon_normal)] = str
        data_schema[vol.Required(CONF_ICON_TODAY, default=icon_today)] = str
        data_schema[vol.Required(CONF_SOON, default=days_as_soon)] = int
        data_schema[vol.Required(CONF_ICON_SOON, default=icon_soon)] = str
        return self.async_show_form(step_id="icons", data_schema=vol.Schema(data_schema), errors=self._errors)

    async def async_step_import(self, user_input):  # pylint: disable=unused-argument
        """Import a config entry.
        Special type of import, we're not actually going to store any data.
        Instead, we're going to rely on the values that are in config file.
        """
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return self.async_create_entry(title="configuration.yaml", data={})

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        if config_entry.options.get("unique_id", None) is not None:
            return OptionsFlowHandler(config_entry)
        else:
            return EmptyOptions(config_entry)

def is_not_date(date, one_time, calendar_type=CALENDAR_TYPE_GREGORIAN):
    """Validate date based on calendar type."""
    if calendar_type == CALENDAR_TYPE_HEBREW:
        # Hebrew date validation
        try:
            from hdate import HebrewDate
        except ImportError:
            return True  # Can't validate Hebrew dates without hdate library
        
        if not date or not isinstance(date, str):
            return True
        
        try:
            # Try format: DD-MM-YYYY
            parts = date.split("-")
            if len(parts) == 3:
                day = int(parts[0])
                month = int(parts[1])
                year = int(parts[2])
                # Validate using HebrewDate
                HebrewDate(year=year, month=month, day=day)
                return False
            # Try format: DD-MM (no year for recurring dates)
            elif len(parts) == 2:
                day = int(parts[0])
                month = int(parts[1])
                # Basic validation: Hebrew months 1-14, days 1-30
                if 1 <= month <= 14 and 1 <= day <= 30:
                    # For more thorough validation, try creating a date with a sample year
                    # Use a leap year to allow all month values
                    try:
                        HebrewDate(year=5784, month=month, day=day)
                        return False
                    except (ValueError, AttributeError):
                        return True
                return True
        except (ValueError, AttributeError, TypeError):
            pass
        
        # Try format with month names (e.g., "5 Tishrei" or "5 Tishrei 5784")
        try:
            parts = date.split()
            if len(parts) >= 2:
                day = int(parts[0])
                month_name = parts[1]
                year = None
                
                # Handle "Adar I" and "Adar II" with space (e.g., "15 Adar I 5765" or "15 Adar II")
                if len(parts) >= 3 and parts[1].lower() == 'adar' and parts[2].lower() in ('i', 'ii', '1', '2'):
                    month_name = parts[1] + ' ' + parts[2]  # Combine "Adar" + "I" or "II"
                    if len(parts) == 4:
                        year = int(parts[3])
                elif len(parts) == 3:
                    year = int(parts[2])
                
                # Map Hebrew month names to numbers
                # Using hdate library month numbering: Tishrei=1, ..., Adar=6, Adar_I=7, Adar_II=8, Nisan=9, ..., Elul=14
                month_map = {
                    'tishrei': 1, 'cheshvan': 2, 'marcheshvan': 2, 'kislev': 3, 'tevet': 4,
                    'shevat': 5, 'shvat': 5, 'adar': 6,
                    'adar1': 7, 'adar_i': 7, 'adar i': 7,
                    'adar2': 8, 'adar_ii': 8, 'adar ii': 8,
                    'nisan': 9, 'iyar': 10, 'sivan': 11, 'tammuz': 12,
                    'av': 13, 'elul': 14
                }
                
                month_name_lower = month_name.lower()
                if month_name_lower in month_map:
                    month = month_map[month_name_lower]
                    
                    if year is not None:
                        # With year
                        HebrewDate(year=year, month=month, day=day)
                        return False
                    else:
                        # Without year - validate with sample leap year
                        try:
                            HebrewDate(year=5784, month=month, day=day)
                            return False
                        except (ValueError, AttributeError):
                            return True
        except (ValueError, AttributeError, TypeError, IndexError):
            pass
        
        return True  # Invalid Hebrew date
    else:
        # Gregorian validation (original logic)
        try:
            datetime.strptime(date, "%Y-%m-%d")
            return False
        except ValueError:
            if not one_time:
                pass
            else:
                return True
        try:
            datetime.strptime(date, "%m-%d")
            return False
        except ValueError:
            return True


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        super().__init__()
        self._config_entry = config_entry
        self._data = {}
        self._data["unique_id"] = config_entry.options.get("unique_id")

    async def async_step_init(self, user_input=None):
        self._errors = {}
        if user_input is not None:
            self._data.update(user_input)
            calendar_type = user_input.get(CONF_CALENDAR_TYPE, DEFAULT_CALENDAR_TYPE)
            if is_not_date(user_input[CONF_DATE], user_input[CONF_ONE_TIME], calendar_type):
                self._errors["base"] = "invalid_date"
            if self._errors == {}:
                return await self.async_step_icons()
        return await self._show_init_form(user_input)

    async def async_step_icons(self, user_input=None):
        self._errors = {}
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(title="", data=self._data)
        return await self._show_icon_form(user_input)

    async def _show_init_form(self, user_input):
        data_schema = OrderedDict()
        count_up = self._config_entry.options.get(CONF_COUNT_UP)
        one_time = self._config_entry.options.get(CONF_ONE_TIME)
        unit_of_measurement = self._config_entry.options.get(CONF_UNIT_OF_MEASUREMENT)
        half_anniversary = self._config_entry.options.get(CONF_HALF_ANNIVERSARY)
        calendar_type = self._config_entry.options.get(CONF_CALENDAR_TYPE)
        event_type = self._config_entry.options.get(CONF_EVENT_TYPE)
        if count_up is None:
            count_up = DEFAULT_COUNT_UP
        if one_time is None:
            one_time = DEFAULT_ONE_TIME
        if half_anniversary is None:
            half_anniversary = DEFAULT_HALF_ANNIVERSARY
        if unit_of_measurement is None:
            unit_of_measurement = DEFAULT_UNIT_OF_MEASUREMENT
        if calendar_type is None:
            calendar_type = DEFAULT_CALENDAR_TYPE
        if event_type is None:
            event_type = DEFAULT_EVENT_TYPE
        data_schema[vol.Required(CONF_NAME,default=self._config_entry.options.get(CONF_NAME),)] = str
        data_schema[vol.Required(CONF_CALENDAR_TYPE, default=calendar_type,)] = SelectSelector(
            SelectSelectorConfig(
                options=CALENDAR_TYPE_OPTIONS,
                mode=SelectSelectorMode.DROPDOWN,
                translation_key="calendar_type",
            )
        )
        data_schema[vol.Required(CONF_EVENT_TYPE, default=event_type,)] = SelectSelector(
            SelectSelectorConfig(
                options=EVENT_TYPE_OPTIONS,
                mode=SelectSelectorMode.DROPDOWN,
                translation_key="event_type",
            )
        )
        data_schema[vol.Required(CONF_DATE, default=self._config_entry.options.get(CONF_DATE),)] = str
        data_schema[vol.Required(CONF_COUNT_UP, default=count_up,)] = bool
        data_schema[vol.Required(CONF_ONE_TIME, default=one_time,)] = bool
        data_schema[vol.Required(CONF_HALF_ANNIVERSARY,default=half_anniversary,)] = bool
        data_schema[vol.Required(CONF_UNIT_OF_MEASUREMENT,default=unit_of_measurement,)] = str
        return self.async_show_form(
            step_id="init", data_schema=vol.Schema(data_schema), errors=self._errors
        )

    async def _show_icon_form(self, user_input):
        # Get event type from the data collected in init step (may have been updated)
        old_event_type = self._config_entry.options.get(CONF_EVENT_TYPE, DEFAULT_EVENT_TYPE)
        new_event_type = self._data.get(CONF_EVENT_TYPE, old_event_type)
        event_type_changed = old_event_type != new_event_type
        
        event_icons = EVENT_TYPE_ICONS.get(new_event_type, EVENT_TYPE_ICONS[DEFAULT_EVENT_TYPE])
        
        # Check if existing icons are the old event type defaults (not user-customized)
        existing_icon_normal = self._config_entry.options.get(CONF_ICON_NORMAL)
        existing_icon_today = self._config_entry.options.get(CONF_ICON_TODAY)
        existing_icon_soon = self._config_entry.options.get(CONF_ICON_SOON)
        
        # If event type changed and icons match old event type defaults, use new event type icons
        if event_type_changed:
            icon_normal = event_icons["normal"]
            icon_today = event_icons["today"]
            icon_soon = event_icons["soon"]
        else:
            # Use existing values if set, otherwise use event type-specific defaults
            icon_normal = existing_icon_normal or event_icons["normal"]
            icon_today = existing_icon_today or event_icons["today"]
            icon_soon = existing_icon_soon or event_icons["soon"]
        
        days_as_soon = self._config_entry.options.get(CONF_SOON) or DEFAULT_SOON
        
        data_schema = OrderedDict()
        data_schema[vol.Required(CONF_ICON_NORMAL, default=icon_normal,)] = str
        data_schema[vol.Required(CONF_ICON_TODAY, default=icon_today,)] = str
        data_schema[vol.Required(CONF_SOON, default=days_as_soon,)] = int
        data_schema[vol.Required(CONF_ICON_SOON, default=icon_soon,)] = str
        return self.async_show_form(step_id="icons", data_schema=vol.Schema(data_schema), errors=self._errors)


class EmptyOptions(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        super().__init__()
