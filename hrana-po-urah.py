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

# %%
df = (
    # df_hrana[df_hrana["cas"] > "2025-07-17"]
    df_hrana[df_hrana["cas"] > "2025-09-08"]
    .set_index("cas")[["pojedel_kcal"]]
    .resample("3h")
    .sum()
)
df["dan"] = df.index.date
df["ura"] = df.index.time

# .set_index('cas')["pojedel_kcal"].dt.gro
df
# %%
import seaborn as sns

sns.violinplot(df.sort_values("ura"), y="pojedel_kcal", x="ura")
# sns.violinplot(df.sort_values("ura"), y="pojedel_kcal", x="ura", inner="point")

# %%
