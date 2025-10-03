# %%
import datetime
from zoneinfo import ZoneInfo
from babel.dates import format_date
import pandas as pd
import streamlit as st
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio
from utils import get_data, FILE_ID
from jinja2 import Template

st.set_page_config(layout="wide")


@st.cache_data(show_spinner="Nalaganje podatkov...")
def get_data_cached() -> pd.DataFrame:
    return get_data()


if "first_load" not in st.session_state:
    st.session_state.first_load = True
    st.cache_data.clear()


data = get_data_cached()
figs = {}


df_hrana = pd.merge(data["log_hrana"], data["vrste_hrana"], how="left", on="vrsta")
df_hrana["pojedel_kcal"] = df_hrana.apply(
    lambda row: row.pojedel_g * row.kcal_per_g, axis="columns"
)
df_hrana["pojedel_procent"] = df_hrana["pojedel_kcal"] / 225 * 100

# %%
# with st.expander("Kumulativno procenti dnevnih kalorij", expanded=True):
st.markdown("## Kumulativno procenti dnevnih kalorij")


def get_plot_kcal_kumulativa(df_hrana, date_start, date_end, current_datetime):
    kcal = df_hrana.set_index("cas")["pojedel_kcal"].loc[
        date_start : date_end + datetime.timedelta(days=1)
    ]
    df = pd.DataFrame(
        {
            "dan": kcal.index.date,
            "ura": kcal.index.time,
            "kcal": kcal,
        },
        index=kcal.index,
    )
    df = pd.concat(
        [
            df,
            pd.DataFrame(
                [
                    {"dan": d, "ura": datetime.time(0, 0), "kcal": 0}
                    for d in df["dan"].unique()
                ]
            ),
            pd.DataFrame(
                [
                    (
                        {"dan": d, "ura": current_datetime.time(), "kcal": 0}
                        if d == current_datetime.date()
                        else {"dan": d, "ura": datetime.time(23, 59), "kcal": 0}
                    )
                    for d in df["dan"].unique()
                ]
            ),
        ]
    ).sort_values(["dan", "ura"])

    df["ura"] = df["ura"].map(
        lambda t: datetime.datetime.combine(current_datetime.date(), t)
    )
    df["kcal_kumulativa"] = df.groupby("dan")["kcal"].cumsum()
    df["kcal_kumulativa_procent"] = df["kcal_kumulativa"] / 225 * 100

    fig = px.line(
        df,
        x="ura",
        y="kcal_kumulativa_procent",
        color="dan",
        line_shape="hv",
        markers=True,
    )

    for trace in fig.data:
        trace.opacity = 1.0 if trace.name == str(date_end) else 0.3
    fig.update_traces(marker=dict(size=5))
    fig.add_vline(x=current_datetime, line_width=1, line_color="red", opacity=0.5)
    fig.update_layout(legend={"traceorder": "reversed"})

    return fig


current_datetime = datetime.datetime.now(tz=ZoneInfo("Europe/Ljubljana"))
date_start = datetime.date(2025, 7, 18)
date_end = current_datetime.date()
fig_kcal_kumulativa = get_plot_kcal_kumulativa(
    df_hrana,
    date_start=date_start,
    date_end=date_end,
    current_datetime=current_datetime,
)
st.plotly_chart(fig_kcal_kumulativa)


# %%
# with st.expander("Grafi po dnevih", expanded=True):
st.markdown("## Grafi po dnevih")


def get_plot_hrana_vs_vrsta(df, value_col="pojedel_g"):
    df_pivot = (
        df.set_index("cas")
        .groupby("vrsta")
        .resample("1d")[value_col]
        .sum()
        .unstack("vrsta")[df["vrsta"].unique()]
    )
    fig = px.area(df_pivot, y=df_pivot.columns[1:])
    for i in fig["data"]:
        i["line"]["width"] = 0
    return fig


figs["Hrana (g)"] = get_plot_hrana_vs_vrsta(df_hrana, "pojedel_g")
figs["Hrana (kcal)"] = get_plot_hrana_vs_vrsta(df_hrana, "pojedel_kcal")


def plot_pojedel_nacin(df):
    df = df[df["cas"] > "2025-07-17"]
    df["nacin"] = (
        df["nacin"]
        .astype("category")
        .cat.set_categories(["sam", "z roke / ponujeno", "po sondi"], ordered=True)
    )
    df = (
        df.set_index("cas")
        .groupby("nacin")["pojedel_kcal"]
        .resample("1d", include_groups=False)
        .sum()
        .reset_index()
    )
    df["pojedel_procent"] = df["pojedel_kcal"] / 225 * 100
    fig = px.bar(
        df,
        x="cas",
        y="pojedel_procent",
        color="nacin",
        color_discrete_map={
            "sam": "#2CA02C",
            "z roke / ponujeno": "#DBC900",
            "po sondi": "#F54927",
        },
        barmode="relative",
    )

    return fig


figs["Pojedel način [%]"] = plot_pojedel_nacin(df_hrana)


def get_scatterplot_with_trendline(df, value_col, agg_func, color="blue"):
    s = df.set_index("cas").resample("1d")[value_col].aggregate(agg_func)
    fig = px.scatter(
        x=s.index,
        y=s,
        trendline="rolling",
        trendline_options=dict(window="7d"),
        color_discrete_sequence=[color],
    )
    fig.update_traces(
        marker={"size": 4, "opacity": 0.9},
        line={"width": 1.5},
    )
    return fig


