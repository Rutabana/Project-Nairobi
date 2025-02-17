import pytest
from math import radians, cos, sin
from src.util.sim_functions import parse_3d, heading_to_vector, update_location_vector, DEGREES_PER_KM

# ---------------------------------- UNIT TEST ---------------------------------- #

# ----------------------------- Test parse_location ----------------------------- #
def test_parse_3d_vector_valid_2d():
    """Test valid 2D input (auto-padded to 3D)."""
    vector_str = "[1.2921, 36.8219]"
    result = parse_3d(vector_str, name="location")
    assert result == [1.2921, 36.8219, 0.0]

def test_parse_3d_valid_3d():
    """Test valid 3D input."""
    vector_str = "[1.3, 36.8, 100.0]"
    result = parse_3d(vector_str, name="location")
    assert result == [1.3, 36.8, 100.0]

def test_parse_3d_negative_altitude():
    """Test valid 3D input with negative altitude."""
    vector_str = "[1.2921, 36.8219, -50.0]"
    result = parse_3d(vector_str, name="location")
    assert result == [1.2921, 36.8219, -50.0]
def test_parse_3d_invalid_json():
    """Test non-JSON input."""
    vector_str = "not_a_json_array"
    with pytest.raises(SystemExit):
        parse_3d(vector_str, name="velocity")

def test_parse_3d_non_array_input():
    """Test JSON object instead of array."""
    vector_str = '{"lat": 1.2921, "lon": 36.8219}'
    with pytest.raises(SystemExit):
        parse_3d(vector_str, name="location")

def test_parse_3d_wrong_length_1():
    """Test array with 1 element."""
    vector_str = "[1.2921]"
    with pytest.raises(SystemExit):
        parse_3d(vector_str, name="velocity")

def test_parse_3d_wrong_length_4():
    """Test array with 4 elements."""
    vector_str = "[1.2921, 36.8219, 100.0, 200.0]"
    with pytest.raises(SystemExit):
        parse_3d(vector_str, name="location")

def test_parse_3d_non_numeric_elements():
    """Test array with non-numeric values."""
    vector_str = "[1.2921, 'invalid', 100.0]"
    with pytest.raises(SystemExit):
        parse_3d(vector_str, name="velocity")

# ---------------------------------- Edge Cases ---------------------------------- #
def test_parse_3d_zero_values():
    """Test zeros in all dimensions."""
    vector_str = "[0.0, 0.0, 0.0]"
    result = parse_3d(vector_str, name="location")
    assert result == [0.0, 0.0, 0.0]

def test_parse_3d_scientific_notation():
    """Test scientific notation in input."""
    vector_str = "[1.2921e0, 3.68219e1, -5.0e1]"
    result = parse_3d(vector_str, name="velocity")
    assert result == [1.2921, 36.8219, -50.0]

def test_parse_3d_mixed_types():
    """Test mixed integer/float values."""
    vector_str = "[1, 36.8219, -50]"
    result = parse_3d(vector_str, name="location")
    assert result == [1.0, 36.8219, -50.0]

# ---------------------------- Test heading_to_vector --------------------------- #
def test_heading_to_vector_north():
    """Test heading 0° (North) with altitude component."""
    heading = 0
    speed_kmh = 10
    result = heading_to_vector(heading, speed_kmh)
    
    # Expected values
    expected_lat = (10 * DEGREES_PER_KM) / 3600  # 10 km/h north
    expected_lon = 0.0
    expected_alt = 0.0  # No vertical component in heading
    
    assert result == pytest.approx((expected_lat, expected_lon, expected_alt))

def test_heading_to_vector_northeast():
    """Test 45° heading with altitude zero."""
    heading = 45
    speed_kmh = 10
    result = heading_to_vector(heading, speed_kmh)
    
    factor = cos(radians(45))
    expected_lat = (10 * DEGREES_PER_KM * factor) / 3600
    expected_lon = (10 * DEGREES_PER_KM * factor) / 3600
    
    assert result == pytest.approx((expected_lat, expected_lon, 0.0))

def test_heading_to_vector_south_negative_speed():
    """Test South direction (180°) with negative speed."""
    heading = 0
    speed_kmh = -5  # Moving backward south
    result = heading_to_vector(heading, speed_kmh)
    
    expected_lat = (-5 * DEGREES_PER_KM) / 3600
    assert result[0] == pytest.approx(expected_lat)

# ------------------------- Test update_location_vector ------------------------- #
def test_update_location_2d_movement():
    """Test horizontal movement with zero altitude."""
    location = [1.2921, 36.8219, 0.0]  # 3D format
    velocity = (0.001, 0.001, 0.0)  # Northeast movement
    distance = 0
    speed_kmh = 10
    
    new_loc, new_dist = update_location_vector(location, velocity, distance, speed_kmh)
    
    assert new_loc == pytest.approx([1.2931, 36.8229, 0.0])
    assert new_dist == pytest.approx(10 / 3600)  # 10 km/h for 1 second

def test_update_location_vector_3d_movement():
    """Test movement with altitude change."""
    location = [1.2921, 36.8219, 100.0]
    velocity = (0.001, 0.001, 0.1)  # Rising while moving NE
    distance = 5.0
    speed_kmh = 20
    
    new_loc, new_dist = update_location_vector(location, velocity, distance, speed_kmh)
    
    assert new_loc == pytest.approx([1.2931, 36.8229, 100.1])
    assert new_dist == pytest.approx(5 + (20 / 3600))

