import json
import os
import sys
from datetime import datetime

import pandas as pd
from shapely.geometry import shape

def make_df(in_jsonl, out_format, laag):
    # Haal de veldnamen en veldtypen op
    # print(os.path.basename(in_jsonl).split(".")[0])
    f_names = out_format["lagen"][laag]["velden"].keys()


    # Maak een Pandas DataFrame
    df = pd.DataFrame(data=None, columns=f_names)

    # Zet de datatypes aan de hand van de veldtypen uit de dictionary
    for f in f_names:
        f_type = out_format["lagen"][laag]["velden"][f]["veldtype"]
        if f_type == "int":
            df[f] = df[f].astype(int)
        elif f_type == "decimal":
            df[f] = df[f].astype('float64')
        elif f_type == "str":
            df[f] = df[f].astype(str)
        elif f_type == "date":
            df[f] = pd.to_datetime(df[f], format='%Y-%m-%d')
    return df, f_names


def extract_nested_value(data, path):
    """Haalt de geneste waarde uit een dictionary op basis van het pad."""
    keys = path.split(".")
    value = data
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return None
    return value


def read_jsonlines(file_path, f_names, out_format, laag):
    with open(file_path, 'r', encoding='utf-8') as file:
        i = 0
        keys = []
        for line in file:
            i += 1
            if i > 10:
                pass
            if i in range(0, 10000000, 10000):
                print(f"read jsonlines: {i} rows")

            data = json.loads(line)  # Parse de JSON-lijn
            properties = data.get('properties', {})  # Haal de properties op
            if i < 1000:
                for property in properties.keys():
                    if property not in keys:
                        keys.append(property)
            relevant_data = {}

            for field in f_names:
                # Kijk of er een 'source' is opgegeven in out_format
                field_info = out_format["lagen"][laag]["velden"][field]
                source = field_info.get("source", field)  # Gebruik 'source' of het veld zelf als sleutel

                # Als 'source' een genest pad bevat, gebruik extract_nested_value
                if "." in source:
                    relevant_data[field] = extract_nested_value(properties, source)
                else:
                    relevant_data[field] = properties.get(source)

            geometry_type_laag = out_format["lagen"][laag].get("geometry_type", None)

            # print(f"data['geometry']:{data['geometry']}")
            geometry = process_geometry(data['geometry'], geometry_type_laag=geometry_type_laag)
            # print(f"geometry na process geometry:{geometry}")
            # Zet de geometrie om naar een Shapely object
            geometry = shape(geometry)
            relevant_data['geometry'] = geometry  # Voeg de geometrie toe
            # print(f"relevant_data['geometry']:{relevant_data['geometry']}")
            relevant_data['copydatum'] = datetime.now().strftime('%Y-%m-%d')

            yield relevant_data


def remove_m_from_coordinates(coordinates, geometry_type):
    """Remove m-value if present, based on the structure of the first coordinate."""
    if geometry_type in ("Point", "POINT"):
        if len(coordinates) == 4:
            return coordinates[:3]
        elif len(coordinates) == 2:
            return coordinates[:2] + [0]
        else:
            return coordinates
    elif geometry_type in ("MultiLineString", "LineString"):
        if len(coordinates[0]) == 4:  # x, y, z, m
            return [[x, y, z] for x, y, z, _ in coordinates]
        elif len(coordinates[0]) == 2:  # x, y, z, m
            return [[x, y, 0] for x, y in coordinates]
        elif len(coordinates[0]) < 4:  # x, y, z
            return coordinates
        else:
            raise ValueError("Unexpected coordinate length")


def point_to_multilinestring(coordinates):
    coordinates = [[[coordinates[0], coordinates[1], coordinates[2]], [coordinates[0], coordinates[1], coordinates[2]]]]
    return coordinates


def geometrycollection_to_multilinestring(geometry_dict):
    if geometry_dict['geometries'] == []:
        return [[[0, 0], [0, 0]]]

    all_lines = []
    # Itereer door de geometrieën in de GeometryCollection
    for geom in geometry_dict['geometries']:
        geometry_type = geom['type']
        coordinates = geom['coordinates']
        if geometry_type == 'Point':
            new_coordinates = remove_m_from_coordinates(coordinates, geometry_type)
            # Converteer een punt naar een LineString met twee identieke coördinaten
            all_lines.append([new_coordinates, new_coordinates])
        elif geometry_type == 'LineString':
            new_coordinates = remove_m_from_coordinates(coordinates, geometry_type)
            # Voeg LineString toe aan de lijst
            all_lines.append(new_coordinates)
        elif geometry_type == 'MultiLineString':
            new_coordinates = [remove_m_from_coordinates(line, geometry_type) for line in coordinates]
            # Voeg alle lijnen van MultiLineString toe aan de lijst
            all_lines.extend(new_coordinates)

    # Maak een nieuwe MultiLineString GeoJSON
    geometry_dict['type'] = 'MultiLineString'
    geometry_dict['coordinates'] = all_lines
    return all_lines


def process_geometry(geometry_dict, geometry_type_laag=None):
    """Process geometry dictionary to remove m-value where necessary."""
    geometry_type = geometry_dict['type']

    if geometry_type in ('GeometryCollection',):
        new_coordinates = geometrycollection_to_multilinestring(geometry_dict)
    else:
        coordinates = geometry_dict['coordinates']
        if coordinates == []:
            new_coordinates = [[[0, 0], [0, 0]]]
        elif geometry_type in ('Point',):
            new_coordinates = remove_m_from_coordinates(coordinates, geometry_type)
        elif geometry_type in ('LineString',):
            geometry_type_laag = 'MultiLineString'
            new_coordinates = [remove_m_from_coordinates(coordinates, geometry_type)]
        elif geometry_type in ('MultiLineString', 'MULTILINESTRING'):
            new_coordinates = [remove_m_from_coordinates(line, geometry_type) for line in coordinates]
        else:
            raise ValueError(f"Unsupported geometry type:{geometry_type}")

    if geometry_type_laag == "MULTILINESTRING" and geometry_type in ("Point", "POINT"):
        new_coordinates = point_to_multilinestring(new_coordinates)
    geometry_dict['coordinates'] = new_coordinates
    if geometry_type_laag is not None:
        geometry_dict['type'] = geometry_type_laag
    if len(str(new_coordinates)) < 10:
        print(f"voor exit:{new_coordinates}")
        print(f"voor exit:{geometry_dict}")
        sys.exit()

    return geometry_dict
