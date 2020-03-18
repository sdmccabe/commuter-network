import requests
from state_fips_mapping import STATE_TO_FIPS
from pathlib import Path
import json
import pandas as pd

# fmt: off
TYPES = [
    (
        "data/raw/population_data/county/",
        "county",
        lambda row: row[['state', 'county']].str.cat(),
    ),
    (
        "data/raw/population_data/town/",
        "county subdivision",
        lambda row: row[['state', 'county', 'county subdivision']].str.cat(),
    ),
    (
        "data/raw/population_data/tract/",
        "tract",
        lambda row: row[['state', 'county', 'tract']].str.cat(),
    ),
]

CENSUS_VARS = [
    "B01001_001E", "B01001_003E", "B01001_004E", "B01001_005E",
    "B01001_006E", "B01001_007E", "B01001_008E", "B01001_009E",
    "B01001_010E", "B01001_011E", "B01001_012E", "B01001_013E",
    "B01001_014E", "B01001_015E", "B01001_016E", "B01001_017E",
    "B01001_018E", "B01001_019E", "B01001_020E", "B01001_021E",
    "B01001_022E", "B01001_023E", "B01001_024E", "B01001_025E",
    "B01001_027E", "B01001_028E", "B01001_029E", "B01001_030E",
    "B01001_031E", "B01001_032E", "B01001_033E", "B01001_034E",
    "B01001_035E", "B01001_036E", "B01001_037E", "B01001_038E",
    "B01001_039E", "B01001_040E", "B01001_041E", "B01001_042E",
    "B01001_043E", "B01001_044E", "B01001_045E", "B01001_046E",
    "B01001_047E", "B01001_048E", "B01001_049E"
]
# fmt: on
GROUPING = {
    "Population": [0],
    "<18": [1, 2, 3, 4, 24, 25, 26, 27],
    "18-24": [5, 6, 7, 8, 28, 29, 30, 31],
    "25-29": [9, 32],
    "30-34": [10, 33],
    "35-39": [11, 34],
    "40-44": [12, 35],
    "45-49": [13, 36],
    "50-54": [14, 37],
    "55-59": [15, 38],
    "60-64": [16, 17, 39, 40],
    "65+": [18, 19, 20, 21, 22, 23, 41, 42, 43, 44, 45, 46],
}


def request_to_df(r):
    content = json.loads(r.content)
    header = content[0]
    data = content[1:]
    return pd.DataFrame(data, columns=header)


def main():
    for (DIR, LEVEL, FUNC) in TYPES:
        Path(DIR).mkdir(parents=True, exist_ok=True)
        for state, fips in STATE_TO_FIPS.items():
            if not Path(f"{DIR}{state}.tsv").is_file():
                s = (
                    "https://api.census.gov/data/2016/acs/acs5/?get=NAME,"
                    f"{','.join(CENSUS_VARS)}&for={LEVEL}:*&in=state:{fips}"
                )
                r = requests.get(s)
                df = request_to_df(r)
                df.loc[:, CENSUS_VARS] = df.loc[:, CENSUS_VARS].astype(int)
                for label, indices in GROUPING.items():
                    varnames = [CENSUS_VARS[idx] for idx in indices]
                    df.loc[:, label] = df.loc[:, varnames].sum(axis=1)

                df = df.loc[:, ~df.columns.isin(CENSUS_VARS)]
                df.loc[:, "FIPS"] = df.apply(FUNC, axis=1)

                df.to_csv(f"{DIR}{state}.tsv", sep="\t", index=False)


if __name__ == "__main__":
    main()
