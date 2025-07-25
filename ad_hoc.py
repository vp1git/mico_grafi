# %%
from utils import get_data
import pandas as pd
import plotly.express as px

# %%
data = get_data()


# %%
df_hrana = pd.merge(data["log_hrana"], data["vrste_hrana"], how="left", on="vrsta")
df_hrana["pojedel_kcal"] = df_hrana.apply(
    lambda row: row.pojedel_g * row.kcal_per_g, axis="columns"
)


# %%
def get_plot_hrana_vs_vrsta(df, value_col="pojedel_kcal"):
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


get_plot_hrana_vs_vrsta(df_hrana)


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


get_plot_hrana_pojedel(df_hrana, "pojedel_g")


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


get_plot_teza(data["log_teza"])


# %%
def get_plot_driska(df):
    driska = (
        # df[df.vrsta.isin(["driska", "mehko kakanje"])]
        df[df.vrsta.isin(["driska"])]
        .set_index("cas")
        .resample("1d")["vrsta"]
        .count()
    )
    fig = px.bar(
        x=driska.index,
        y=driska,
        color_discrete_sequence=["orange"],
        # labels=dict(x="Datum", y="Driska"),
    )
    return fig


get_plot_driska(data["log_drugo"])


# %%
def get_plot_drugo(df, vrsta, kolicina=False, color='blue'):
    s = df[df.vrsta.isin([vrsta])].set_index("cas")
    if kolicina:
        s = s.resample('1d')['kolicina'].sum()
    else:
        s = s.resample("1d")["vrsta"].count()
    fig = px.bar(
        x=s.index,
        y=s,
        color_discrete_sequence=[color],
        labels=dict(x="Datum", y=vrsta),
    )
    return fig


get_plot_drugo(data["log_drugo"], 'bruhanje', kolicina=False, color='red')
get_plot_drugo(data["log_drugo"], 'prednisolone (5mg tablete)', kolicina=True, color='blue')
get_plot_drugo(data["log_drugo"], 'driska', kolicina=False, color='orange')
get_plot_drugo(data["log_drugo"], 'infuzija s.c. (mL)', kolicina=True)


# %%
def get_plot_zdravila(df_in):
    zdravila_izbor = [
        "infuzija s.c. (mL)",
        "mirataz (uho)",
        "reglan (10mg tablete)",
        "prevomax",
        "vominil (mg)",
        "farmatan (tablete)",
        "milprazon (tablete)",
        "Erycitol (B12) (mL)",
    ]
    df = df_in[df_in.vrsta.isin(zdravila_izbor)].copy()
    df["info"] = df_in.apply(
        lambda row: f"[{row.ura} :: {row.kolicina}]", axis="columns"
    )
    df = (
        df.groupby(["datum", "vrsta"])["info"]
        .aggregate(lambda x: " , ".join(x))
        .reset_index()
    )
    df["x_start"] = df.datum - pd.Timedelta(days=0.4)
    df["x_end"] = df.datum + pd.Timedelta(days=0.4)
    df["vrsta"] = pd.Categorical(df.vrsta, zdravila_izbor)

    fig = px.timeline(
        data_frame=df.sort_values("vrsta", ascending=False),
        x_start="x_start",
        x_end="x_end",
        y="vrsta",
        hover_data=["datum", "vrsta", "info"],
    )
    return fig


# %%
#
#
#
#
#
#
#
#
#
# %%

# %%
import pandas as pd
import locale
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

locale.setlocale(locale.LC_ALL, "sl_SI")
# %%
datum_format = "%A, %d. %B %Y"

df_kcal = (
    pd.read_table(
        "kcal.txt",
        parse_dates=["datum"],
        date_format=datum_format,
        index_col="datum",
    )
    .groupby("datum")
    .aggregate("sum")
)
df_g = (
    pd.read_table(
        "g.txt",
        parse_dates=["datum"],
        date_format=datum_format,
        index_col="datum",
    )
    .groupby("datum")
    .aggregate("mean")
)

# %%
df = df_kcal.join(df_g, on="datum", how="outer")
# # %%
# df = df.rolling("7d").mean()
# df["g_delta"] = df.g.shift(0) - df.g.shift(7)

# %%
df = df.resample("7d").mean()  # .rolling('14d').mean()
df["g_delta"] = df.g.shift(0) - df.g.shift(1)

# %%
# fig1 = px.line(df, y=["g_delta", "kcal"])
fig1 = make_subplots(rows=2, cols=1)
fig1.add_trace(go.Line(x=df.index, y=df.kcal, name="kcal"), row=1, col=1)
fig1.add_trace(go.Line(x=df.index, y=df.g_delta), row=2, col=1)
fig1.update_yaxes(title_text="kcal", row=1, col=1)
fig1.update_yaxes(title_text="∆ g", row=2, col=1)
fig1.update_layout(showlegend=False)
fig1.show()

fig2 = px.scatter(
    df,
    x="kcal",
    y="g_delta",
    # trendline="lowess", trendline_options=dict(frac=0.9),
    trendline="ols",  # trendline_options=dict(log_x=True),
    trendline_scope="overall",
)
fig2.update_layout(showlegend=False)
fig2.show()
# results = px.get_trendline_results(fig2)
# print(results.iat[0, 0].summary())

# %%
#
#
#
#
#
# %%
px.scatter(
    x=pojedel_kcal.reindex(date_range).interpolate(),
    y=teza.reindex(date_range).interpolate(),
    labels=dict(x="Pojedel (kcal)", y="Teža"),
)
# %%
px.histogram(x=pojedel_kcal, labels=dict(x="Pojedel (kcal)"))
# %%
px.histogram(x=teza.reindex(date_range).interpolate(), labels=dict(x="Teža (g)"))
