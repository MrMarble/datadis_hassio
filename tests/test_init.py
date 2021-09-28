"""Test component setup."""
import pytest
from homeassistant.setup import async_setup_component

from custom_components.datadis_integration.const import DOMAIN


@pytest.mark.skip
async def test_async_setup(hass):
    """Test the component gets setup."""
    assert await async_setup_component(hass, DOMAIN, {}) is True
