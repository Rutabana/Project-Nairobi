import pytest
import time
from src.ec2.iot_devices.drone import Drone, BATTERY_DECREMENT, LOW_BATTERY_THRESHOLD, CHARGE_RATE, DESCENT_RATE
from src.util.sim_functions import heading_to_vector, update_location_vector

@pytest.fixture
def drone_instance(monkeypatch):
    """
    Fixture that creates a Drone instance with a fixed starting location, heading, and speed.
    Randomness is controlled by monkeypatching:
      - random.randint always returns 40 (for speed)
      - random.uniform always returns 0.05 (for altitude change)
    """
    monkeypatch.setattr("random.randint", lambda a, b: 40)
    monkeypatch.setattr("random.uniform", lambda a, b: 0.05)
    # Starting with an altitude of 10.0 for predictability.
    return Drone("drone-123", [1.2921, 36.8219, 10.0], 90, test=True)

def test_initialization(drone_instance):
    assert drone_instance.device_id == "drone-123"
    assert drone_instance.location == [1.2921, 36.8219, 10.0]
    assert drone_instance.heading == 90
    # Speed is fixed to 40 by monkeypatch.
    assert drone_instance.speed_kmh == 40
    assert drone_instance.total_distance_km == 0.0
    assert drone_instance.battery == 100.0
    assert drone_instance.is_descending is False
    assert drone_instance.is_landed is False

def test_update_battery_landed(drone_instance):
    # When landed, battery should increase.
    drone_instance.is_landed = True
    drone_instance.battery = 90.0
    drone_instance.update_battery()
    expected_battery = min(100.0, 90.0 + CHARGE_RATE)
    assert drone_instance.battery == pytest.approx(expected_battery)
    # If battery reaches or exceeds 95, the drone should resume flight.
    drone_instance.battery = 94.0
    drone_instance.is_landed = True
    drone_instance.update_battery()
    assert drone_instance.is_landed is False
    assert drone_instance.is_descending is False

def test_update_battery_start_descending(drone_instance):
    # If battery is low and not already descending, it should start descending.
    drone_instance.battery = LOW_BATTERY_THRESHOLD
    drone_instance.is_descending = False
    drone_instance.is_landed = False
    drone_instance.update_battery()
    assert drone_instance.is_descending is True

def test_update_battery_descending(drone_instance):
    # When descending, battery should drop faster.
    drone_instance.is_descending = True
    initial_battery = 50.0
    drone_instance.battery = initial_battery
    drone_instance.update_battery()
    expected_battery = max(0.0, initial_battery - BATTERY_DECREMENT * 2)
    assert drone_instance.battery == pytest.approx(expected_battery)

def test_update_movement_normal(drone_instance):
    # When flying normally, the drone's location should update.
    drone_instance.is_descending = False
    drone_instance.is_landed = False
    original_location = drone_instance.location.copy()
    original_distance = drone_instance.total_distance_km
    drone_instance.update_movement()
    assert drone_instance.location != original_location
    assert drone_instance.total_distance_km > original_distance

def test_update_movement_descending(drone_instance):
    # When descending (and not yet landed), altitude should decrease by DESCENT_RATE.
    drone_instance.is_descending = True
    drone_instance.is_landed = False
    drone_instance.location[2] = 5.0  # Ensure altitude is high enough.
    original_location = drone_instance.location.copy()
    drone_instance.update_movement()
    expected_alt = round(original_location[2] - DESCENT_RATE, 6)
    assert pytest.approx(drone_instance.location[2], rel=1e-6) == expected_alt

def test_update_movement_landed(drone_instance):
    # If descending causes the altitude to drop to 0 or below, the drone should land.
    drone_instance.is_descending = True
    drone_instance.is_landed = False
    drone_instance.location[2] = 0.0  # Drone at ground level.
    original_location = drone_instance.location.copy()
    drone_instance.update_movement()
    assert drone_instance.is_landed is True
    # When landed, velocity should be zero so the location remains unchanged.
    assert drone_instance.location == original_location

def test_get_payload(drone_instance):
    payload = drone_instance.get_payload()
    assert payload["deviceId"] == "drone-123"
    assert isinstance(payload["timestamp"], int)
    assert isinstance(payload["location"], list)
    assert len(payload["location"]) == 3
    # Status should be "flying" in normal flight.
    assert payload["status"] == "flying"
    assert payload["battery"] == round(drone_instance.battery, 1)

def test_simulate_step(monkeypatch, drone_instance):
    # Patch time.sleep to avoid delay during tests.
    monkeypatch.setattr(time, "sleep", lambda s: None)
    original_location = drone_instance.location.copy()
    payload = drone_instance.simulate_step()
    # Verify the payload structure.
    assert "deviceId" in payload
    assert "timestamp" in payload
    assert "location" in payload
    assert "battery" in payload
    # Confirm that location was updated.
    assert drone_instance.location != original_location
