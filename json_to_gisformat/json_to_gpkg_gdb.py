import json
import os.path
from sys import exception

import pandas as pd
import geopandas as gpd

from Geojsonl_to_gpkg_gdb_functies import make_df, read_jsonlines

out_format_json = "json_to_gisformat/out_format.json"
with open(out_format_json, 'r') as file:
    out_format = json.load(file)
in_jsonl_path = r"C:\awvData\downloadGeolatteNoSqlFeatureserver"

# ---------------------------------------
i=0
for laag in out_format["lagen"] :
    i+=1
    if laag == 'wegenregister':
        pass
    if laag != 'innames':
        pass
    if i < 14:
        continue
    try:
        print(f"start verwerking laag {i}. {laag}")
        in_jsonl = os.path.join(in_jsonl_path,laag+".json")
        df, f_names = make_df(in_jsonl,out_format,laag)
        # Voeg data toe aan het bestaande DataFrame
        new_data = pd.DataFrame(read_jsonlines(in_jsonl,f_names,out_format,laag))
        # print(f"newdata:\n{new_data}")
        # print(f"volledige lijn new_data:\n{new_data.iloc[0]}")
        # print(f"newdata.dtypes:\n{new_data.dtypes}")

        # Gebruik pd.concat om de nieuwe data toe te voegen aan het bestaande DataFrame
        df = pd.concat([df, new_data], ignore_index=True)
        # print(f"df:\n{df}")
        # print(f"df.dtypes:\n{df.dtypes}")
        # print(f"volledige lijn df:\n{df.iloc[0]}")  # Vervang 0 door het rijnummer dat je volledig wilt zien

        # Zet het DataFrame om naar een GeoDataFrame
        gdf = gpd.GeoDataFrame(df, geometry=df['geometry'], crs=31370)


        # Controleer het resultaat
        # print(f"gdf.dtypes:{df.dtypes}")
        # print(f"volledige lijn gdf:\n{df.iloc[0]}")
        print(f"Aantal rijen in het DataFrame: {gdf.shape[0]}")

        # Exporteer het GeoDataFrame naar een GeoPackage
        gdf.to_file(r"C:\awvData\AwvData.gpkg", layer=laag, driver="GPKG")
        gdf.to_file(r"C:\awvData\AwvData.gdb", layer=laag, driver="OpenFileGDB")


    except FileNotFoundError as e:
        print(f"Bestand niet gevonden voor laag {laag}: {e}")
    except ValueError as e:
        print(f"Waarde fout bij het verwerken van laag {laag}: {e}")

