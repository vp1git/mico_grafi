# %%
px.scatter(
    x=pojedel_kcal.reindex(date_range).interpolate(),
    y=teza.reindex(date_range).interpolate(),
    labels=dict(x="Pojedel (kcal)", y="Teža")
)
# %%
px.histogram(
    x=pojedel_kcal,
    labels=dict(x="Pojedel (kcal)")
)
# %%
px.histogram(
    x=teza.reindex(date_range).interpolate(),
    labels=dict(x="Teža (g)")
)