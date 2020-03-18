import pandas as pd
import networkx as nx
import glob
import argparse
from pathlib import Path
from state_fips_mapping import STATE_TO_FIPS


def open_dfs(fnames, **kwargs):
    """Given a list of filenames, open and concatenate into one data frame."""
    dfs = []
    for fname in fnames:
        _df = pd.read_csv(fname, **kwargs)
        dfs.append(_df)
    df = pd.concat(dfs, axis=0, ignore_index=True)
    return df


def main(args):
    if args.states is None:
        metadata_files = glob.glob(f"data/derived/lodes_tract/*_metadata.csv.gz")
        pop_files = glob.glob(f"data/raw/population_data/tract/*.tsv")
        flow_files = glob.glob(f"data/derived/lodes_tract/*_flow.csv.gz")
        STATES = STATE_TO_FIPS.keys()
    else:
        STATES = [x.strip().lower() for x in args.states.split(",")]
        metadata_files = []
        pop_files = []
        flow_files = []
        for state in STATES:
            metadata_files.append(f"data/derived/lodes_tract/{state}_metadata.csv.gz")
            pop_files.append(f"data/raw/population_data/tract/{state}.tsv")
            flow_files.append(f"data/derived/lodes_tract/{state}_flow.csv.gz")

    metadata = open_dfs(
        metadata_files,
        dtype={"st": "str", "cty": "str", "trct": "str", "zcta": "str"},
        compression="gzip",
    )
    pop = open_dfs(pop_files, sep="\t", dtype={"FIPS": "str"},)
    flow = open_dfs(
        flow_files,
        dtype={"source": "str", "target": "str", "weight": "Int64"},
        compression="gzip",
    )

    flow = flow.loc[flow["weight"] >= int(args.minimum_weight), :]
    gazetteer = pd.read_csv(
        "data/raw/2019_Gaz_tracts_national.txt", sep="\t", dtype={"GEOID": str},
    )
    gazetteer.columns = [x.strip() for x in gazetteer.columns]
    gazetteer = gazetteer.loc[:, ["GEOID", "INTPTLONG", "INTPTLAT"]]
    SFIPS = [STATE_TO_FIPS[s] for s in STATES]

    flow = flow.loc[flow['source'].str[:2].isin(SFIPS), :]
    flow = flow.loc[flow['target'].str[:2].isin(SFIPS), :]
    G = nx.from_pandas_edgelist(
        flow, "source", "target", edge_attr=["weight"], create_using=nx.DiGraph()
    )
    del flow

    state_dict = metadata.set_index("trct")["stname"].to_dict()
    county_dict = metadata.set_index("trct")["ctyname"].to_dict()
    tract_dict = metadata.set_index("trct")["trctname"].to_dict()

    lat_dict = gazetteer.set_index("GEOID")["INTPTLAT"].to_dict()
    long_dict = gazetteer.set_index("GEOID")["INTPTLONG"].to_dict()

    nx.set_node_attributes(G, state_dict, "state")
    nx.set_node_attributes(G, county_dict, "county")
    nx.set_node_attributes(G, tract_dict, "tract")
    nx.set_node_attributes(G, lat_dict, "latitude")
    nx.set_node_attributes(G, long_dict, "longitude")
    for p in [
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
        d = pop.set_index("FIPS").loc[:, p].to_dict()
        nx.set_node_attributes(G, d, p)

    if args.output is None:
        nx.write_graphml(G, "data/derived/tract_commuter_flows.graphml")
    else:
        Path(f"data/derived/{args.output}").mkdir(parents=True, exist_ok=True)
        nx.write_graphml(G, f"data/derived/{args.output}/tract_commuter_flows.graphml")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Construct tract-level commuter networks."
    )
    parser.add_argument(
        "-s",
        "--states",
        action="store",
        help="A comma-separated list of two-letter state USPS codes to include "
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

    main(args)
