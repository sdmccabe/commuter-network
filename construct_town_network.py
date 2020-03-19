import networkx as nx
import pandas as pd
import argparse
from pathlib import Path
from state_fips_mapping import STATE_TO_FIPS


# This script uses the following data files:
#
# table3.xlsx: https://www.census.gov/data/tables/2015/demo/metro-micro/commuting-flows-2015.html
# 2019_Gaz_cousubs_national.txt: https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html
# 2019_Gaz_counties_national.txt: https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html


SCHEMA = {
    "source_state_fips_code": str,
    "source_county_fips_code": str,
    "source_mcd_fips_code": str,
    "source_state_name": str,
    "source_county_name": str,
    "source_mcd_name": str,
    "target_state_fips_code": str,
    "target_county_fips_code": str,
    "target_mcd_fips_code": str,
    "target_state_name": str,
    "target_county_name": str,
    "target_mcd_name": str,
    "weight": "Int64",
    "margin": str,
}


def parseint(s):
    try:
        return int(s)
    except ValueError:
        s = s.replace(",", "")
        return int(s)


def construct_fips(state, county, mcd):
    return state + county + mcd


def construct_network(states, minimum_weight, output):
    df = pd.read_excel(
        "data/raw/table3.xlsx",
        skiprows=7,
        header=None,
        names=SCHEMA.keys(),
        dtype=SCHEMA,
    )
    df = df.loc[pd.notnull(df["weight"]), :]

    # Because there is a mixture of MCD-level and county-level flow,
    # we need to bring in both gazetteers. Note that we will be padding
    # out county-only FIPS codes to the 10-digit MCD code by adding zeros.
    town_gazetteer = pd.read_csv(
        "data/raw/2019_Gaz_cousubs_national.txt", sep="\t", dtype={"GEOID": str},
    )
    town_gazetteer.columns = [x.strip() for x in town_gazetteer.columns]
    town_gazetteer = town_gazetteer.loc[:, ["GEOID", "INTPTLONG", "INTPTLAT"]]

    county_gazetteer = pd.read_csv(
        "data/raw/2019_Gaz_counties_national.txt", sep="\t", dtype={"GEOID": str},
    )
    county_gazetteer.columns = [x.strip() for x in county_gazetteer.columns]
    county_gazetteer = county_gazetteer.loc[:, ["GEOID", "INTPTLONG", "INTPTLAT"]]
    county_gazetteer["GEOID"] = county_gazetteer["GEOID"] + "00000"
    gazetteer = pd.concat([county_gazetteer, town_gazetteer])

    source_gazetteer = gazetteer.rename(
        {
            "INTPTLONG": "source_longitude",
            "INTPTLAT": "source_latitude",
            "GEOID": "source_fips",
        },
        axis=1,
    )

    target_gazetteer = gazetteer.rename(
        {
            "INTPTLONG": "target_longitude",
            "INTPTLAT": "target_latitude",
            "GEOID": "target_fips",
        },
        axis=1,
    )

    # restrict nodes to the 50 states + DC
    df = df.loc[0 < df["target_state_fips_code"].astype(float), :]
    df = df.loc[0 < df["source_state_fips_code"].astype(float), :]
    df = df.loc[df["target_state_fips_code"].astype(float) <= 56, :]
    df = df.loc[df["source_state_fips_code"].astype(float) <= 56, :]

    df = df.loc[df["weight"] >= int(minimum_weight), :]

    df["weight"] = df["weight"].apply(parseint)
    df["margin"] = df["margin"].apply(parseint)

    # As discussed above, we have a mixture of MCD and county-level nodes.
    df["source_mcd_name"] = df["source_mcd_name"].fillna("")
    df["target_mcd_name"] = df["target_mcd_name"].fillna("")
    df["source_mcd_fips_code"] = df["source_mcd_fips_code"].fillna("00000")
    df["target_mcd_fips_code"] = df["target_mcd_fips_code"].fillna("00000")

    # Strip initial zero in state FIPS codes for target. The spreadsheet
    # has state FIPS as a three-digit number to allow for Canada.
    df["target_state_fips_code"] = df["target_state_fips_code"].str[1:]

    # Restrict to the desired states
    if states is not None:
        STATES = [x.strip().lower() for x in states.split(",")]
        STATE_FIPS = [STATE_TO_FIPS[x] for x in STATES]
        df = df.loc[df["target_state_fips_code"].isin(STATE_FIPS), :]
        df = df.loc[df["source_state_fips_code"].isin(STATE_FIPS), :]
    else:
        STATES = STATE_TO_FIPS.keys()

    pop_metadatas = []
    for state in STATES:
        pop = pd.read_csv(
            f"data/raw/population_data/town/{state}.tsv",
            sep="\t",
            dtype={"FIPS": "str"},
        )
        pop_metadatas.append(pop)
    pop_metadata = pd.concat(pop_metadatas, axis=0, ignore_index=True)
    del pop_metadatas

    # Simple concatenation of component FIPS codes.
    df["source_fips"] = df.apply(
        lambda row: construct_fips(
            row.source_state_fips_code,
            row.source_county_fips_code,
            row.source_mcd_fips_code,
        ),
        axis=1,
    )

    df["target_fips"] = df.apply(
        lambda row: construct_fips(
            row.target_state_fips_code,
            row.target_county_fips_code,
            row.target_mcd_fips_code,
        ),
        axis=1,
    )

    df = df.loc[df["source_fips"].apply(lambda s: len(s) == 10), :]
    df = df.loc[df["target_fips"].apply(lambda s: len(s) == 10), :]

    df = df.merge(pop_metadata, "left", left_on="target_fips", right_on="FIPS")
    del pop_metadata

    df = df.merge(source_gazetteer, how="left", on="source_fips",)
    df = df.merge(target_gazetteer, how="left", on="target_fips",)

    # Construct the graph with edge attributes.
    G = nx.from_pandas_edgelist(
        df,
        "source_fips",
        "target_fips",
        edge_attr=["weight", "margin"],
        create_using=nx.DiGraph(),
    )

    # Node attributes are a bit trickier. It's unlikely, but just to make sure
    # we don't miss any metadata, we combine the source and target information
    # about locations.
    target_attr_df = (
        df.set_index("target_fips")
        .loc[:, ["target_state_name", "target_county_name", "target_mcd_name"]]
        .rename(
            {
                "target_state_name": "state",
                "target_county_name": "county",
                "target_mcd_name": "town",
            },
            axis=1,
        )
    )
    source_attr_df = (
        df.set_index("source_fips")
        .loc[:, ["target_state_name", "target_county_name", "target_mcd_name"]]
        .rename(
            {
                "target_state_name": "state",
                "target_county_name": "county",
                "target_mcd_name": "town",
            },
            axis=1,
        )
    )
    lat_dict = gazetteer.set_index("GEOID")["INTPTLAT"].to_dict()
    long_dict = gazetteer.set_index("GEOID")["INTPTLONG"].to_dict()

    state_dict = target_attr_df["state"].to_dict()
    state_dict.update(source_attr_df["state"].to_dict())
    county_dict = target_attr_df["county"].to_dict()
    county_dict.update(source_attr_df["county"].to_dict())
    town_dict = target_attr_df["town"].to_dict()
    town_dict.update(source_attr_df["town"].to_dict())

    # With the node attribute dicts created, we can set node attributes and
    # then write to files.

    nx.set_node_attributes(G, state_dict, "state")
    nx.set_node_attributes(G, county_dict, "county")
    nx.set_node_attributes(G, town_dict, "town")
    nx.set_node_attributes(G, lat_dict, "latitude")
    nx.set_node_attributes(G, long_dict, "longitude")

    for pop in [
        "Population",
        "<18",
        "18-24",
        "25-29",
        "30-34",
        "35-39",
        "40-44",
        "45-49",
        "50-54",
        "55-59",
        "60-64",
        "65+",
    ]:
        d = df.set_index("target_fips").loc[:, pop].to_dict()
        nx.set_node_attributes(G, d, pop)

    if output is None:
        df.to_csv("data/derived/town_commuter_flows.tsv", sep="\t", index=False)
        nx.write_graphml(G, "data/derived/town_commuter_flows.graphml")
    else:
        Path(f"data/derived/{output}").mkdir(parents=True, exist_ok=True)
        df.to_csv(
            f"data/derived/{output}/town_commuter_flows.tsv",
            sep="\t",
            index=False,
        )
        nx.write_graphml(G, f"data/derived/{output}/town_commuter_flows.graphml")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Construct town-level commuter networks."
    )
    parser.add_argument(
        "-s",
        "--states",
        action="store",
        help="A comma-separated list of two-digit state FIPS codes to include "
        "in the network. If this argument is absent use all 50 states + DC.",
        default=None,
    )
    parser.add_argument(
        "-o",
        "--output",
        action="store",
        help="The name of a subfolder of data/derived to save to. If this "
        "argument is absent, save to data/derived directly",
        default=None,
    )
    parser.add_argument(
        "-m",
        "--minimum-weight",
        action="store",
        help="The minimum number of trips required to keep an edge. Where "
        "this is higher, the resulting graph will be sparser.",
        default=0,
    )
    args = parser.parse_args()
    construct_network(args.states, args.minimum_weight, args.output)
