# commuter-network
Python code for constructing commuter networks from Census data.

These scripts all produce commuter networks as GraphML objects. There are
various relevant node and edge attributes; not all are present in each graph:

Node:
- `name`: the node names correspond to FIPS codes for a particular level
   of granularity
- `state`, `county`: straightforward descriptives 
- `town`: in states where available, the name of the relevant [minor civil divisions](https://en.wikipedia.org/wiki/Minor_civil_division)
- `block`, `tract`: Census administrative units
- `latitude`, `longitude`: coordinates for the relevant spatial unit, drawn from 2019
   [Census gazetteer files](https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html)

Edge:
- `weight`: the amount of commuting traffic between the edges
- `margin`: the uncertainty around this magnitude, where available

`construct_county_network.py` creates a weighted edgelist of commuting flows
between counties, drawn from Table 1 of the [2011-2015 5-Year ACS Commuting Flows
dataset](https://www.census.gov/data/tables/2015/demo/metro-micro/commuting-flows-2015.html).

`construct_town_network.py` creates a weighted edgelist of commuting flows
between minor civil divisions (where available; counties where not available),
drawn from Table 3 of the [2011-2015 5-Year ACS Commuting Flows
dataset](https://www.census.gov/data/tables/2015/demo/metro-micro/commuting-flows-2015.html).
