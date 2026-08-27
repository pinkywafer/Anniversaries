"""Dynamic services for Anniversaries integration."""
import logging
from typing import Any, Dict

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er
from homeassistant.exceptions import HomeAssistantError
from homeassistant.data_entry_flow import FlowResultType

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_DATE,
    CONF_DATE_TEMPLATE,
    CONF_ONE_TIME,
    CONF_COUNT_UP,
    CONF_UNIT_OF_MEASUREMENT,
    CONF_ID_PREFIX,
)

_LOGGER = logging.getLogger(__name__)

# Service schema for adding an anniversary
ADD_ANNIVERSARY_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): cv.string,
    vol.Exclusive(CONF_DATE, 'date_specifier'): cv.string,
    vol.Exclusive(CONF_DATE_TEMPLATE, 'date_specifier'): cv.template,
    vol.Optional(CONF_ONE_TIME, default=False): cv.boolean,
    vol.Optional(CONF_COUNT_UP, default=False): cv.boolean,
    vol.Optional(CONF_UNIT_OF_MEASUREMENT): cv.string,
    vol.Optional(CONF_ID_PREFIX): cv.string,
})

# Service schema for removing an anniversary
REMOVE_ANNIVERSARY_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): cv.string,
})

async def async_register_services(hass: HomeAssistant):
    """Register services for the Anniversaries integration."""

    async def add_anniversary(call: ServiceCall) -> None:
        """Service to add a new anniversary."""
        # Prepare anniversary configuration
        anniversary_config = {
            CONF_NAME: call.data[CONF_NAME],
        }

        # Add date or date template
        if CONF_DATE in call.data:
            anniversary_config[CONF_DATE] = call.data[CONF_DATE]
        elif CONF_DATE_TEMPLATE in call.data:
            anniversary_config[CONF_DATE_TEMPLATE] = call.data[CONF_DATE_TEMPLATE]
        else:
            raise HomeAssistantError("Either date or date template must be provided")

        # Add optional parameters
        optional_params = [
            CONF_ONE_TIME,
            CONF_COUNT_UP,
            CONF_UNIT_OF_MEASUREMENT,
            CONF_ID_PREFIX,
        ]
        for param in optional_params:
            if param in call.data:
                anniversary_config[param] = call.data[param]

        # Create a user configuration flow
        flow = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={'source': 'user'},
            data=anniversary_config
        )

        # Handle multi-step config flow
        while flow['type'] == FlowResultType.FORM:
            # Prepare data for the next step
            step_id = flow['step_id']

            if step_id == 'icons':
                # Provide default icon configuration
                icon_config = {
                    'icon_normal': 'mdi:calendar-blank',
                    'icon_today': 'mdi:calendar-star',
                    'icon_soon': 'mdi:calendar',
                    'days_as_soon': 1
                }

                flow = await hass.config_entries.flow.async_configure(
                    flow['flow_id'],
                    user_input=icon_config
                )
            else:
                # If an unexpected step occurs, raise an error
                raise HomeAssistantError(f"Unexpected config flow step: {step_id}")

        # Check if the flow was successful
        if flow['type'] != FlowResultType.CREATE_ENTRY:
            raise HomeAssistantError(f"Failed to create anniversary: {flow}")

    async def remove_anniversary(call: ServiceCall) -> None:
        """Service to remove an anniversary by name."""
        name = call.data[CONF_NAME]

        # Get all config entries for this domain
        entries = hass.config_entries.async_entries(DOMAIN)

        # Get the entity registry
        registry = er.async_get(hass)

        # Track if any anniversary was removed
        removed = False

        # Check each config entry
        for config_entry in entries:
            # Find entities for this config entry
            entities = er.async_entries_for_config_entry(registry, config_entry.entry_id)

            # Remove matching entities and config entry
            for entity in entities:
                if entity.original_name == name:
                    # Remove the entity from the registry
                    registry.async_remove(entity.entity_id)

                    # Remove the config entry
                    await hass.config_entries.async_remove(config_entry.entry_id)
                    removed = True
                    break

            if removed:
                break

        if not removed:
            raise HomeAssistantError(f"No anniversary found with name: {name}")

    # Register services with validation schemas
    hass.services.async_register(
        DOMAIN,
        'add_anniversary',
        add_anniversary,
        schema=ADD_ANNIVERSARY_SCHEMA
    )

    hass.services.async_register(
        DOMAIN,
        'remove_anniversary',
        remove_anniversary,
        schema=REMOVE_ANNIVERSARY_SCHEMA
    )

    _LOGGER.info("Anniversaries dynamic services registered")
