# %%
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio

pio.templates.default = "plotly"


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
        line={"width": 1.5},
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

# %%
pojedel_kcal = df_hrana.groupby("datum")["pojedel_kcal"].sum()
figs["Pojedel (kcal)"] = px.scatter(
    x=pojedel_kcal.index,
    y=pojedel_kcal,
    trendline="rolling",
    trendline_options=dict(window="7d"),
    color_discrete_sequence=["green"],
    # labels=dict(x="Datum", y="Pojedel (kcal)"),
)
apply_scatterplot_style(figs["Pojedel (kcal)"])

# %%
date_range = pd.date_range(df_hrana.datum.min(), df_hrana.datum.max(), freq="D")
df_drugo = dfs["log_drugo"]
df_teza = dfs["log_teza"]

# %%
teza_g = df_teza.groupby("datum")["teza_g"].mean()
figs["Teža (g)"] = px.scatter(
    x=teza_g.index,
    y=teza_g,
    trendline="rolling",
    trendline_options=dict(window="7d"),
    # labels=dict(x="Datum", y="Teža (g)"),
)
apply_scatterplot_style(figs["Teža (g)"])

# %%
prednicortone = (
    df_drugo[df_drugo.vrsta.isin(["prednisolone (5mg tablete)"])]
    .groupby("datum")["količina"]
    .sum()
)
figs["Prednicortone (5 mg tablete)"] = px.bar(
    x=prednicortone.index,
    y=prednicortone,
    # labels=dict(x="Datum", y="Prednicortone (5 mg tablete)"),
)

# %%
bruhanje = (
    df_drugo[df_drugo.vrsta.isin(["bruhanje"])]
    .groupby("datum")["vrsta"]
    .count()
    .reindex(date_range)
    .fillna(0)
)

color = "red"
figs["Bruhanje (št. na teden)"] = px.bar(
    x=bruhanje.index,
    y=bruhanje,
    color_discrete_sequence=[color],
    # labels=dict(x="Datum", y="Bruhanje (št. na teden)"),
)
# figs["Bruhanje (št. na teden)"].add_traces(
#     px.line(
#         x=bruhanje.index,
#         y=bruhanje.rolling("7d", center=True).sum(),
#         color_discrete_sequence=[color],
#     ).data,
# )

# %%
driska = (
    # df_drugo[df_drugo.vrsta.isin(["driska", "mehko kakanje"])]
    df_drugo[df_drugo.vrsta.isin(["driska"])]
    .groupby("datum")["vrsta"]
    .count()
    .reindex(date_range)
    .fillna(0)
)
color = "orange"
figs["Driska (št. na teden)"] = px.bar(
    x=driska.index,
    y=driska,
    color_discrete_sequence=[color],
    # labels=dict(x="Datum", y="Driska (št. na teden)"),
)
# figs["Driska (št. na teden)"].add_traces(
#     px.line(
#         x=driska.index,
#         y=driska.rolling("7d", center=True).sum(),
#         color_discrete_sequence=[color],
#     ).data,
# )
# %%
# driska_df = (
#     df_drugo[df_drugo.vrsta.isin(["driska", "mehko kakanje"])]
#     .assign(n=1)
#     .groupby(["datum", "vrsta"], as_index=False)["n"]
#     .count()
#     .pivot(index="datum", columns="vrsta", values="n")
#     .reindex(date_range)
#     .fillna(0)
#     .reset_index(names="datum")
#     .melt(id_vars="datum", value_name="n")
# )
# figs["Driska (št. na teden)"] = px.bar(
#     data_frame=driska_df,
#     x="datum",
#     y="n",
#     color="vrsta",
# )
# %%
df_drugo_vrste_izbor = [
    "infuzija s.c. (mL)",
    "mirataz (uho)",
    "reglan (10mg tablete)",
    "prevomax",
    "vominil (mg)",
    "farmatan (tablete)",
    "milprazon (tablete)",
    "Erycitol (B12) (mL)",
]
df_drugo_for_plot = df_drugo[df_drugo.vrsta.isin(df_drugo_vrste_izbor)].copy()
df_drugo_for_plot["datum_plus_1"] = df_drugo_for_plot.datum + pd.Timedelta(days=1)
df_drugo_for_plot["vrsta"] = pd.Categorical(
    df_drugo_for_plot.vrsta, df_drugo_vrste_izbor
)

figs["Zdravila"] = px.timeline(
    data_frame=df_drugo_for_plot.sort_values("vrsta", ascending=False),
    x_start="datum",
    x_end="datum_plus_1",
    y="vrsta",
)

# %%
preselected_subplots = [
    "Pojedel (kcal)",
    "Teža (g)",
    "Prednicortone (5 mg tablete)",
    "Bruhanje (št. na teden)",
    "Driska (št. na teden)",
]

selected_subplots = st.multiselect(
    "Izbira grafov", figs.keys(), default=preselected_subplots
)

st.button("Osveži podatke", on_click=get_data.clear)

# %%
fig_out = make_subplots(
    rows=len(selected_subplots),
    cols=1,
    shared_xaxes=True,
    subplot_titles=selected_subplots,
    vertical_spacing=0.05,
)

# Add traces from px figures
for i, fig_key in enumerate(selected_subplots, start=1):
    for trace in figs[fig_key].data:
        fig_out.add_trace(trace, row=i, col=1)
        if fig_key == "Zdravila":
            fig_out.update_yaxes(selector=i - 1, dtick=1)

fig_out.update_xaxes(type="date")
fig_out.update_layout(height=700, width=600)

# %%
st.plotly_chart(fig_out)

st.markdown(f"[Izvorni podatki](https://docs.google.com/spreadsheets/d/{FILE_ID})")
