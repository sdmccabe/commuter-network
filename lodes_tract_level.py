import glob
import pandas as pd
from tqdm import tqdm


def main():

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

    for state in tqdm(STATES):
        metadata = pd.read_csv(
            f"data/raw/LODES7/{state}/{state}_xwalk.csv.gz",
            sep=",",
            usecols=["st", "cty", "trct", "zcta", "stname", "ctyname", "trctname",],
            compression="gzip",
            encoding="latin-1",
            dtype="str",
        )

        metadata = metadata.groupby(["st", "cty", "trct"]).first().reset_index()
        metadata.to_csv(
            f"data/derived/lodes_tract/{state}_metadata.csv.gz",
            index=False,
            compression="gzip",
        )

        files = glob.glob(f"data/raw/LODES7/{state}/od/{state}_od_*_JT00_2016.csv.gz")
        dfs = []

        for fname in files:
            df = pd.read_csv(
                fname,
                sep=",",
                usecols=["w_geocode", "h_geocode", "S000"],
                compression="gzip",
                encoding="latin-1",
                dtype={"w_geocode": "str", "h_geocode": "str", "S000": "int"},
            ).rename(
                columns={"w_geocode": "target", "h_geocode": "source", "S000": "weight"}
            )

            df["target"] = df["target"].str[:11]
            df["source"] = df["source"].str[:11]

            dfs.append(df)

        df = pd.concat(dfs, axis=0, ignore_index=True)
        del dfs
        df = df.groupby(["source", "target"]).agg({"weight": "sum"}).reset_index()

        df.to_csv(
            f"data/derived/lodes_tract/{state}_flow.csv.gz",
            index=False,
            compression="gzip",
        )


if __name__ == "__main__":
    main()
