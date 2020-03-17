#!/bin/bash

if [ ! -d "data/raw/LODES7" ]
then
    bash collected_lodes_data.sh
fi

if [ ! -d "data/derived/lodes_tract" ]
then
    python aggregate_lodes_tract_level.py
fi

python construct_county_network.py -s ma -o massachusetts -m 1
python construct_town_network.py -s ma -o massachusetts -m 1
python construct_tract_network.py -s ma -o massachusetts -m 1
#python construct_block_network.py -s ma -o massachusetts -m 1

python construct_county_network.py -o national -m 1
python construct_town_network.py -o national -m 1
python construct_tract_network.py -o national -m 1
