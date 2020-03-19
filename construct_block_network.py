import glob
import pandas as pd
import argparse
import networkx as nx
from pathlib import Path


def construct_network(states, minimum_weight, output):
    if states is None:
        # fmt: off
        STATES = [
            "ak", "al", "ar", "az", "ca", "co", "ct", "dc", "de", "fl",
            "ga", "hi", "ia", "id", "il", "in", "ks", "ky", "la", "ma",
            "md", "me", "mn", "mo", "ms", "mt", "nc", "nd", "ne", "nh",
            "nj", "nm", "nm", "nv", "ny", "oh", "ok", "or", "pa", "ri",
            "sc", "sd", "tn", "tx", "ut", "va", "vt", "wa", "wi", "wv",
            "wy",
        ]
        # fmt: on
    else:
        STATES = [x.strip().lower() for x in states.split(",")]

    metadatas = []
    dfs = []
    for state in STATES:
        metadata = pd.read_csv(
            f"data/raw/LODES7/{state}/{state}_xwalk.csv.gz",
            sep=",",
            usecols=[
                "tabblk2010",
                "st",
                "cty",
                "trct",
                "zcta",
                "stname",
                "stusps",
                "ctyname",
                "trctname",
                "blklatdd",
                "blklondd",
            ],
            compression="gzip",
            encoding="latin-1",
            dtype="str",
        )

        metadatas.append(metadata)

        files = glob.glob(f"data/raw/LODES7/{state}/od/{state}_od_*_JT00_2016.csv.gz")

        for fname in files:
            df = pd.read_csv(
                fname,
                sep=",",
                usecols=["w_geocode", "h_geocode", "S000"],
                compression="gzip",
                encoding="latin-1",
                dtype={"w_geocode": "str", "h_geocode": "str", "S000": "Int64"},
            ).rename(
                columns={"w_geocode": "target", "h_geocode": "source", "S000": "weight"}
            )

            dfs.append(df)

    df = pd.concat(dfs, axis=0, ignore_index=True)
    metadata = pd.concat(metadatas, axis=0, ignore_index=True)
    del dfs
    del metadatas

    df = df.loc[df["weight"] >= int(minimum_weight), :]
    G = nx.from_pandas_edgelist(
        df, "source", "target", edge_attr=["weight"], create_using=nx.DiGraph()
    )
    del df

    state_dict = metadata.set_index("tabblk2010")["stname"].to_dict()
    county_dict = metadata.set_index("tabblk2010")["ctyname"].to_dict()
    tract_dict = metadata.set_index("tabblk2010")["trctname"].to_dict()
    lat_dict = metadata.set_index("tabblk2010")["blklatdd"].to_dict()
    long_dict = metadata.set_index("tabblk2010")["blklondd"].to_dict()

    nx.set_node_attributes(G, state_dict, "state")
    nx.set_node_attributes(G, county_dict, "county")
    nx.set_node_attributes(G, tract_dict, "tract")
    nx.set_node_attributes(G, lat_dict, "latitude")
    nx.set_node_attributes(G, long_dict, "longitude")

    if output is None:
        nx.write_graphml(G, "data/derived/block_commuter_flows.graphml")
    else:
        Path(f"data/derived/{output}").mkdir(parents=True, exist_ok=True)
        nx.write_graphml(G, f"data/derived/{output}/block_commuter_flows.graphml")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Construct county-level commuter networks."
    )
    parser.add_argument(
        "-s",
        "--states",
        action="store",
        help="A comma-separated list of two-digit state USPS codes to include "
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
