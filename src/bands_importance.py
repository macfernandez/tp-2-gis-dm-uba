from matplotlib import backend_bases
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

bands_names = pd.read_csv('src/bands_names.txt', header=None, names=['names']).names.to_list()
bands = pd.read_csv('src/bands_importance.txt', header=None, names=['importance']).assign(name=bands_names)
bands.sort_values(by=['importance','name'], ascending=[False, True], inplace=True)

important_bands = bands.head(28)
fig, ax = plt.subplots(figsize=(6,6))
sns.barplot(
    data=important_bands,
    x='importance',
    y='name',
    color='indianred'
)
ax.set_xlabel('Feature importance', style='italic')
ax.set_ylabel('')
plt.suptitle(f'Random Forest: {len(important_bands)} bandas con mayor importancia', fontsize=16)
plt.tight_layout()
plt.savefig('plots/feature_importance.png')

fig, ax = plt.subplots(figsize=(10,5))
sns.lineplot(
    data=bands.head(80),
    x='name',
    y='importance',
    color='indianred'
)
ax.axhline(y=0.01, color='black', linestyle='--')
ax.set_xlabel('Feature importance', style='italic')
ax.set_ylabel('')
plt.tick_params(
    axis='x',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    bottom=True,      # ticks along the bottom edge are off
    top=False,         # ticks along the top edge are off
    labelbottom=False)
plt.suptitle('Random Forest: importancia de bandas', fontsize=16)
plt.tight_layout()
plt.savefig('plots/feature_importance_line.png')
