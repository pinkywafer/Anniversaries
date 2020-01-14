""" config flow """
from collections import OrderedDict
import logging
from homeassistant.core import callback
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant import config_entries
from datetime import datetime
import uuid

from .const import (
    DOMAIN,
    DEFAULT_ICON_NORMAL,
    DEFAULT_ICON_SOON,
    DEFAULT_ICON_TODAY,
    DEFAULT_DATE_FORMAT,
    DEFAULT_SOON,
    CONF_SENSOR,
    CONF_ENABLED,
    CONF_ICON_NORMAL,
    CONF_ICON_TODAY,
    CONF_ICON_SOON,
    CONF_DATE,
    CONF_DATE_FORMAT,
    CONF_SENSORS,
    CONF_SOON,
)

from homeassistant.const import CONF_NAME

_LOGGER = logging.getLogger(__name__)


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
            if is_not_date(user_input[CONF_DATE]):
                self._errors["base"] = "invalid_date"
            if self._errors == {}:
                return self.async_create_entry(title=self._data["name"], data=self._data)
        return await self._show_user_form(user_input)

    async def _show_user_form(self, user_input):
        name = ""
        date = ""
        icon_normal = DEFAULT_ICON_NORMAL
        icon_soon = DEFAULT_ICON_SOON
        icon_today = DEFAULT_ICON_TODAY
        date_format = DEFAULT_DATE_FORMAT
        days_as_soon = DEFAULT_SOON
        if user_input is not None:
            if CONF_NAME in user_input:
                name = user_input[CONF_NAME]
            if CONF_DATE in user_input:
                date = user_input[CONF_DATE]
            if CONF_ICON_NORMAL in user_input:
                icon_normal = user_input[CONF_ICON_NORMAL]
            if CONF_ICON_SOON in user_input:
                icon_soon = user_input[CONF_ICON_SOON]
            if CONF_ICON_TODAY in user_input:
                icon_today = user_input[CONF_ICON_TODAY]
            if CONF_DATE_FORMAT in user_input:
                date_format = user_input[CONF_DATE_FORMAT]
        data_schema = OrderedDict()
        data_schema[vol.Required(CONF_NAME, default=name)] = str
        data_schema[vol.Required(CONF_DATE, default=date)] = str
        data_schema[vol.Required(CONF_ICON_NORMAL, default=icon_normal)] = str
        data_schema[vol.Required(CONF_ICON_TODAY, default=icon_today)] = str
        data_schema[vol.Required(CONF_SOON, default=days_as_soon)] = int
        data_schema[vol.Required(CONF_ICON_SOON, default=icon_soon)] = str
        data_schema[vol.Required(CONF_DATE_FORMAT, default=date_format)] = str
        return self.async_show_form(step_id="user", data_schema=vol.Schema(data_schema), errors=self._errors)

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

def is_not_date(date):
    try:
        datetime.strptime(date, "%Y-%m-%d")
        return False
    except ValueError:
        pass
    try:
        datetime.strptime(date, "%m-%d")
        return False
    except ValueError:
        return True
        
class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry
        self._data = config_entry.options

    async def async_step_init(self, user_input=None):
        self._errors = {}
        if user_input is not None:
            self._data.update(user_input)
            if is_not_date(user_input[CONF_DATE]):
                self._errors["base"] = "invalid_date"
            if self._errors == {}:
                return self.async_create_entry(title="", data=self._data)
        return await self._show_init_form(user_input)

    async def _show_init_form(self, user_input):
        data_schema = OrderedDict()
        data_schema[vol.Required(CONF_DATE, default=self.config_entry.options.get(CONF_DATE),)] = str
        data_schema[vol.Required(CONF_ICON_NORMAL,default=self.config_entry.options.get(CONF_ICON_NORMAL),)] = str
        data_schema[vol.Required(CONF_ICON_TODAY,default=self.config_entry.options.get(CONF_ICON_SOON),)] = str
        data_schema[vol.Required(CONF_SOON,default=self.config_entry.options.get(CONF_SOON),)] = int
        data_schema[vol.Required(CONF_ICON_SOON,default=self.config_entry.options.get(CONF_ICON_SOON),)] = str
        data_schema[vol.Required(CONF_DATE_FORMAT,default=self.config_entry.options.get(CONF_DATE_FORMAT),)] = str
        return self.async_show_form(
            step_id="init", data_schema=vol.Schema(data_schema), errors=self._errors
        )

class EmptyOptions(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry