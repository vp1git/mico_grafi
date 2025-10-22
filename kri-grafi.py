# %%
from utils import get_data
import seaborn as sns
import matplotlib.dates as mdates
from datetime import datetime

# %%
data = get_data()
df_kri = data["kri"]
df_kri_cols = data["kri_stolpci"]

# %%
df_kri_melted = df_kri.melt(id_vars="cas")
df_kri_cols = df_kri_cols.set_index("kratica")

# %%
sns.set_style("whitegrid")
g = sns.FacetGrid(df_kri_melted, col="variable", col_wrap=6, sharey=False)
g.map(sns.lineplot, "cas", "value", marker="o", linewidth=0.5)

for ax, variable in zip(g.axes.flat, df_kri_cols.index):
    lower = df_kri_cols["od"][variable]
    upper = df_kri_cols["do"][variable]
    ax.axhspan(lower, upper, linewidth=2, color="green", alpha=0.3)
    ax.tick_params(axis="x", labelrotation=90, labelbottom=True)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.set_title(f'{variable} [{df_kri_cols["merska enota"][variable]}]', size=16)

g.fig.subplots_adjust(hspace=0.5)
g.set_axis_labels("", "")

# %%
current_date = datetime.now().strftime("%Y-%m-%d")
g.savefig(f"output/Mico - kri grafi - {current_date}.pdf")

# %%
