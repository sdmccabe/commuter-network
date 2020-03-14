import networkx as nx
import pandas as pd

# This script uses the following data files:
#
# table1.xlsx: https://www.census.gov/data/tables/2015/demo/metro-micro/commuting-flows-2015.html
# 2019_Gaz_counties_national.txt: https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html


SCHEMA = {
    "source_state_fips_code": str,
    "source_county_fips_code": str,
    "source_state_name": str,
    "source_county_name": str,
    "target_state_fips_code": str,
    "target_county_fips_code": str,
    "target_state_name": str,
    "target_county_name": str,
    "flow_weight": str,
    "flow_margin": str,
}


def parseint(s):
    try:
        return int(s)
    except ValueError:
        s = s.replace(",", "")
        return int(s)


def construct_fips(state, county):
    return state + county


def main():
    df = pd.read_excel(
        "data/raw/table1.xlsx",
        skiprows=7,
        header=None,
        names=SCHEMA.keys(),
        dtype=SCHEMA,
    )
    df = df.loc[pd.notnull(df["flow_weight"]), :]

    gazetteer = pd.read_csv(
        "data/raw/2019_Gaz_counties_national.txt", sep="\t", dtype={"GEOID": str},
    )
    gazetteer.columns = [x.strip() for x in gazetteer.columns]
    gazetteer = gazetteer.loc[:, ["GEOID", "INTPTLONG", "INTPTLAT"]]

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

    df["flow_weight"] = df["flow_weight"].apply(parseint)
    df["flow_margin"] = df["flow_margin"].apply(parseint)

    # Strip initial zero in state FIPS codes for target. The spreadsheet
    # has state FIPS as a three-digit number to allow for Canada.
    df["target_state_fips_code"] = df["target_state_fips_code"].str[1:]

    # Simple concatenation of component FIPS codes.
    df["source_fips"] = df.apply(
        lambda row: construct_fips(
            row.source_state_fips_code, row.source_county_fips_code,
        ),
        axis=1,
    )

    df["target_fips"] = df.apply(
        lambda row: construct_fips(
            row.target_state_fips_code, row.target_county_fips_code,
        ),
        axis=1,
    )

    df = df.loc[df["source_fips"].apply(lambda s: len(s) == 5), :]
    df = df.loc[df["target_fips"].apply(lambda s: len(s) == 5), :]

    df = df.merge(source_gazetteer, how="left", on="source_fips",)
    df = df.merge(target_gazetteer, how="left", on="target_fips",)

    # Construct the graph with edge attributes.
    G = nx.from_pandas_edgelist(
        df, "source_fips", "target_fips", edge_attr=["flow_weight", "flow_margin"]
    )

    # Node attributes are a bit trickier. It's unlikely, but just to make sure
    # we don't miss any metadata, we combine the source and target information
    # about locations.
    target_attr_df = (
        df.set_index("target_fips")
        .loc[:, ["target_state_name", "target_county_name"]]
        .rename(
            {"target_state_name": "state", "target_county_name": "county",}, axis=1,
        )
    )
    source_attr_df = (
        df.set_index("source_fips")
        .loc[:, ["target_state_name", "target_county_name"]]
        .rename(
            {"target_state_name": "state", "target_county_name": "county",}, axis=1,
        )
    )
    lat_dict = gazetteer.set_index("GEOID")["INTPTLAT"].to_dict()
    long_dict = gazetteer.set_index("GEOID")["INTPTLONG"].to_dict()

    state_dict = target_attr_df["state"].to_dict()
    state_dict.update(source_attr_df["state"].to_dict())
    county_dict = target_attr_df["county"].to_dict()
    county_dict.update(source_attr_df["county"].to_dict())

    # With the node attribute dicts created, we can set node attributes and
    # then write to files.

    nx.set_node_attributes(G, state_dict, "state")
    nx.set_node_attributes(G, county_dict, "county")
    nx.set_node_attributes(G, lat_dict, "latitude")
    nx.set_node_attributes(G, long_dict, "longitude")

    df.to_csv("data/derived/county_commuter_flows.tsv", sep="\t", index=False)
    nx.write_graphml(G, "data/derived/county_commuter_flows.graphml")


if __name__ == "__main__":
    main()
