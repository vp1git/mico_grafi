# %%
import pandas as pd
import plotly.express as px

df_raw = pd.read_excel("./data/Mico - kalorije.ods", sheet_name="Tabela", skiprows=3)
df_raw.columns

# %%
column_map = {
    "datum": "datum",
    "skupaj vse (kcal)": "dnevno_kcal",
    "tehtanje (g)": "teza_g",
    "bruhal": "bruhal",
    "driska": "driska",
    # "prednisolone (5mg tablete)": "prednicortone_5mg",
}
df = df_raw[column_map.keys()].rename(columns=column_map)
df["bruhal"] = df["bruhal"].notna()
df["driska"] = df["driska"].notna()
df["prednicortone_5mg"] = df["prednicortone_5mg"].fillna(0)

# %%
px.line(x=df.datum, y=df.bruhal.rolling(30).mean())

# %%
fig = px.scatter(
    x=df.datum,
    y=df["dnevno_kcal"],
    trendline="rolling",
    trendline_options=dict(window=7),
)
fig.update_traces(
    marker={"size": 4, "opacity": 1},
    line={"width": 1},
)
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
