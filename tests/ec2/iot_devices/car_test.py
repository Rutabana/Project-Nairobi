import pytest
import time
import json
from src.ec2.iot_devices.car import Car, GAS_DECREMENT, GAS_REFILL_AMOUNT, GAS_REFILL_THRESHOLD
from src.util.sim_functions import heading_to_vector, update_location_vector

@pytest.fixture
def car_instance():
    """
    Fixture that creates a Car instance with a fixed starting location and heading.
    To avoid randomness in tests, we manually set speed after initialization.
    """
    car = Car("car-123", [1.2921, 36.8219, 0.0], 90, test=True)
    car.speed_kmh = 60  # Fix the speed for deterministic testing
    return car

def test_initialization(car_instance):
    assert car_instance.device_id == "car-123"
    assert car_instance.location == [1.2921, 36.8219, 0.0]
    assert car_instance.heading == 90
    assert car_instance.speed_kmh == 60
    assert car_instance.total_distance_km == 0.0
    assert car_instance.gas == GAS_REFILL_AMOUNT

def test_update_heading_changes(monkeypatch, car_instance):
    # Force random.randint to always return 1 so heading is updated.
    monkeypatch.setattr("random.randint", lambda a, b: 1)
    # Force random.choice to return a specific new heading, e.g. 180.
    monkeypatch.setattr("random.choice", lambda choices: 180)
    original_heading = car_instance.heading
    car_instance.update_heading()
    assert car_instance.heading == 180

def test_update_heading_no_change(monkeypatch, car_instance):
    # Force random.randint to always return a value other than 1.
    monkeypatch.setattr("random.randint", lambda a, b: 2)
    original_heading = car_instance.heading
    car_instance.update_heading()
    assert car_instance.heading == original_heading

def test_update_gas_consumption(monkeypatch, car_instance):
    # Test gas consumption without refill.
    car_instance.gas = 80.0
    # Force random.randint (for refill chance) to return a value that does not trigger refill.
    monkeypatch.setattr("random.randint", lambda a, b: 5)
    car_instance.update_gas()
    expected_gas = round(80.0 - GAS_DECREMENT, 1)
    assert car_instance.gas == expected_gas

def test_update_gas_refill(monkeypatch, car_instance):
    # Test that gas refills if below or equal to threshold.
    car_instance.gas = GAS_REFILL_THRESHOLD
    # Force random.randint to trigger refill (i.e. return 1).
    monkeypatch.setattr("random.randint", lambda a, b: 1)
    car_instance.update_gas()
    assert car_instance.gas == GAS_REFILL_AMOUNT

def test_update_location(car_instance):
    # Test that update_location properly updates location and total distance.
    original_location = car_instance.location.copy()
    original_distance = car_instance.total_distance_km
    car_instance.update_location()
    # The new location should differ from the original.
    assert car_instance.location != original_location
    # Total distance should have increased.
    assert car_instance.total_distance_km > original_distance

def test_get_payload(car_instance):
    payload = car_instance.get_payload()
    assert payload["deviceId"] == "car-123"
    assert isinstance(payload["timestamp"], int)
    assert isinstance(payload["location"], list)
    assert len(payload["location"]) == 3
    assert payload["gas"] == car_instance.gas

def test_simulate_step(monkeypatch, car_instance):
    # Patch update_heading to avoid randomness during this test.
    monkeypatch.setattr(car_instance, "update_heading", lambda: None)
    original_location = car_instance.location.copy()
    payload = car_instance.simulate_step()
    # Verify the payload has the required keys.
    assert "deviceId" in payload
    assert "timestamp" in payload
    assert "location" in payload
    assert "gas" in payload
    # Check that location has been updated.
    assert car_instance.location != original_location
