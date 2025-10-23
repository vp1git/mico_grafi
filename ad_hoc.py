# %%
import datetime
from utils import get_data
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

pd.options.plotting.backend = "plotly"

# %%
data = get_data()
df_hrana = pd.merge(data["log_hrana"], data["vrste_hrana"], how="left", on="vrsta")
df_hrana["pojedel_kcal"] = df_hrana.apply(
    lambda row: row.pojedel_g * row.kcal_per_g, axis="columns"
)


#
#
#
# %%
pojedel_kcal = df_hrana[df_hrana["cas"] > "2025-07-17"].set_index("cas")["pojedel_kcal"]
pojedel_delta = pojedel_kcal.resample("1h").sum() - (225 / 24)

df_drugo = data["log_drugo"]
leukeran_datumi = df_drugo["cas"][df_drugo["vrsta"].str.contains("Leukeran")].dt.date

fig = px.line(pojedel_delta.cumsum())

for i in leukeran_datumi:
    fig.add_vline(i, line_width=0.5, opacity=0.7)

fig.add_vline("2025-09-08", line_dash="dot", line_width=0.5, opacity=0.7)
fig.add_vline("2025-08-14", line_dash="dash", line_width=0.5, opacity=0.7)
fig.add_vline("2025-10-02", line_dash="dash", line_width=0.5, opacity=0.7)
# fig.update_xaxes(rangeslider_visible=True)
fig
# %%

# %%
#
data["log_drugo"]
#
#
#


# %%
def plot_hrana_sam_sonda(df_hrana, procent=True):
    df = df_hrana.copy().set_index("cas")
    sam = df["pojedel_kcal"][df["nacin"].isin(["sam", "z roke / ponujeno"])]
    sonda = df["pojedel_kcal"][df["nacin"].isin(["po sondi"])]
    df = pd.concat(
        {
            "sam / z roke": sam.resample(
                "1d",
            )
            .sum()
            .reindex(pd.date_range("2025-07-17", "2025-08-26")),
            "sonda": sonda.resample("1d")
            .sum()
            .reindex(pd.date_range("2025-07-17", "2025-08-26")),
        },
        axis="columns",
    ).melt(ignore_index=False, value_name="pojedel_kcal", var_name="nacin")
    df["pojedel_procent"] = df["pojedel_kcal"] / 225 * 100

    if procent:
        y = "pojedel_procent"
        hline = 100
    else:
        y = "pojedel_kcal"
        hline = 225
    fig = (
        px.bar(
            df,
            y=y,
            color="nacin",
            # color_discrete_sequence=["darkgray", "lightgray"],
            template="plotly_white",
        )
        .add_hline(hline, line_dash="dash")
        .update_xaxes(dtick="1d", tickangle=90)
    )

    return fig


plot_hrana_sam_sonda(df_hrana, procent=False)


#
#
#
# %%
def plot_bruhanje_kakanje(df_log_drugo, df_vrste_drugo):
    df = data["log_drugo"].join(data["vrste_drugo"].set_index("vrsta"), on="vrsta")
    df = df[df["tip"] == "kakanje_bruhanje"]
    df["tip"] = df["vrsta"].map(lambda x: "bruhanje" if x == "bruhanje" else "kakanje")
    df = df[df["cas"] >= datetime.datetime(2025, 7, 17)]
    fig = (
        px.scatter(
            df,
            x="cas",
            y="tip",
            color="vrsta",
            height=180,
            color_discrete_map={
                "bruhanje": "red",
                "driska": "yellow",
                "mehko kakanje": "orange",
                "kakanje dobro": "brown",
                "kakanje trdo": "black",
            },
        )
        .update_xaxes(dtick="1d", tickangle=90)
        .update_layout(
            legend=dict(
                orientation="h",  # show entries horizontally
                xanchor="center",  # use center of legend as anchor
                x=0.5,
                y=-1,
            )
        )
    )
    return fig


plot_bruhanje_kakanje(data["log_drugo"], data["vrste_drugo"])

#
#
#
# %%
df = data["log_drugo"]
time = df.cas.dt.time[df.vrsta == "bruhanje"]
time = [t.hour for t in time if t != (datetime.time(0, 0))]
# px.bar(x=time,points='all')
px.histogram(x=time, nbins=24)

# %%
from babel.dates import format_date

# %%
from zoneinfo import ZoneInfo

current_datetime = datetime.datetime.now(tz=ZoneInfo("Europe/Ljubljana"))
date_start, date_end = (
    current_datetime.date() - datetime.timedelta(days=7),
    current_datetime.date(),
)
df = data["log_drugo"].join(data["vrste_drugo"].set_index("vrsta"), on="vrsta")
df = df[df["cas"].dt.date.between(date_start, date_end)]
df["dan"] = df["cas"].dt.date
df["ura"] = df["cas"].dt.time
# %%
[i.strftime("%a %-d. %b %Y") for i in df.dan]
[format_date(i, locale="sl_SI") for i in df.dan]

# %%
df = pd.DataFrame(
    {
        "kcal": df_hrana.set_index("cas")["pojedel_kcal"].resample("1d").sum(),
        "g": data["log_teza"].set_index("cas")["teza_g"].resample("1d").mean(),
    }
)
df["g"] = df["g"].interpolate()
df
# # %%
# df = df.rolling("7d").mean()
# df["g_delta"] = df.g.shift(0) - df.g.shift(7)

# %%
# df = df.resample("7d").mean()  # .rolling('14d').mean()
df = df.resample("3d").mean()  # .rolling('14d').mean()
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
    color="g",
    color_continuous_scale="solar",
    # trendline="lowess", trendline_options=dict(frac=0.9),
    trendline="ols",  # trendline_options=dict(log_x=True),
    trendline_scope="overall",
)
fig2.update_layout(showlegend=False)
fig2.show()
# results = px.get_trendline_results(fig2)
# print(results.iat[0, 0].summary())

# %%


# px.scatter(df, x='ura', y='kcal_kumulativa_procent', color='dan')
# %
#
#
#
#
#
# %%
for day, data in data["log_drugo"].set_index("cas").resample("1d"):
    print(day)
    print(data)
#    print('--------')
# %%
df = data["log_drugo"]
df["dan"] = df["cas"].dt.date
df


# %%
#
#
#
#
#
# %%
pojedel_kcal = df_hrana["pojedel_kcal"]
px.scatter(
    x=pojedel_kcal.reindex(date_range).interpolate(),
    y=teza.reindex(date_range).interpolate(),
    labels=dict(x="Pojedel (kcal)", y="Teža"),
)
# %%
px.histogram(x=pojedel_kcal, labels=dict(x="Pojedel (kcal)"))
# %%
px.histogram(x=teza.reindex(date_range).interpolate(), labels=dict(x="Teža (g)"))
