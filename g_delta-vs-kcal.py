# %%
import pandas as pd
from datetime import datetime
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from utils import get_data

# %%
data = get_data()
df_hrana = pd.merge(data["log_hrana"], data["vrste_hrana"], how="left", on="vrsta")
df_hrana["pojedel_kcal"] = df_hrana.apply(
    lambda row: row.pojedel_g * row.kcal_per_g, axis="columns"
)


# %%
pojedel_kcal = df_hrana.set_index("cas")["pojedel_kcal"].resample("1d").sum()
teza_g = data["log_teza"].set_index("cas")["teza_g"].resample("1d").mean()
df = pd.concat({"kcal": pojedel_kcal, "g": teza_g}, axis="columns")
df = df.interpolate()

# %%
df = df.resample("3d").mean()  # .rolling('14d').mean()
df["g_delta"] = df["g"].shift(0) - df["g"].shift(1)

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
    color=[(d-datetime.now()).days for d in df.index],
    # trendline="lowess", trendline_options=dict(frac=0.9),
    trendline="ols",  #trendline_options=dict(log_x=True),
    trendline_scope="overall",
)
fig2.update_layout(showlegend=False)
fig2.show()
# results = px.get_trendline_results(fig2)
# print(results.iat[0, 0].summary())

# %%
