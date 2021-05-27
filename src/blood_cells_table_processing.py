import skimage
import skimage.filters
from pathlib import Path
import io3d
from matplotlib import pyplot as plt
import scipy
import exsu
from skimage.morphology import label
from scipy.ndimage.morphology import binary_closing, binary_erosion, binary_opening, binary_dilation
from skimage.color import label2rgb
from skimage.measure import regionprops, regionprops_table
import skimage.io
import pandas as pd
from sklearn import datasets
import numpy as np
import seaborn as sns
import sklearn.model_selection
import exsu
import datetime
from loguru import logger

#%%

separate_cells = False
# 271px = 10um
# pxsz_mm = 0.010/271
debug = True
debug = False
pxsz_um = 10.0/271.0
pxsz_um
min_size_um2 = 5.
max_size_um2 = 40.
#%%

report = exsu.Report('graphics', show=debug)

df = pd.read_csv("blood_cells.csv", index_col=0).reset_index()

#%% md

# Remove large cells

#%%


dfs = df[df.area < (0.9e4 * pxsz_um**2)]

#     y = 1
#
# elif props.area > 2.9e4:
#     y = 1
# else:
#
#     # normal size
#     if (props.perimeter**2) / props.area < 15.5:
#         y = 2
#     else:
#         y = 3

#%%

dfs = dfs[(dfs['cl'] == 1) | (dfs['cl']==5)]
dfs.cl.unique()

#%%

def rem(keys, key):
    if key in keys:
        keys.remove(key)
dfs

#%%

keys = list(df.keys())
keys.remove("index")
keys.remove("label")
keys.remove("cl")
rem(keys, "class")
rem(keys, "min_intensity")
rem(keys, "max_intensity")
rem(keys, "mean_intensity")
rem(keys, "q1_intensity")
rem(keys, "q2_intensity")
rem(keys, "filename")
# if "class" in keys:
#     keys.remove("class")
keys

#%%

dfs

#%%

# sns.pairplot(data=dfs, hue="cl", vars=keys)
# plt.savefig("pairplot.pdf")

#%%

vars=["area", "perimeter", "major_axis_length", "minor_axis_length", 'solidity', 'eccentricity', "noncompactness"]


sns.pairplot(data=dfs, hue="cl",
             # size="cl",
             # style="cls",
             vars=vars)
report.savefig("cl")




#%% md

# Schistocyt separation

#%%

sns.pairplot(data=dfs, hue="schistocyt",
             # size="cl",
             # style="cls",
             vars=vars)

report.savefig("schistocyt")



#%% md

# Schistocyt separation

#%%

sns.pairplot(data=dfs[dfs.schistocyt==True], hue="cl",
             # size="cl",
             # style="cls",
             # vars=["area", "perimeter", "mima", "major_axis_length", "minor_axis_length", "noncompactness"])
             vars=vars
             )

report.savefig("cl_schistocytT")
#%%

sns.pairplot(data=dfs[dfs.schistocyt==False], hue="cl",
             # size="cl",
             # style="cls",
             vars=vars
             # vars=["area", "perimeter", "mima", "major_axis_length", "minor_axis_length", "noncompactness"])
             )

report.savefig("cl_schistocytF")
#%%

dfs.describe()

#%%

dfs.im_id


#%%


sns.displot(data=dfs, x="minor_axis_length", hue="cl", kind="kde", fill=True)

#%%

# g = sns.PairGrid(dfs, x_vars="im_id", hue="cl")
g = sns.FacetGrid(dfs, row="im_id")
g.map_dataframe(sns.kdeplot, x="minor_axis_length", hue="cl")

#%%

pd.pivot_table(dfs, columns="im_id", index=["cl", "schistocyt"], values="minor_axis_length", aggfunc="count")

#%%

dfs.minor_axis_length

#%%

import scipy.stats
bins = 10
prop = "minor_axis_length"
prop = "major_axis_length"
prop = "mima"
a = np.array(dfs[dfs.cl==1]["minor_axis_length"][dfs.im_id>0])
b = np.array(dfs[dfs.cl==5]["minor_axis_length"][dfs.im_id>0])
# np.random.random(a.size)
sns.histplot(dfs, x=prop, hue="cl", bins=bins)
print(scipy.stats.kstest(list(a),list(b), N=bins))

print(len(a), len(b))
ya, bn = np.histogram(a, bins=bins)
yb, bn = np.histogram(b, bins=bn)
scipy.stats.chisquare(ya,yb)

#%% md

## Checking hypothesis testing

#%%

bins = 20
aa = a + 0.1  * np.random.standard_normal(a.shape)
sns.histplot([a, aa], bins=bins)
print(scipy.stats.kstest(list(a),list(aa), N=bins))


ya, bn = np.histogram(a*10, bins=bins)
yb, bn = np.histogram(aa*19, bins=bn)
scipy.stats.chisquare(ya,yb)

#%%

scipy.__version__


#%%

np.random.standard_normal([10])


#%%


