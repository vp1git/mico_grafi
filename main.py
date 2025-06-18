# %%
import pandas as pd
import plotly.express as px

df_raw = pd.read_excel("./data/Mico - kalorije.ods", sheet_name="Tabela", skiprows=3)
list(enumerate(df_raw.columns.to_list()))

# %%
df_hrana = pd.concat([df_raw["datum"], df_raw.iloc[:, 1:24]], axis="columns")

# %%
hrana_by_appearance = (
    df_hrana.melt(id_vars="datum")
    .groupby("variable")
    .apply(lambda x: x.reset_index().value.first_valid_index())
    .reset_index(name="first_appear")
    .sort_values("first_appear")
    .variable.to_list()
)

df_hrana = df_hrana[["datum"] + hrana_by_appearance]
df_hrana
# %%
figs = {}
# %%
figs["hrana"] = px.area(df_hrana, x="datum", y=df_hrana.columns[1:], title="Hrana (g)")
for i in figs["hrana"]["data"]:
    i["line"]["width"] = 0
figs["hrana"]


# %%
# df_hrana = pd.concat(
#     [df_raw["datum"], df_raw.iloc[:, 2:19] > 0],
#     axis="columns",
# )
# df_hrana
# figs["hrana"] = px.imshow(
#     df_hrana.set_index("datum").transpose(),
#     aspect="auto",
#     color_continuous_scale=["white", "green"],  # or any two colors
#     # labels=dict(x="Date", y="Category", color="True/False"),
#     title="Hrana"
# )
# figs["hrana"].update_coloraxes(showscale=False)  # Hide color bar if desired
# figs["hrana"]


# %%
column_map = {
    "datum": "datum",
    "skupaj vse (kcal)": "pojedel_kcal",
    "tehtanje (g)": "teza_g",
    "bruhal": "bruhal",
    "driska": "driska",
    "prednisolone (5mg tablete)": "prednicortone_5mg",
}
df = df_raw[column_map.keys()].rename(columns=column_map)
df["bruhal"] = df["bruhal"].notna()
df["driska"] = df["driska"].notna()
df["prednicortone_5mg"] = df["prednicortone_5mg"].fillna(0)

# %%
# px.line(x=df.datum, y=df.bruhal.rolling(30).mean())

# %%
figs["pojedel_kcal"] = px.scatter(
    x=df.datum,
    y=df.pojedel_kcal,
    trendline="rolling",
    trendline_options=dict(window="7d"),
    title="Pojedel (kcal)",
)
figs["teza_g"] = px.scatter(
    x=df.datum,
    y=df.teza_g,
    trendline="rolling",
    trendline_options=dict(window="7d"),
    title="Teža (g)",
)
figs["bruhal"] = px.line(
    x=df.datum,
    y=df.bruhal.rolling(window=7).sum(),
    title="Bruhanje (dni na teden)",
)
figs["driska"] = px.line(
    x=df.datum,
    y=df.driska.rolling(window=7).sum(),
    title="Driska (dni na teden)",
)
figs["prednicortone_5mg"] = px.bar(
    x=df.datum, y=df.prednicortone_5mg, title="Prednicortone (5 mg tablete)"
)

for fig in [figs["pojedel_kcal"], figs["teza_g"]]:
    fig.update_traces(
        marker={"size": 4, "opacity": 1},
        line={"width": 1},
    )

# %%
# for fig in figs.values():
#     fig.show()

# %%
from plotly.graph_objects import Figure
from plotly.subplots import make_subplots
from datetime import date

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

fig_out.show()
fig_out.write_html(f"output/Mico {date.today()}.html")

# %%
#
#
#
#
#
#
#
#
# %%
from datetime import datetime

df2 = df.copy()
df2["bruhal"]
df_melted = df.melt(id_vars="datum")
fig = px.scatter(
    data_frame=df_melted,
    x="datum",
    y="value",
    facet_row="variable",
    # trendline="rolling",
    # trendline_options=dict(window=7),
)

dose_change_dates = {
    "5.00 mg": datetime(2025, 3, 21),
    "3.75 mg": datetime(2025, 4, 23),
    "2.5 mg": datetime(2025, 5, 5),
}
for dose, date in dose_change_dates.items():
    fig.add_vline(
        x=date.timestamp() * 1000,
        line_width=0.5,
        # line_dash="dot",
        annotation_text=dose,
        annotation_position="bottom",
    )
fig.update_yaxes(matches=None)
fig.for_each_annotation(lambda a: a.update(text=a.text.replace("variable=", "")))
fig.update_traces(
    marker={"size": 3, "opacity": 1},
    line={"width": 0.8},
)
fig.write_html("output/Mico 2025-05-28.html")
# %%

df_raw["bruhal"].unique()

# %%
df_hrana.melt(id_vars="datum").dropna().to_clipboard()

# %%
pd.DataFrame(df_raw.columns)
# %%
df_drugo = df_hrana = pd.concat(
    [df_raw["datum"], df_raw.iloc[:, 30:32], df_raw.iloc[:, 34:]], axis="columns"
)
df_drugo.melt(id_vars="datum").dropna().to_clipboard()
# %%
