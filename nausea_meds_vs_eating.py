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
df_drugo = data["log_drugo"].join(data["vrste_drugo"].set_index("vrsta"), on="vrsta")

#
# %%
df = df_drugo.copy()

# df = df[df['tip'] == "zdravilo"]
df = df[
    df["vrsta"].isin(
        [
            "Leukeran (chlorambucil 2mg tablete) [tablet]",
            "Zofran (ondansetron 4mg tablete) [tablet]",
            "Cerenia (maropitant 16 mg tablete) [tablet]",
            "Prevomax (maropitant 10 mg/mL) [mL]",
            "bruhanje",
        ]
    )
]

df = df[df["cas"] > "2025-07-17"]

df = (
    df.set_index("cas")
    .groupby("vrsta")["kolicina"]
    .resample("1d", include_groups=False)
    .sum()
    .reset_index()
)

df_zdravila = df
del df

px.bar(df_zdravila, x="cas", y="kolicina", color="vrsta", barmode="group")


# %%
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
    fig = px.bar(
        df,
        x="cas",
        y="pojedel_kcal",
        color="nacin",
        color_discrete_map={
            "sam": "#2CA02C",
            "z roke / ponujeno": "#2E91E5",
            "po sondi": "#BCBD22",
        },
        barmode="relative",
    )
    fig.add_hline(225,line_dash="dash")
    return fig


plot_pojedel_nacin(df_hrana)


# %%
df_zdravila
df_pojedel

# %%
fig = make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True,
    # subplot_titles=selected_subplots,
    vertical_spacing=0.05,
)

fig_pojedel = px.bar(
    df_pojedel,
    x="cas",
    y="pojedel_kcal",
    color="nacin",
)
fig_zdravila = px.bar(df_zdravila, x="cas", y="kolicina", color="vrsta")

for i in fig_pojedel.data:
    fig.add_trace(i, row=1, col=1)
for i in fig_zdravila.data:
    fig.add_trace(i, row=2, col=1)

fig.update_xaxes(type="date")
# fig.update_layout(height=700, width=600)
fig.update_xaxes(dtick="1d", tickangle=90)
# fig.update_layout(
#     legend=dict(
#         orientation="h",  # show entries horizontally
#         xanchor="center",  # use center of legend as anchor
#         x=0.5,
#         y=-1,
#     )
# )
fig.update_layout({"barmode": "stack"})
fig.show()

# %%
