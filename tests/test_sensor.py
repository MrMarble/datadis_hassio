"""Tests for the sensor module."""

from unittest import mock

from custom_components.datadis_integration.sensor import DatadisSensor


@mock.patch("datadis.get_token")
@mock.patch(
    "datadis.get_supplies", return_value=[{"cups": "cups", "distributorCode": 0}]
)
@mock.patch("datadis.get_max_power", return_value=1337)
async def test_async_update_passed(*args):
    """Test a passed async_update."""
    sensor = DatadisSensor("username", "password", {"cups": "cups"})
    await sensor.async_update()
    assert sensor.available is True
    assert sensor.state == "1337 kWh"


@mock.patch("datadis.get_token")
@mock.patch("datadis.get_supplies")
@mock.patch("datadis.get_max_power")
async def test_async_update_failed(*args):
    """Test a failed async_update."""
    sensor = DatadisSensor("username", "password", {"cups": "cups"})
    await sensor.async_update()
    assert sensor.available is False
