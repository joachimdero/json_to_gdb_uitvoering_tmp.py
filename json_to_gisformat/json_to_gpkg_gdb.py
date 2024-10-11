import cProfile
import json
import os
import logging
from datetime import datetime
import polars as pl
import geopandas as gpd
from Geojsonl_to_gpkg_gdb_functies import make_df, read_jsonlines

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Stel het laagste niveau in (bijv. DEBUG), zodat alles wordt gelogd
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(r"C:\awvData\awvDataTools\log_json_to_gpkg_gdb.log"),  # Log naar een bestand
        logging.StreamHandler()  # Log naar de console
    ]
)
logging.info("start LOG")


def main():
    out_format_json = r"/home/davidlinux/PycharmProjects/json_to_gdb_uitvoering_tmp.py/json_to_gisformat/out_format.json"
    with open(out_format_json, 'r') as file:
        out_format = json.load(file)
    in_jsonl_path = r"/home/davidlinux/PycharmProjects/json_to_gdb_uitvoering_tmp.py/inputfiles"
    i = 0
    for laag in out_format["lagen"]:
        i += 1
        logging.info(f"start verwerking laag {i}.{laag}")
        if laag not in [
            'fietssuggestiestroken_wrapp'
        ]: continue

        try:
            in_jsonl = os.path.join(in_jsonl_path, laag + ".json")
            df, f_names = make_df(out_format, laag)

            # Voeg data toe aan het bestaande DataFrame
            new_data = pl.DataFrame(read_jsonlines(in_jsonl, f_names, out_format, laag))

            # Gebruik pd.concat om de nieuwe data toe te voegen aan het bestaande DataFrame
            df = pl.concat([new_data, df], how="diagonal")

            # Zet de 'copydatum' kolom om naar een datetime-object
            df.cast({'copydatum': pl.Date})

            pandas_df = df.to_pandas(use_pyarrow_extension_array=True)
            # Zet het DataFrame om naar een GeoDataFrame
            gdf = gpd.GeoDataFrame(pandas_df, geometry=pandas_df['geometry'], crs=31370)

            # Controleer het resultaat
            logging.info(f"Aantal rijen in het DataFrame: {gdf.shape[0]}")

            # Exporteer het GeoDataFrame naar een GeoPackage
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  maak geopackage")
            gdf.to_file(r"/home/davidlinux/PycharmProjects/json_to_gdb_uitvoering_tmp.py/outputfiles/AwvData.gpkg", layer=laag, driver="GPKG")
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  maak OpenFileGDB")
            gdf.to_file(r"/home/davidlinux/PycharmProjects/json_to_gdb_uitvoering_tmp.py/outputfiles/AwvData.gdb", layer=laag, driver="OpenFileGDB")

        except FileNotFoundError as e:
            logging.error(f"Bestand niet gevonden voor laag {laag}: {e}")
        except ValueError as e:
            logging.error(f"Waarde fout bij het verwerken van laag {laag}: {e}")
        except Exception as e:
            raise e
            logging.error(f"Onverwachte fout bij het verwerken van laag {laag}: {e}")
    logging.info("stop LOG")

if __name__ == '__main__':
    cProfile.run('main()')
