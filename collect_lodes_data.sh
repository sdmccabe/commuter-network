#!/bin/bash
mkdir -p "data/raw"
cd data/raw
wget -r -np --cut-dirs 2 -nH -N -A '*_JT00_2016.csv.gz,*_xwalk.csv.gz' -R 'us_xwalk.csv.gz' -X "LODES7/*/wac/,LODES7/*/rac/" "https://lehd.ces.census.gov/data/lodes/LODES7/"
cd ../..


