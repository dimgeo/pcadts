import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# ------------------------------
# INLEZEN EN VOORBEREIDEN
# ------------------------------

# Sterftedata
mortality_df = pd.read_csv("fixed.csv")  # kolommen: yearweek, age, deaths
mortality_df["date"] = pd.to_datetime(mortality_df["yearweek"] + '-1', format='%G-W%V-%u')
mortality_df["year"] = mortality_df["date"].dt.year

# Eurostat leeftijdsgroepen
eurostat_groups = ['Y60-64', 'Y65-69', 'Y70-74', 'Y75-79', 'Y80-84', 'Y85-89', 'Y_GE90']
mortality_df = mortality_df[mortality_df["age"].isin(eurostat_groups)].copy()

# Bevolkingsdata
pop_df = pd.read_csv("leeftijdsopbouw.csv", header=None, names=["year", "age", "population"])
pop_df = pop_df[pop_df["year"] != "Year"].copy()
pop_df["year"] = pop_df["year"].astype(int)
pop_df["age"] = pop_df["age"].astype(int)
pop_df["population"] = pd.to_numeric(pop_df["population"], errors="coerce")

# Leeftijdsgroepen groeperen
age_bins = [
    ("Y60-64", 60, 64),
    ("Y65-69", 65, 69),
    ("Y70-74", 70, 74),
    ("Y75-79", 75, 79),
    ("Y80-84", 80, 84),
    ("Y85-89", 85, 89),
    ("Y_GE90", 90, 200)
]
def assign_age_group(age):
    for label, a_min, a_max in age_bins:
        if a_min <= age <= a_max:
            return label
    return None
pop_df["age_group"] = pop_df["age"].apply(assign_age_group)
pop_df = pop_df.dropna(subset=["age_group"])

# Populatie aggregeren per groep
df_agg = pop_df.groupby(["year", "age_group"])["population"].sum().reset_index()
population_lookup = df_agg.set_index(["year", "age_group"])["population"].to_dict()

# Toevoegen populatie aan sterftedata en bereken sterfte per 100.000
mortality_df["population"] = mortality_df.apply(
    lambda row: population_lookup.get((row["year"], row["age"])), axis=1
)
mortality_df["mortality_rate"] = mortality_df["deaths"] / mortality_df["population"] * 100000

# ------------------------------
# PCA UITVOEREN
# ------------------------------

# Pivot naar wide format
mortality_pivot = mortality_df.pivot(index="date", columns="age", values="mortality_rate").sort_index()
mortality_pivot = mortality_pivot.interpolate(method='linear', limit_direction='both')

# Normaliseren (zodat PCA alleen patroonverschillen ziet)
scaler = StandardScaler()
data_scaled = scaler.fit_transform(mortality_pivot)

# PCA toepassen
pca = PCA(n_components=2)
pca_result = pca.fit_transform(data_scaled)
pca_df = pd.DataFrame(pca_result, index=mortality_pivot.index, columns=['PC1', 'PC2'])

# ------------------------------
# VISUALISATIE
# ------------------------------

# Grafiek 1: PC1 en PC2 over de tijd
plt.figure(figsize=(14, 6))
plt.plot(pca_df['PC1'], label='PC1 (algemene sterftetrend)', color='blue')
plt.plot(pca_df['PC2'], label='PC2 (verschuiving tussen leeftijden)', color='orange')
plt.title('PCA op gestandaardiseerde sterftecijfers 60+ (per 100.000)')
plt.xlabel('Tijd')
plt.ylabel('Componentwaarde')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Grafiek 2: Bijdrage van leeftijdsgroepen aan PC1 en PC2
loadings = pd.DataFrame(pca.components_.T, index=mortality_pivot.columns, columns=['PC1', 'PC2'])
bar_width = 0.35
index = np.arange(len(loadings.index))

plt.figure(figsize=(12, 5))
plt.bar(index - bar_width/2, loadings['PC1'], bar_width, label='PC1')
plt.bar(index + bar_width/2, loadings['PC2'], bar_width, label='PC2')
plt.xticks(index, loadings.index, rotation=45)
plt.title('Bijdrage van leeftijdsgroepen aan PC1 en PC2 (gestandaardiseerd)')
plt.ylabel('Component-loading')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
