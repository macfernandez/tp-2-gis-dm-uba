import rasterio
import numpy as np
import pandas as pd
from rasterio.windows import Window

def metadata_from_tile(in_raster):
    with rasterio.open(in_raster) as src:
        w, h, t = src.width, src.height, src.transform
    return w, h, t

def sliding_windows(size, step_size, width, height, whole=False):
    """Slide a window of +size+ by moving it +step_size+ pixels"""
    w, h = size, size
    sw, sh = step_size, step_size
    end_i = height - h if whole else height
    end_j = width - w if whole else width
    for pos_i, i in enumerate(range(0, end_i, sh)):
        for pos_j, j in enumerate(range(0, end_j, sw)):
            real_w = w if whole else min(w, abs(width - j))
            real_h = h if whole else min(h, abs(height - i))
            yield Window(j, i, real_w, real_h), (pos_i, pos_j)
            
def create_windowed_dataset(tile, window):
    img_df = pd.DataFrame()
    src = rasterio.open(tile)
    img = src.read(window=window)
    r,m,n = img.shape
    img_df = (
        pd
        .DataFrame(img.reshape(r,m*n))
        .T
        .replace([np.inf, -np.inf], np.nan)
        .fillna(-99)
        .to_numpy()
    )
    return img_df
