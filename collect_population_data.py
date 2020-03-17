import requests
from state_fips_mapping import STATE_TO_FIPS
from pathlib import Path
import json
import pandas as pd


def main():
    TRACT_DIR = "data/raw/population_data/tract/"
    if not Path(TRACT_DIR).is_dir():
        Path(TRACT_DIR).mkdir(parents=True)
        for state, fips in STATE_TO_FIPS.items():
            s = (
                "https://api.census.gov/data/2016/acs/acs5/?get=NAME,"
                "B01001_001E,B01001_003E,B01001_004E,B01001_005E,"
                "B01001_006E,B01001_007E,B01001_008E,B01001_009E,"
                "B01001_010E,B01001_011E,B01001_012E,B01001_013E,"
                "B01001_014E,B01001_015E,B01001_016E,B01001_017E,"
                "B01001_018E,B01001_019E,B01001_020E,B01001_021E,"
                "B01001_022E,B01001_023E,B01001_024E,B01001_025E,"
                "B01001_027E,B01001_028E,B01001_029E,B01001_030E,"
                "B01001_031E,B01001_032E,B01001_033E,B01001_034E,"
                "B01001_035E,B01001_036E,B01001_037E,B01001_038E,"
                "B01001_039E,B01001_040E,B01001_041E,B01001_042E,"
                "B01001_043E,B01001_044E,B01001_045E,B01001_046E,"
                "B01001_047E,B01001_048E,B01001_049E"
                f"&for=tract:*&in=state:{fips}"
                # "&key={API_KEY}"
            )
            r = requests.get(s)
            content = json.loads(r.content)
            header = content[0]
            data = content[1:]
            df = pd.DataFrame(data, columns=header)
            df.loc[:, df.columns.str.startswith("B")] = df.loc[
                :, df.columns.str.startswith("B")
            ].astype(int)
            df.loc[:, "Population"] = df.loc[:, "B01001_001E"]

            df.loc[:, "<18"] = df.loc[
                :,
                [
                    "B01001_003E",
                    "B01001_004E",
                    "B01001_005E",
                    "B01001_006E",
                    "B01001_027E",
                    "B01001_028E",
                    "B01001_029E",
                    "B01001_030E",
                ],
            ].sum(axis=1)
            df.loc[:, "18-24"] = df.loc[
                :,
                [
                    "B01001_007E",
                    "B01001_008E",
                    "B01001_009E",
                    "B01001_010E",
                    "B01001_031E",
                    "B01001_032E",
                    "B01001_033E",
                    "B01001_034E",
                ],
            ].sum(axis=1)
            df.loc[:, "25-29"] = df.loc[:, ["B01001_011E", "B01001_035E"]].sum(axis=1)
            df.loc[:, "30-34"] = df.loc[:, ["B01001_012E", "B01001_036E"]].sum(axis=1)
            df.loc[:, "35-39"] = df.loc[:, ["B01001_013E", "B01001_037E"]].sum(axis=1)
            df.loc[:, "40-44"] = df.loc[:, ["B01001_014E", "B01001_038E"]].sum(axis=1)
            df.loc[:, "45-49"] = df.loc[:, ["B01001_015E", "B01001_039E"]].sum(axis=1)
            df.loc[:, "50-54"] = df.loc[:, ["B01001_016E", "B01001_040E"]].sum(axis=1)
            df.loc[:, "55-59"] = df.loc[:, ["B01001_017E", "B01001_041E"]].sum(axis=1)
            df.loc[:, "60-64"] = df.loc[
                :, ["B01001_018E", "B01001_019E", "B01001_042E", "B01001_043E"]
            ].sum(axis=1)
            df.loc[:, "65+"] = df.loc[
                :,
                [
                    "B01001_020E",
                    "B01001_021E",
                    "B01001_022E",
                    "B01001_023E",
                    "B01001_024E",
                    "B01001_025E",
                    "B01001_044E",
                    "B01001_045E",
                    "B01001_046E",
                    "B01001_047E",
                    "B01001_048E",
                    "B01001_049E",
                ],
            ].sum(axis=1)
            df = df.loc[:, ~df.columns.str.startswith("B")]
            df.loc[:, "FIPS"] = df.apply(
                lambda row: row.state + row.county + row.tract, axis=1,
            )

            df.to_csv(f"{TRACT_DIR}{state}.tsv", sep="\t", index=False)

    COUSUB_DIR = "data/raw/population_data/town/"
    if not Path(COUSUB_DIR).is_dir():
        Path(COUSUB_DIR).mkdir(parents=True)
        for state, fips in STATE_TO_FIPS.items():
            s = (
                "https://api.census.gov/data/2016/acs/acs5/?get=NAME,"
                "B01001_001E,B01001_003E,B01001_004E,B01001_005E,"
                "B01001_006E,B01001_007E,B01001_008E,B01001_009E,"
                "B01001_010E,B01001_011E,B01001_012E,B01001_013E,"
                "B01001_014E,B01001_015E,B01001_016E,B01001_017E,"
                "B01001_018E,B01001_019E,B01001_020E,B01001_021E,"
                "B01001_022E,B01001_023E,B01001_024E,B01001_025E,"
                "B01001_027E,B01001_028E,B01001_029E,B01001_030E,"
                "B01001_031E,B01001_032E,B01001_033E,B01001_034E,"
                "B01001_035E,B01001_036E,B01001_037E,B01001_038E,"
                "B01001_039E,B01001_040E,B01001_041E,B01001_042E,"
                "B01001_043E,B01001_044E,B01001_045E,B01001_046E,"
                "B01001_047E,B01001_048E,B01001_049E"
                f"&for=county+subdivision:*&in=state:{fips}"
                # "&key={API_KEY}"
            )
            r = requests.get(s)
            content = json.loads(r.content)
            header = content[0]
            data = content[1:]
            df = pd.DataFrame(data, columns=header)

            df.loc[:, df.columns.str.startswith("B")] = df.loc[
                :, df.columns.str.startswith("B")
            ].astype(int)
            df.loc[:, "Population"] = df.loc[:, "B01001_001E"]

            df.loc[:, "<18"] = df.loc[
                :,
                [
                    "B01001_003E",
                    "B01001_004E",
                    "B01001_005E",
                    "B01001_006E",
                    "B01001_027E",
                    "B01001_028E",
                    "B01001_029E",
                    "B01001_030E",
                ],
            ].sum(axis=1)
            df.loc[:, "18-24"] = df.loc[
                :,
                [
                    "B01001_007E",
                    "B01001_008E",
                    "B01001_009E",
                    "B01001_010E",
                    "B01001_031E",
                    "B01001_032E",
                    "B01001_033E",
                    "B01001_034E",
                ],
            ].sum(axis=1)
            df.loc[:, "25-29"] = df.loc[:, ["B01001_011E", "B01001_035E"]].sum(axis=1)
            df.loc[:, "30-34"] = df.loc[:, ["B01001_012E", "B01001_036E"]].sum(axis=1)
            df.loc[:, "35-39"] = df.loc[:, ["B01001_013E", "B01001_037E"]].sum(axis=1)
            df.loc[:, "40-44"] = df.loc[:, ["B01001_014E", "B01001_038E"]].sum(axis=1)
            df.loc[:, "45-49"] = df.loc[:, ["B01001_015E", "B01001_039E"]].sum(axis=1)
            df.loc[:, "50-54"] = df.loc[:, ["B01001_016E", "B01001_040E"]].sum(axis=1)
            df.loc[:, "55-59"] = df.loc[:, ["B01001_017E", "B01001_041E"]].sum(axis=1)
            df.loc[:, "60-64"] = df.loc[
                :, ["B01001_018E", "B01001_019E", "B01001_042E", "B01001_043E"]
            ].sum(axis=1)
            df.loc[:, "65+"] = df.loc[
                :,
                [
                    "B01001_020E",
                    "B01001_021E",
                    "B01001_022E",
                    "B01001_023E",
                    "B01001_024E",
                    "B01001_025E",
                    "B01001_044E",
                    "B01001_045E",
                    "B01001_046E",
                    "B01001_047E",
                    "B01001_048E",
                    "B01001_049E",
                ],
            ].sum(axis=1)
            df = df.loc[:, ~df.columns.str.startswith("B")]
            df.loc[:, "FIPS"] = df.apply(
                lambda row: row.state + row.county + row["county subdivision"], axis=1,
            )

            df.to_csv(f"{COUSUB_DIR}{state}.tsv", sep="\t", index=False)
    COUNTY_DIR = "data/raw/population_data/county/"
    if not Path(COUNTY_DIR).is_dir():
        Path(COUNTY_DIR).mkdir(parents=True)
        for state, fips in STATE_TO_FIPS.items():
            s = (
                "https://api.census.gov/data/2016/acs/acs5/?get=NAME,"
                "B01001_001E,B01001_003E,B01001_004E,B01001_005E,"
                "B01001_006E,B01001_007E,B01001_008E,B01001_009E,"
                "B01001_010E,B01001_011E,B01001_012E,B01001_013E,"
                "B01001_014E,B01001_015E,B01001_016E,B01001_017E,"
                "B01001_018E,B01001_019E,B01001_020E,B01001_021E,"
                "B01001_022E,B01001_023E,B01001_024E,B01001_025E,"
                "B01001_027E,B01001_028E,B01001_029E,B01001_030E,"
                "B01001_031E,B01001_032E,B01001_033E,B01001_034E,"
                "B01001_035E,B01001_036E,B01001_037E,B01001_038E,"
                "B01001_039E,B01001_040E,B01001_041E,B01001_042E,"
                "B01001_043E,B01001_044E,B01001_045E,B01001_046E,"
                "B01001_047E,B01001_048E,B01001_049E"
                f"&for=county:*&in=state:{fips}"
                # "&key={API_KEY}"
            )
            r = requests.get(s)
            content = json.loads(r.content)
            header = content[0]
            data = content[1:]
            df = pd.DataFrame(data, columns=header)

            df.loc[:, df.columns.str.startswith("B")] = df.loc[
                :, df.columns.str.startswith("B")
            ].astype(int)
            df.loc[:, "Population"] = df.loc[:, "B01001_001E"]

            df.loc[:, "<18"] = df.loc[
                :,
                [
                    "B01001_003E",
                    "B01001_004E",
                    "B01001_005E",
                    "B01001_006E",
                    "B01001_027E",
                    "B01001_028E",
                    "B01001_029E",
                    "B01001_030E",
                ],
            ].sum(axis=1)
            df.loc[:, "18-24"] = df.loc[
                :,
                [
                    "B01001_007E",
                    "B01001_008E",
                    "B01001_009E",
                    "B01001_010E",
                    "B01001_031E",
                    "B01001_032E",
                    "B01001_033E",
                    "B01001_034E",
                ],
            ].sum(axis=1)
            df.loc[:, "25-29"] = df.loc[:, ["B01001_011E", "B01001_035E"]].sum(axis=1)
            df.loc[:, "30-34"] = df.loc[:, ["B01001_012E", "B01001_036E"]].sum(axis=1)
            df.loc[:, "35-39"] = df.loc[:, ["B01001_013E", "B01001_037E"]].sum(axis=1)
            df.loc[:, "40-44"] = df.loc[:, ["B01001_014E", "B01001_038E"]].sum(axis=1)
            df.loc[:, "45-49"] = df.loc[:, ["B01001_015E", "B01001_039E"]].sum(axis=1)
            df.loc[:, "50-54"] = df.loc[:, ["B01001_016E", "B01001_040E"]].sum(axis=1)
            df.loc[:, "55-59"] = df.loc[:, ["B01001_017E", "B01001_041E"]].sum(axis=1)
            df.loc[:, "60-64"] = df.loc[
                :, ["B01001_018E", "B01001_019E", "B01001_042E", "B01001_043E"]
            ].sum(axis=1)
            df.loc[:, "65+"] = df.loc[
                :,
                [
                    "B01001_020E",
                    "B01001_021E",
                    "B01001_022E",
                    "B01001_023E",
                    "B01001_024E",
                    "B01001_025E",
                    "B01001_044E",
                    "B01001_045E",
                    "B01001_046E",
                    "B01001_047E",
                    "B01001_048E",
                    "B01001_049E",
                ],
            ].sum(axis=1)
            df = df.loc[:, ~df.columns.str.startswith("B")]
            df.loc[:, "FIPS"] = df.apply(lambda row: row.state + row.county, axis=1,)

            df.to_csv(f"{COUNTY_DIR}{state}.tsv", sep="\t", index=False)


if __name__ == "__main__":
    main()
