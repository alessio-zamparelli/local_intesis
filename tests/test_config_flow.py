import pytest
import voluptuous as vol

from homeassistant.const import CONF_HOST

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.local_intesis import async_migrate_entry
from custom_components.local_intesis.const import (
    CONF_SCAN_INTERVAL,
    DOMAIN,
    MIN_SCAN_INTERVAL,
)


async def test_migrate_entry_v1_preserves_scan_interval(hass):
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=1,
        data={"host": "1.2.3.4", "username": "admin", "password": "admin"},
        options={},
    )
    entry.add_to_hass(hass)

    assert await async_migrate_entry(hass, entry) is True
    assert entry.version == 2
    assert entry.options[CONF_SCAN_INTERVAL] == MIN_SCAN_INTERVAL


async def test_options_flow_validation(hass):
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=2,
        data={"host": "1.2.3.4", "username": "admin", "password": "admin"},
        options={},
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == "form"
    flow_id = result["flow_id"]

    for invalid in ("not-a-number", "5", "3601"):
        with pytest.raises(vol.Invalid) as exc:
            await hass.config_entries.options.async_configure(
                flow_id, {CONF_SCAN_INTERVAL: invalid}
            )
        assert CONF_SCAN_INTERVAL in exc.value.schema_errors

    result = await hass.config_entries.options.async_configure(
        flow_id, {CONF_SCAN_INTERVAL: "60"}
    )
    assert result["type"] == "create_entry"
    assert result["data"][CONF_SCAN_INTERVAL] == 60