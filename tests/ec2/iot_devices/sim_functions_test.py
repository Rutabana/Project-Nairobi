import pytest
from math import radians, cos, sin
from src.util.sim_functions import parse_location, heading_to_vector, update_location_vector, DEGREES_PER_KM

# ---------------------------------- UNIT TEST ---------------------------------- #

# ----------------------------- Test parse_location ----------------------------- #
def test_parse_location_valid():
    assert parse_location("[1.2921, 36.8219]") == [1.2921, 36.8219] # No Altitude
    assert parse_location("[1.3, 36.8, 100.0]") == [1.3, 36.8, 100.0] # Altitude

def test_parse_location_invalid():
    with pytest.raises(SystemExit):
        parse_location("not_a_json_array")

# ---------------------------- Test heading_to_vector --------------------------- #
def test_heading_to_vector_north():
    """Test heading_to_vector for North direction."""
    heading = 0  # North
    speed_kmh = 10  # 10 km/h
    delta_lat, delta_lon = heading_to_vector(heading, speed_kmh)

    # Expected: North movement (positive delta_lat, zero delta_lon)
    expected_delta_lat = (speed_kmh * DEGREES_PER_KM) / 3600  # Degrees per second
    expected_delta_lon = 0.0

    assert delta_lat == pytest.approx(expected_delta_lat)
    assert delta_lon == pytest.approx(expected_delta_lon)

def test_heading_to_vector_east():
    """Test heading_to_vector for East direction."""
    heading = 90  # East
    speed_kmh = 10  # 10 km/h
    delta_lat, delta_lon = heading_to_vector(heading, speed_kmh)

    # Expected: East movement (zero delta_lat, positive delta_lon)
    expected_delta_lat = 0.0
    expected_delta_lon = (speed_kmh * DEGREES_PER_KM) / 3600  # Degrees per second

    assert delta_lat == pytest.approx(expected_delta_lat)
    assert delta_lon == pytest.approx(expected_delta_lon)

def test_heading_to_vector_northeast():
    """Test heading_to_vector for Northeast direction."""
    heading = 45  # Northeast
    speed_kmh = 10  # 10 km/h
    delta_lat, delta_lon = heading_to_vector(heading, speed_kmh)

    # Expected: Northeast movement (equal delta_lat and delta_lon)
    expected_delta = (speed_kmh * DEGREES_PER_KM) / 3600 * cos(radians(45))  # Degrees per second
    assert delta_lat == pytest.approx(expected_delta)
    assert delta_lon == pytest.approx(expected_delta)

# ------------------------- Test update_location_vector ------------------------- #
def test_update_location_vector_north():
    """Test update_location_vector for North movement."""
    location = [-1.2921, 36.8219]  # Nairobi coordinates
    velocity_vector = (0.001, 0.0)  # North movement (delta_lat = 0.001°/s, delta_lon = 0)
    total_distance_km = 0
    speed_kmh = 10  # 10 km/h

    new_location, updated_distance = update_location_vector(location, velocity_vector, total_distance_km, speed_kmh)

    # Expected new location
    expected_lat = location[0] + velocity_vector[0]
    expected_lon = location[1] + velocity_vector[1]
    assert new_location == [round(expected_lat, 6), round(expected_lon, 6)]

    # Expected distance
    expected_distance = total_distance_km + (speed_kmh / 3600)  # km per second
    assert updated_distance == pytest.approx(expected_distance)

def test_update_location_vector_northeast():
    """Test update_location_vector for Northeast movement."""
    location = [-1.2921, 36.8219]  # Nairobi coordinates
    velocity_vector = (0.001, 0.001)  # Northeast movement (delta_lat = 0.001°/s, delta_lon = 0.001°/s)
    total_distance_km = 0
    speed_kmh = 10  # 10 km/h

    new_location, updated_distance = update_location_vector(location, velocity_vector, total_distance_km, speed_kmh)

    # Expected new location
    expected_lat = location[0] + velocity_vector[0]
    expected_lon = location[1] + velocity_vector[1]
    assert new_location == [round(expected_lat, 6), round(expected_lon, 6)]

    # Expected distance
    expected_distance = total_distance_km + (speed_kmh / 3600)  # km per second
    assert updated_distance == pytest.approx(expected_distance)

def test_update_location_vector_no_movement():
    """Test update_location_vector for no movement."""
    location = [-1.2921, 36.8219]  # Nairobi coordinates
    velocity_vector = (0.0, 0.0)  # No movement
    total_distance_km = 0
    speed_kmh = 0  # 0 km/h

    new_location, updated_distance = update_location_vector(location, velocity_vector, total_distance_km, speed_kmh)

    # Expected: No change in location or distance
    assert new_location == [round(location[0], 6), round(location[1], 6)]
    assert updated_distance == 0.0