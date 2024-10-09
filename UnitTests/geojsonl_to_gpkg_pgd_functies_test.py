from json_to_gisformat.Geojsonl_to_gpkg_gdb_functies import extract_nested_value


def test_extract_nested_value_missing_key():
    # arrange
    properties = {
        "key1": "value1"
    }
    expected = None

    # act
    result = extract_nested_value(properties, "key_not_existing")

    # assert
    assert result == expected, "Failed test for missing key"

def test_extract_nested_value_nested_dict_0_level():
    # arrange
    properties = {
        "key1": "value1"
    }
    expected = "value1"

    # act
    result = extract_nested_value(properties, "key1")

    # assert
    assert result == expected, f"Failed test_extract_nested_value_nested_dict_0_level {expected}"


def test_extract_nested_value_nested_dict_1_level():
    # arrange
    properties = {
        "key1": {
            "key2": "value2"
        }
    }
    expected = "value2"

    # act
    result = extract_nested_value(properties, "key1.key2")

    # assert
    assert result == expected, f"Failed test_extract_nested_value_nested_dict_1_level {expected}"


def test_extract_nested_value_nested_dict_2_levels():
    # arrange
    properties = {
        "key1": {
            "key2": {
                "key3": "value3"
            }
        }
    }
    expected = "value3"

    # act
    result = extract_nested_value(properties, "key1.key2.key3")

    # assert
    assert result == expected, f"Failed test_extract_nested_value_nested_dict_2_levels {expected}"