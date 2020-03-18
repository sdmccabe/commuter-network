#!/bin/bash

# collect Gazetteer files
if [ ! -f "data/raw/2019_Gaz_counties_national.txt" ]
then
    wget -P "data/raw/" "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2019_Gazetteer/2019_Gaz_counties_national.zip"
    unzip "data/raw/2019_Gaz_counties_national.zip" -d data/raw
fi

if [ ! -f "data/raw/2019_Gaz_cousubs_national.txt" ]
then
    wget -P "data/raw/" "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2019_Gazetteer/2019_Gaz_cousubs_national.zip"
    unzip "data/raw/2019_Gaz_cousubs_national.zip" -d data/raw
fi

if [ ! -f "data/raw/2019_Gaz_tracts_national.txt" ]
then
    wget -P "data/raw/" "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2019_Gazetteer/2019_Gaz_tracts_national.zip"
    unzip "data/raw/2019_Gaz_tracts_national.zip" -d data/raw
fi

# collect ACS commuter flow data
if [ ! -f "data/raw/table1.xlsx" ]
then
    wget -P "data/raw/" "https://www2.census.gov/programs-surveys/demo/tables/metro-micro/2015/commuting-flows-2015/table1.xlsx"
fi

if [ ! -f "data/raw/table3.xlsx" ]
then
    wget -P "data/raw/" "https://www2.census.gov/programs-surveys/demo/tables/metro-micro/2015/commuting-flows-2015/table3.xlsx"
fi

# collect and aggregate LODES data
if [ ! -d "data/raw/LODES7/wy" ]
then
    bash collect_lodes_data.sh
fi

if [ ! -f "data/derived/lodes_tract/wy_flow.csv.gz" ]
then
    python aggregate_lodes_tract_level.py
fi

# collect ACS population data
if [ ! -d "data/raw/population_data/wy" ]
then
    python collect_population_data.py
fi

# run example scripts
python construct_county_network.py -s ma -o massachusetts -m 1
python construct_town_network.py -s ma -o massachusetts -m 1
python construct_tract_network.py -s ma -o massachusetts -m 1
#python construct_block_network.py -s ma -o massachusetts -m 1

python construct_county_network.py -o national -m 1
python construct_town_network.py -o national -m 1
python construct_tract_network.py -o national -m 1
