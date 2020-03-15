#!/bin/bash
mkdir -p "data/derived"
cd data/derived
wget -r -np --cut-dirs 2 -nH -N -A '*_JT00_2016.csv.gz,*_xwalk.csv.gz' -R 'us_xwalk.csv.gz' "https://lehd.ces.census.gov/data/lodes/LODES7/"
cd ../..