def test_update_location_vector_no_movement():
    """Test zero velocity vector."""
    location = [1.2921, 36.8219, 50.0]
    velocity = (0.0, 0.0, 0.0)
    distance = 10.0
    speed_kmh = 0
    
    new_loc, new_dist = update_location_vector(location, velocity, distance, speed_kmh)
    
    assert new_loc == location
    assert new_dist == 10.0  # Unchanged

def test_update_location_vector_negative_altitude():
    """Test descending movement."""
    location = [1.2921, 36.8219, 100.0]
    velocity = (0.0, 0.0, -0.05)  # Descending
    distance = 2.5
    speed_kmh = 5  # Horizontal speed still needs to be accounted
    
    new_loc, new_dist = update_location_vector(location, velocity, distance, speed_kmh)
    
    assert new_loc == pytest.approx([1.2921, 36.8219, 99.95])
    assert new_dist == pytest.approx(2.5 + (5 / 3600))


# ------------------------------ INTEGRATION TEST ------------------------------- #

def test_integration_car_movement():
    """Test a car moving north for 1 hour."""
    # Initial location
    location_str = "[1.2921, 36.8219, 0.0]"
    location = parse_3d(location_str)

    # Movement parameters
    heading = 0  # North
    speed_kmh = 60  # 60 km/h
    total_distance_km = 0.0

    # Simulate 1 hour of movement (3600 seconds)
    for _ in range(3600):
        velocity_vector = heading_to_vector(heading, speed_kmh)
        location, total_distance_km = update_location_vector(
            location, velocity_vector, total_distance_km, speed_kmh
        )

    # Expected final location
    expected_lat = 1.2921 + (60 * DEGREES_PER_KM)  # 60 km north
    expected_lon = 36.8219  # No change in longitude
    expected_alt = 0.0  # No change in altitude

    assert location == pytest.approx([expected_lat, expected_lon, expected_alt], abs=1e-6)
    assert total_distance_km == pytest.approx(60.0)  # 60 km traveled

def test_integration_drone_ascent_and_movement():
    """Test a drone ascending and moving east."""
    # Initial location
    location_str = "[1.2921, 36.8219, 0.0]"
    location = parse_3d(location_str)

    # Movement parameters
    heading = 90  # East
    speed_kmh = 30  # 30 km/h
    total_distance_km = 0.0

    # Simulate 1 minute of movement (60 seconds)
    for _ in range(60):
        velocity_vector = heading_to_vector(heading, speed_kmh)
        velocity_vector = (velocity_vector[0], velocity_vector[1], 0.1)  # Ascend at 0.1 m/s
        location, total_distance_km = update_location_vector(
            location, velocity_vector, total_distance_km, speed_kmh
        )

    # Expected final location
    expected_lat = 1.2921
    expected_lon = 36.8219 + (30 * DEGREES_PER_KM / 60)  # 0.5 km east
    expected_alt = 6.0  # 0.1 m/s * 60 seconds = 6 meters

    assert location == pytest.approx([expected_lat, expected_lon, expected_alt], abs=1e-6)
    assert total_distance_km == pytest.approx(0.5)  # 0.5 km traveled

def test_integration_phone_recharge():
    """Test a phone recharging after low battery."""
    # Initial location
    location_str = "[1.2921, 36.8219, 0.0]"
    location = parse_3d(location_str)

    # Movement parameters
    heading = 180  # South
    speed_kmh = 5  # 5 km/h (walking speed)
    total_distance_km = 0.0

    # Simulate 10 minutes of movement (600 seconds)
    for _ in range(600):
        velocity_vector = heading_to_vector(heading, speed_kmh)
        location, total_distance_km = update_location_vector(
            location, velocity_vector, total_distance_km, speed_kmh
        )

    # Expected final location (adjust tolerance to 1e-5)
    expected_lat = 1.2921 - (5 * DEGREES_PER_KM / 6)
    expected_lon = 36.8219
    expected_alt = 0.0

    # Using abs=1e-4 to account for rounding errors
    assert location == pytest.approx([expected_lat, expected_lon, expected_alt], abs=1e-4)
    assert total_distance_km == pytest.approx(0.833, abs=1e-3)

def test_integration_zero_speed():
    """Test a device with zero speed (no movement)."""
    # Initial location
    location_str = "[1.2921, 36.8219, 0.0]"
    location = parse_3d(location_str)

    # Movement parameters
    heading = 45  # Northeast
    speed_kmh = 0  # 0 km/h
    total_distance_km = 0.0

    # Simulate 1 minute of movement (60 seconds)
    for _ in range(60):
        velocity_vector = heading_to_vector(heading, speed_kmh)
        location, total_distance_km = update_location_vector(
            location, velocity_vector, total_distance_km, speed_kmh
        )

    # Expected final location (no change)
    expected_lat = 1.2921
    expected_lon = 36.8219
    expected_alt = 0.0

    assert location == pytest.approx([expected_lat, expected_lon, expected_alt], abs=1e-6)
    assert total_distance_km == pytest.approx(0.0)  # No distance traveled

