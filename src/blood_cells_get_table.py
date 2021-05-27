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
pth = io3d.joinp("medical/orig/cardio_blood_cells/TP1_a")


odir = datetime.datetime.now().strftime("%Y%m%d_%H%M")
report = exsu.Report(odir, show=debug)
pth.exists()

min_size_px = min_size_um2 / (pxsz_um ** 2)
max_size_px = max_size_um2 / (pxsz_um ** 2)
#%% md

# Segmentation processing step by step

#%%

def q1_intensity(mask, img):
    return np.quantile(img[mask], 0.25)
def q2_intensity(mask, img):
    return np.quantile(img[mask], 0.5)
def q3_intensity(mask, img):
    return np.quantile(img[mask], 0.75)

def quartiles(regionmask, intensity):
    return np.percentile(intensity[regionmask], q=(25, 50, 75))


#%%

# for fn in pth.glob("*.jpg"):

fns = list(pth.glob("*jpg"))

dfsl = []

for fn in fns:

    im = skimage.io.imread(fn)
    plt.imshow(im)

    # report = exsu.Report("report", show=True)

    def show_if_debug(*args, debug=True, show_colorbar=False, **kwargs):
        if debug:
            plt.figure()
            plt.imshow(*args, **kwargs)
            if show_colorbar:
                plt.colorbar()
            # plt.close


    img = skimage.color.rgb2gray(im)
    # show_if_debug(img, debug=debug, show_colorbar=True)
    report.imsave(fn.name + ".png", im)

    threshold = skimage.filters.threshold_otsu(img[:])


    bim = img < threshold
    # show_if_debug(bim, debug=debug)
    report.imsave(fn.name + "_thr.png", bim)


    bimh = scipy.ndimage.binary_fill_holes(bim)
    # show_if_debug(bim, debug=debug)
    report.imsave(fn.name + "_holes.png", bimh)


    bimr = skimage.morphology.remove_small_objects(bimh, min_size=min_size_px)
    # show_if_debug(bim, debug=debug)
    report.imsave(fn.name + "_small_removed.png", bimr)

    if separate_cells:
        bimd = binary_erosion(bimr,iterations=50)
        bimd[-100:,-500:] = 0  # remove size tag
        show_if_debug(bimd, debug=debug)

        distance = scipy.ndimage.distance_transform_edt(bimr)
        show_if_debug(distance, debug=debug)

        imlabel = skimage.morphology.watershed(-distance, markers=label(bimd), mask=bim)
        show_if_debug(imlabel, debug=debug)
    else:
        imlabel = label(bimr)


    # Segmented cells



    # Cell shape description


    # dfi = pd.DataFrame(regionprops_table(imlabel, intensity_image=img))
    dfi = pd.DataFrame(regionprops_table(
        imlabel, intensity_image=np.uint8(255 * img),
        properties=(
            "label",
            "area",
            "perimeter",
            "max_intensity",
            "mean_intensity",
            "min_intensity",
            "solidity",
            "minor_axis_length",
            "major_axis_length",
            "eccentricity",
            "bbox"

        ),
        # extra_properties=[q1_intensity]
    ))


    extra_properties=(quartiles,)
    extra_properties=[
        q1_intensity,
        q2_intensity,
        q3_intensity,
    ]
    for ep in extra_properties:
        values = []
        for i in range(np.max(imlabel)):
            values.append(ep(imlabel==i, 255*img))

        dfi[str(ep.__name__)] = values
    dfi["filename"] = fn.name
    dfsl.append(dfi)

    # remove big labels
    big_labels = list(dfi[dfi.area > max_size_px].label)
    logger.debug(big_labels)
    for lab in big_labels:
        imlabel[imlabel==lab] = 0

    imrgb = label2rgb(imlabel, image=img, bg_label=0)
    # show_if_debug(imrgb)
    report.imsave(fn.name + "_labeled.png", imrgb)

    # axs = plt.subplots(2,2)
    # axs[0].imshow(im)
    # axs[1].imshow()

if len(dfsl) > 0:
    df = pd.concat(dfsl)

#%%

df.reset_index()

df[["perimeter", "minor_axis_length", "major_axis_length"]] *= pxsz_um
df[["area"]] *= pxsz_um**2

#%%

df.filename.str.split("_")

#%%

df.filename.unique()

#%%
# Recalculate into SI units

df["cl"] = df.filename.str.extract('(\d+)').astype(int)
df["noncompactness"] = df.perimeter**2 / df.area
df["q1q2"] = df.q1_intensity / df.q2_intensity
df["mima"] = df.minor_axis_length / df.major_axis_length
df["im_id"] = df.filename.str.extract('_([abcd])')
df.im_id = df.im_id.map(dict(a=1, b=2, c=3, d=4))
df["schistocyt"] = df.noncompactness > 20.
df.im_id
df["cls"] = (df.cl>1) * 2 +  (df.schistocyt * 1)
df
df.to_csv("blood_cells.csv")

