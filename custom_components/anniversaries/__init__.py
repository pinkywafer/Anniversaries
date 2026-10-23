"""The Anniversaries Integration"""
import logging
from homeassistant import config_entries
from homeassistant.helpers import discovery

from .const import (
    CONF_SENSORS,
    CONF_DATE_TEMPLATE,
    DOMAIN,
    ISSUE_URL,
    PLATFORM,
    VERSION,
    CONFIG_SCHEMA,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    """Set up this component using YAML."""
    if config.get(DOMAIN) is None:
        # Config flow setup if no YAML config exists
        return True

    # Log startup message
    _LOGGER.info("Anniversaries %s starting - issues: %s", VERSION, ISSUE_URL)

    platform_config = config[DOMAIN].get(CONF_SENSORS, {})

    # If no platform is enabled, skip setup
    if not platform_config:
        return False

    # Load platform configuration for each entry
    for entry in platform_config:
        hass.async_create_task(
            discovery.async_load_platform(hass, PLATFORM, DOMAIN, entry, config)
        )

    # Initiate config flow to import YAML config
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_IMPORT}, data={}
        )
    )

    return True

async def async_setup_entry(hass, config_entry):
    """Set up this integration using UI."""
    if config_entry.source == config_entries.SOURCE_IMPORT:
        # Marker entry from YAML import: remove it only after setup completes.
        # Awaiting the removal here deadlocks on the entry's own setup lock
        # (upstream issues #180/#181 - the multi-minute startup hang).
        hass.async_create_task(
            hass.config_entries.async_remove(config_entry.entry_id)
        )
        return True

    # Log startup message
    _LOGGER.info("Anniversaries %s starting - issues: %s", VERSION, ISSUE_URL)

    # Safely update entry options if needed
    hass.config_entries.async_update_entry(
        config_entry, options=config_entry.data
    )

    # Add update listener for configuration changes (tied to unload so reloads
    # don't stack up duplicate listeners)
    config_entry.async_on_unload(config_entry.add_update_listener(update_listener))

    # Set up the platforms using the new `async_forward_entry_setups`
    await hass.config_entries.async_forward_entry_setups(config_entry, [PLATFORM])

    return True

async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    # Unload the platform using `async_unload_platforms`
    if await hass.config_entries.async_unload_platforms(config_entry, [PLATFORM]):
        _LOGGER.info(f"Successfully unloaded {PLATFORM} for {DOMAIN}")
        return True
    else:
        _LOGGER.error(f"Error unloading {PLATFORM} for {DOMAIN}")
        return False

async def async_remove_entry(hass, config_entry):
    """Handle removal of a config entry."""
    # Ensure the platform is unloaded before removing the entry
    await async_unload_entry(hass, config_entry)
    _LOGGER.info(f"Successfully removed entry for {DOMAIN}")

async def update_listener(hass, entry):
    """Handle updates to the config entry."""
    # Mirror options into data first. That update re-enters this listener with
    # data == options, which is the point where a single reload happens.
    if entry.data != entry.options:
        hass.config_entries.async_update_entry(entry, data=entry.options)
        return

    await hass.config_entries.async_reload(entry.entry_id)