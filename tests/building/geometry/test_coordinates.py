from intramaps.building.geometry.coordinates import Coordinates
from pytest import approx, raises
def test_distance_to():
    point1 = Coordinates(0, 0, 0)
    point2 = Coordinates(3, 4, 0)
    assert point1.distance_to(point2) == approx(5.0)
    assert point2.distance_to(point1) == approx(5.0)
    assert point1.distance_to(point1) == approx(0.0)

    point3 = Coordinates(1, 1, 1)
    with raises(ValueError):
        point1.distance_to(point3)
    with raises(ValueError):
        point4 = Coordinates(1, 1, 0.5)
    with raises(ValueError):
        point5 = Coordinates("1", 1, 0)
