# %%
import numpy as np
import pandas as pd
import streamlit as st
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
st.set_page_config(layout="wide")


@st.cache_data(show_spinner="Nalaganje podatkov...")
def get_data() -> pd.DataFrame:
    dfs = {
        # k: pd.read_csv(get_google_sheet_url(FILE_ID, sheet_id))
        k: pd.read_excel(get_google_sheet_url(FILE_ID, sheet_id), decimal=",")
        for k, sheet_id in SHEET_IDS.items()
    }
    return dfs


# %%
dfs = get_data()
figs = {}


# %%
def apply_scatterplot_style(fig):
    fig.update_traces(
        marker={"size": 3, "opacity": 0.5},
        line={"width": 1},
    )


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

vrste_hrane_sorted = df_hrana["vrsta_hrane"].unique()
df_hrana_pivot = df_hrana.pivot(
    index="datum", columns="vrsta_hrane", values="pojedel_g"
)[vrste_hrane_sorted].reset_index(names="datum")


figs["Hrana (g)"] = px.area(
    df_hrana_pivot, x="datum", y=df_hrana_pivot.columns[1:], title="Hrana (g)"
)

for i in figs["Hrana (g)"]["data"]:
    i["line"]["width"] = 0


figs["Pojedel (kcal)"] = px.scatter(
    data_frame=df_hrana.groupby("datum", as_index=False).agg({"pojedel_kcal": np.sum}),
    x="datum",
    y="pojedel_kcal",
    trendline="rolling",
    trendline_options=dict(window="7d"),
)
apply_scatterplot_style(figs["Pojedel (kcal)"])

# %%
df_teza = dfs["log_teza"]

figs["Teža (g)"] = px.scatter(
    # data_frame=df_teza.groupby('datum', as_index=False).agg({'teza_g': np.mean}),
    data_frame=df_teza,
    x="datum",
    y="teza_g",
    trendline="rolling",
    trendline_options=dict(window="7d"),
)
apply_scatterplot_style(figs["Teža (g)"])

# %%
df_drugo = dfs["log_drugo"]

figs["Prednicortone (5 mg tablete)"] = px.bar(
    data_frame=df_drugo[df_drugo.vrsta == "prednisolone (5mg tablete)"],
    x="datum",
    y="količina",
)
# figs["Bruhanje (dni na teden)"] = px.line(
#     x=df.datum,
#     y=df.bruhal.rolling(window=7).sum(),
# )
# figs["Driska ali mehko kakanje (dni na teden)"] = px.line(
#     x=df.datum,
#     y=df.driska.rolling(window=7).sum(),
# )

# %%
preselected_subplots = ["Pojedel (kcal)", "Teža (g)", "Prednicortone (5 mg tablete)"]

selected_subplots = st.multiselect(
    "Izbira grafov", figs.keys(), default=preselected_subplots
)

st.button("Osveži podatke", on_click=get_data.clear)

# %%
fig_out = make_subplots(
    rows=len(figs) - 1,
    cols=1,
    shared_xaxes=True,
    subplot_titles=selected_subplots,
    vertical_spacing=0.05,
)

# Add traces from px figures
for i, fig_key in enumerate(selected_subplots, start=1):
    for trace in figs[fig_key].data:
        fig_out.add_trace(trace, row=i, col=1)

fig_out.update_layout(height=900, width=600)

# %%
st.plotly_chart(fig_out)

st.markdown(f"[Izvorni podatki](https://docs.google.com/spreadsheets/d/{FILE_ID})")

# %%
