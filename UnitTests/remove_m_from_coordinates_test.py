import pytest

from json_to_gisformat.Geojsonl_to_gpkg_gdb_functies import remove_m_from_coordinates


def test_remove_m_from_coordinates_raise_value_error():
    # arrange
    coordinates = [[0, 0, 0, 0, 0]]
    geometry_type = 'MultiLineString'

    # act + assert
    with pytest.raises(ValueError) as e:
        remove_m_from_coordinates(coordinates, geometry_type)
    assert str(e.value) == "Unexpected coordinate length"
