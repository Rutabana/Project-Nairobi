import pytest
import time
import json
from src.ec2.iot_devices.phone import Phone, LOW_BATTERY_THRESHOLD, BATTERY_DECREMENT, CHARGE_RATE, WALKING_SPEED_KMH
from src.util.sim_functions import heading_to_vector, update_location_vector

@pytest.fixture
def phone_instance():
    # Start with a fixed location and heading; test mode enabled to avoid Kinesis calls.
    return Phone("phone-123", [1.2921, 36.8219, 0.0], 90, test=True)

def test_initialization(phone_instance):
    # Verify that the Phone instance is correctly initialized.
    assert phone_instance.device_id == "phone-123"
    assert phone_instance.location == [1.2921, 36.8219, 0.0]
    assert phone_instance.heading == 90
    assert phone_instance.speed_kmh == WALKING_SPEED_KMH
    assert phone_instance.battery == 100.0
    assert phone_instance.is_charging is False

def test_update_battery_drain(phone_instance):
    # Set battery above the threshold and test battery drain.
    phone_instance.battery = 50.0
    phone_instance.is_charging = False
    phone_instance.update_battery()
    assert phone_instance.battery == pytest.approx(50.0 - BATTERY_DECREMENT)

def test_update_battery_start_charging(phone_instance):
    # When battery falls below or equal to LOW_BATTERY_THRESHOLD, charging should start.
    phone_instance.battery = 15.0
    phone_instance.is_charging = False
    phone_instance.update_battery()
    assert phone_instance.is_charging is True

def test_update_battery_charging(phone_instance):
    # When charging, battery should increase by CHARGE_RATE.
    phone_instance.battery = 90.0
    phone_instance.is_charging = True
    phone_instance.update_battery()
    assert phone_instance.battery == pytest.approx(min(100.0, 90.0 + CHARGE_RATE))
    # If battery reaches 95 or above, it should stop charging.
    phone_instance.battery = 94.5
    phone_instance.is_charging = True
    phone_instance.update_battery()
    # Depending on CHARGE_RATE, battery may reach or exceed 95.
    if phone_instance.battery >= 95.0:
        assert phone_instance.is_charging is False

def test_update_heading_changes(monkeypatch, phone_instance):
    # Force random.randint to always return 1 so that heading is updated.
    monkeypatch.setattr("random.randint", lambda a, b: 1)
    # Force random.choice to return a specific value.
    monkeypatch.setattr("random.choice", lambda choices: 180)
    phone_instance.is_charging = False  # Ensure heading update is allowed.
    phone_instance.heading = 90  # initial heading
    phone_instance.update_heading()
    assert phone_instance.heading == 180

def test_update_heading_no_change(monkeypatch, phone_instance):
    # Force random.randint to return a value other than 1 so heading remains the same.
    monkeypatch.setattr("random.randint", lambda a, b: 2)
    original_heading = phone_instance.heading
    phone_instance.update_heading()
    assert phone_instance.heading == original_heading

def test_update_location_when_moving(phone_instance):
    # When not charging, location should update.
    phone_instance.is_charging = False
    original_location = phone_instance.location.copy()
    original_total_distance = phone_instance.total_distance_km
    phone_instance.update_location()
    # Location should change from the original
    assert phone_instance.location != original_location
    # And total distance should increase.
    assert phone_instance.total_distance_km > original_total_distance

def test_update_location_when_charging(phone_instance):
    # When charging, location should remain the same.
    phone_instance.is_charging = True
    original_location = phone_instance.location.copy()
    original_total_distance = phone_instance.total_distance_km
    phone_instance.update_location()
    assert phone_instance.location == original_location
    assert phone_instance.total_distance_km == original_total_distance

def test_get_payload(phone_instance):
    # Check that the payload has the expected structure.
    phone_instance.battery = 82.5
    phone_instance.is_charging = False
    payload = phone_instance.get_payload()
    assert payload["deviceId"] == "phone-123"
    # Timestamp should be an int and location remains as a list of three floats.
    assert isinstance(payload["timestamp"], int)
    assert isinstance(payload["location"], list)
    assert len(payload["location"]) == 3
    assert payload["battery"] == 82.5
    assert payload["status"] == "moving"

def test_simulate_step(monkeypatch, phone_instance):
    # Test one simulation step.
    # Patch time.sleep to avoid delay.
    monkeypatch.setattr(time, "sleep", lambda s: None)
    # We can patch update_heading to keep heading stable for predictable location update.
    monkeypatch.setattr(phone_instance, "update_heading", lambda: None)
    original_location = phone_instance.location.copy()
    payload = phone_instance.simulate_step()
    # Verify payload structure and that location or battery state has updated.
    assert "deviceId" in payload
    assert "timestamp" in payload
    assert "location" in payload
    # If not charging, location should have changed.
    if not phone_instance.is_charging:
        assert phone_instance.location != original_location
