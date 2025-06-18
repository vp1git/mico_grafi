# %%
import pandas as pd
import plotly.express as px


def get_google_sheet_url(file_id: str, sheet_id: int) -> str:
    return (
        "https://docs.google.com/spreadsheets/d/"
        + file_id
        # + "/export?format=csv"
        + "/export?format=ods"
        + "&gid="
        + str(sheet_id)
    )


FILE_ID = "1K1XDOwUcrfbYr6QW0mOk_no1vzoCIygBwXc6qvSyqXM"
SHEET_IDS = {
    "log_hrana": 0,
    "log_teza": 1237121504,
    "log_drugo": 1362862141,
    "vrste_hrana": 54176045,
    "vrste_drugo": 1556951560,
}

# %%
dfs = {
    # k: pd.read_csv(get_google_sheet_url(FILE_ID, sheet_id))
    k: pd.read_excel(get_google_sheet_url(FILE_ID, sheet_id))
    for k, sheet_id in SHEET_IDS.items()
}

# %%
figs = {}

# %%
hrana_sorted = dfs["log_hrana"]["vrsta_hrane"].unique()
df_hrana_pivot = (
    dfs["log_hrana"]
    .pivot(index="datum", columns="vrsta_hrane", values="pojedel_g")[hrana_sorted]
    .reset_index(names="datum")
)

# %%
figs["hrana"] = px.area(
    df_hrana_pivot, x="datum", y=df_hrana_pivot.columns[1:], title="Hrana (g)"
)
for i in figs["hrana"]["data"]:
    i["line"]["width"] = 0
figs["hrana"]
# %%
