# %%
import pandas as pd
import streamlit as st
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio
from utils import get_data, FILE_ID

# %%
st.set_page_config(layout="wide")


@st.cache_data(show_spinner="Nalaganje podatkov...")
def get_data_cached() -> pd.DataFrame:
    return get_data()


# %%
data = get_data_cached()
figs = {}


# %%
df_hrana = pd.merge(data["log_hrana"], data["vrste_hrana"], how="left", on="vrsta")
df_hrana["pojedel_kcal"] = df_hrana.apply(
    lambda row: row.pojedel_g * row.kcal_per_g, axis="columns"
)


def get_plot_hrana_vs_vrsta(df, value_col="pojedel_g"):
    df_pivot = (
        df.set_index("cas")
        .groupby("vrsta")
        .resample("1d")[value_col]
        .sum()
        .unstack("vrsta")[df["vrsta"].unique()]
    )

    fig = px.area(df_pivot, y=df_pivot.columns[1:], title="Hrana (g)")

    for i in fig["data"]:
        i["line"]["width"] = 0
    return fig


figs["Hrana (g)"] = get_plot_hrana_vs_vrsta(df_hrana, "pojedel_g")
figs["Hrana (kcal)"] = get_plot_hrana_vs_vrsta(df_hrana, "pojedel_kcal")


# %%
def get_plot_hrana_pojedel(df, value_col="pojedel_kcal"):
    pojedel_kcal = df.set_index("cas").resample("1d")[value_col].sum()
    fig = px.scatter(
        x=pojedel_kcal.index,
        y=pojedel_kcal,
        trendline="rolling",
        trendline_options=dict(window="7d"),
        color_discrete_sequence=["green"],
        # labels=dict(x="Datum", y="Pojedel (kcal)"),
    )
    fig.update_traces(
        marker={"size": 4, "opacity": 0.9},
        line={"width": 1.5},
    )
    return fig


figs["Pojedel (kcal)"] = get_plot_hrana_pojedel(df_hrana, "pojedel_kcal")
figs["Pojedel (g)"] = get_plot_hrana_pojedel(df_hrana, "pojedel_g")


# %%
def get_plot_teza(df, value_col="teza_g"):
    teza_g = df.set_index("cas").resample("1d")[value_col].mean()
    fig = px.scatter(
        x=teza_g.index,
        y=teza_g,
        trendline="rolling",
        trendline_options=dict(window="7d"),
        # labels=dict(x="Datum", y="Teža (g)"),
    )
    fig.update_traces(
        marker={"size": 4, "opacity": 0.9},
        line={"width": 1.5},
    )
    return fig


figs["Teža (g)"] = get_plot_teza(data["log_teza"])


# %%
def get_plot_drugo(df, vrsta, kolicina=False, color="blue"):
    s = df[df.vrsta.isin([vrsta])].set_index("cas")
    if kolicina:
        s = s.resample("1d")["kolicina"].sum()
    else:
        s = s.resample("1d")["vrsta"].count()
    fig = px.bar(
        x=s.index,
        y=s,
        color_discrete_sequence=[color],
        labels=dict(x="Datum", y=vrsta),
    )
    return fig


figs["Prednicortone (5 mg tablete)"] = get_plot_drugo(
    data["log_drugo"], "prednisolone (5mg tablete)", kolicina=True, color="blue"
)
figs["Bruhanje"] = get_plot_drugo(
    data["log_drugo"], "bruhanje", kolicina=False, color="red"
)
figs["Driska"] = get_plot_drugo(
    data["log_drugo"], "driska", kolicina=False, color="orange"
)
figs["Infuzija (mL)"] = get_plot_drugo(
    data["log_drugo"], "infuzija s.c. (mL)", kolicina=True
)
figs["Reglan (10mg tablete)"] = get_plot_drugo(
    data["log_drugo"], "reglan (10mg tablete)", kolicina=True
)
figs["Farmatan (tablete)"] = get_plot_drugo(
    data["log_drugo"], "farmatan (tablete)", kolicina=True
)
figs["Prevomax (mL)"] = get_plot_drugo(data["log_drugo"], "prevomax", kolicina=True)
figs["Mirataz"] = get_plot_drugo(data["log_drugo"], "mirataz (uho)", kolicina=False)

# %%
preselected_subplots = [
    "Pojedel (kcal)",
    "Teža (g)",
    "Prednicortone (5 mg tablete)",
    "Bruhanje",
    "Driska",
]

selected_subplots = st.multiselect(
    "Izbira grafov", figs.keys(), default=preselected_subplots
)

st.button("Osveži podatke", on_click=get_data_cached.clear)

# %%
fig_out = make_subplots(
    rows=len(selected_subplots),
    cols=1,
    shared_xaxes=True,
    subplot_titles=selected_subplots,
    vertical_spacing=0.05,
)

for i, fig_key in enumerate(selected_subplots, start=1):
    for trace in figs[fig_key].data:
        fig_out.add_trace(trace, row=i, col=1)

fig_out.update_xaxes(type="date")
fig_out.update_layout(height=700, width=600)

# %%
st.plotly_chart(fig_out)

st.markdown(f"[Izvorni podatki](https://docs.google.com/spreadsheets/d/{FILE_ID})")
