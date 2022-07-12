from matplotlib import backend_bases
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

bands_names = pd.read_csv('src/bands_names.txt', header=None, names=['names']).names.to_list()
bands = pd.read_csv('src/bands_importance.txt', header=None, names=['importance']).assign(name=bands_names)
bands.sort_values(by=['importance','name'], ascending=[False, True], inplace=True)
bands = bands[bands.importance>=0.01]

fig, ax = plt.subplots(figsize=(6,6))
sns.barplot(
    data=bands,
    x='importance',
    y='name',
    color='indianred'
)
ax.set_xlabel('Feature importance', style='italic')
ax.set_ylabel('')
plt.suptitle('Random Forest: importancia de bandas', fontsize=18)
plt.tight_layout()
plt.savefig('plots/feature_importance.png')