figs["Pojedel (kcal)"] = get_scatterplot_with_trendline(
    df_hrana, "pojedel_kcal", agg_func="sum", color="green"
)
figs["Pojedel (%)"] = get_scatterplot_with_trendline(
    df_hrana, "pojedel_procent", agg_func="sum", color="green"
)
figs["Pojedel (g)"] = get_scatterplot_with_trendline(
    df_hrana, "pojedel_g", agg_func="sum", color="green"
)
figs["Teža (g)"] = get_scatterplot_with_trendline(
    data["log_teza"], "teza_g", agg_func="mean", color="orange"
)


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
    data["log_drugo"],
    "Prednicortone (prednisolone 5mg tablete) [tablet]",
    kolicina=True,
    color="blue",
)
figs["Zofran (ondansetron 4mg tablete) [tablet]"] = get_plot_drugo(
    data["log_drugo"],
    "Zofran (ondansetron 4mg tablete) [tablet]",
    kolicina=True,
    color="blue",
)
figs["Leukeran (chlorambucil 2mg tablete) [tablet]"] = get_plot_drugo(
    data["log_drugo"],
    "Leukeran (chlorambucil 2mg tablete) [tablet]",
    kolicina=True,
    color="blue",
)
figs["Cerenia (maropitant 16 mg tablete) [tablet]"] = get_plot_drugo(
    data["log_drugo"],
    "Cerenia (maropitant 16 mg tablete) [tablet]",
    kolicina=True,
    color="blue",
)
figs["Bruhanje"] = get_plot_drugo(
    data["log_drugo"], "bruhanje", kolicina=False, color="red"
)
figs["Driska"] = get_plot_drugo(
    data["log_drugo"], "driska", kolicina=False, color="orange"
)
figs["Mehko kakanje"] = get_plot_drugo(
    data["log_drugo"], "mehko kakanje", kolicina=False, color="orange"
)
figs["Infuzija (mL)"] = get_plot_drugo(
    data["log_drugo"], "infuzija s.c. (mL)", kolicina=True
)
figs["Reglan (10mg tablete)"] = get_plot_drugo(
    data["log_drugo"],
    "Reglan (metoclopramide 10 mg tablete) [tablet]",
    kolicina=True,
)
figs["Farmatan (tablete)"] = get_plot_drugo(
    data["log_drugo"], "farmatan (tablete)", kolicina=True
)
figs["Prevomax (mL)"] = get_plot_drugo(
    data["log_drugo"], "Prevomax (maropitant 10 mg/mL) [mL]", kolicina=True
)
figs["Mirataz"] = get_plot_drugo(data["log_drugo"], "mirataz (uho)", kolicina=False)

selected_subplots = st.multiselect(
    "Izbira grafov",
    figs.keys(),
    default=[
        "Pojedel način [%]",
        "Teža (g)",
        "Leukeran (chlorambucil 2mg tablete) [tablet]",
    ],
)

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
fig_out.update_xaxes(tickangle=-90)
# fig_out.update_xaxes(dtick='w1')
# fig_out.update_xaxes(range=["2025-07-15", current_datetime.strftime("%Y-%m-%d")])
fig_out.update_xaxes(
    range=[
        (current_datetime - datetime.timedelta(days=180)).strftime("%Y-%m-%d"),
        current_datetime.strftime("%Y-%m-%d"),
    ]
)
fig_out.update_layout({"barmode": "stack"})
fig_out.update_layout(height=700, width=600)

st.plotly_chart(fig_out)


# %%
st.markdown(f"## Dnevnik")


def get_summary_for_dates(date_start, date_end, kategorije):
    template = Template(
        """
{% for item in items %}
### {{ item.date }}
Teža (g): {{item.teza}}

Pojedel (kcal): {{item.kcal}} ({{item.kcal_percent}}%)

{{ item.entries }}
{% endfor %}
"""
    )
    date_range = pd.date_range(date_start, date_end)
    kcal = (
        df_hrana.set_index("cas")
        .resample("1d")["pojedel_kcal"]
        .sum()
        .reindex(date_range)
    )
    teza = (
        data["log_teza"]
        .set_index("cas")
        .resample("1d")["teza_g"]
        .mean()
        .reindex(date_range)
    )

    df = data["log_drugo"].join(data["vrste_drugo"].set_index("vrsta"), on="vrsta")
    df = df[df.tip.isin(kategorije)]
    df = df[df["cas"].dt.date.between(date_start, date_end)]
    df["dan"] = df["cas"].dt.date
    df["ura"] = df["cas"].dt.strftime("%H:%M")

    # Group by day and render
    items = []
    for date, group in df.sort_values(["dan", "ura"], ascending=[False, True]).groupby(
        df["dan"], sort=False
    ):
        group_df = group[["ura", "vrsta", "kolicina"]].reset_index(drop=True).fillna("")
        items.append(
            {
                "date": format_date(date, "EEE d. MMM yyyy", locale="sl_SI"),
                "teza": f"{teza.at[str(date)]:.0f}",
                "kcal": f"{kcal.at[str(date)]:.0f}",
                "kcal_percent": f"{int(round(kcal.at[str(date)]/225*100,0))}",
                "entries": (
                    group_df.to_markdown(index=False) if len(group_df) > 0 else ""
                ),
            }
        )

    rendered = template.render(items=items)
    return rendered


date_start, date_end = st.date_input(
    "Časovni razpon",
    value=(
        current_datetime.date() - datetime.timedelta(days=7),
        current_datetime.date(),
    ),
    format="YYYY-MM-DD",
)
kategorije = st.multiselect(
    "Kategorije",
    options=["kakanje_bruhanje", "zdravilo", "probiotik_dodatek"],
    default=["kakanje_bruhanje", "zdravilo"],
)

st.markdown(get_summary_for_dates(date_start, date_end, kategorije))

# %%
st.markdown(f"[Izvorni podatki](https://docs.google.com/spreadsheets/d/{FILE_ID})")
