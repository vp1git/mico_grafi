# %%
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots


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
df_hrana = pd.merge(
    dfs["log_hrana"],
    dfs["vrste_hrana"],
    how="left",
    left_on="vrsta_hrane",
    right_on="hrana",
)
df_hrana["pojedel_kcal"] = df_hrana.apply(
    lambda row: row.pojedel_g * row.kcal_per_g, axis="columns"
)

figs["pojedel_kcal"] = px.scatter(
    data_frame=df_hrana.groupby("datum", as_index=False).agg({"pojedel_kcal": sum}),
    x="datum",
    y="pojedel_kcal",
    trendline="rolling",
    trendline_options=dict(window="7d"),
    title="Pojedel (kcal)",
)

# %%
df_teza = dfs["log_teza"]

figs["teza_g"] = px.scatter(
    # data_frame=df_teza.groupby('datum', as_index=False).agg({'teza_g': np.mean}),
    data_frame=df_teza,
    x="datum",
    y="teza_g",
    trendline="rolling",
    trendline_options=dict(window="7d"),
    title="Pojedel (kcal)",
)

# %%
for fig_key in ["pojedel_kcal", "teza_g"]:
    figs[fig_key].update_traces(
        marker={"size": 4, "opacity": 1},
        line={"width": 1},
    )

# %%
fig_out = make_subplots(
    rows=len(figs),
    cols=1,
    shared_xaxes=True,
    subplot_titles=(
        "Hrana (g)",
        "Pojedel (kcal)",
        "Teža (g)",
        "Bruhanje (na teden)",
        "Driska (na teden)",
        "Prednicortone (5 mg tablete)",
    ),
)

# Add traces from px figures
for i, fig in enumerate(figs.values(), start=1):
    for trace in fig.data:
        fig_out.add_trace(trace, row=i, col=1)
# %%
fig_out

# %%
df_drugo = dfs["log_drugo"]
df_drugo[df_drugo.vrsta == "prednisolone (5mg tablete)"]
figs["prednicortone_5mg"] = px.bar(
    data_frame=df_drugo[df_drugo.vrsta == "prednisolone (5mg tablete)"],
    x="datum",
    y="količina",
    title="Prednicortone (5 mg tablete)",
)
figs["prednicortone_5mg"]

# %%
