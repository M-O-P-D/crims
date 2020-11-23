
import warnings
warnings.filterwarnings(action='ignore', category=FutureWarning, module=r'.*pyproj' )

import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
import contextily as ctx

from . import geography
from .utils import standardise_force_name

force_boundaries = geography.create_forces_gdf()

all_msoas = geography.get_msoa11_gdf()


def density_map(crimes, force_name):
  # plot the results on a map
  crime_counts = crimes[["time"]].groupby(level=0).count().rename({"time": "colour"}, axis=1)

  start = min(crimes["time"])
  end = max(crimes["time"])

  # shading of MSOAs according to crime counts on a linear scale
  amax = crime_counts["colour"].max()
  # need to deal with rounding errors
  crime_counts["colour"] = crime_counts["colour"].apply(lambda r: to_rgba("r", alpha=min(1.0, 0.1+0.9*r/amax)))
  msoas = pd.merge(all_msoas[all_msoas.MSOA11CD.isin(crime_counts.index.values)][["MSOA11CD", "geometry"]], crime_counts, left_on="MSOA11CD", right_index=True)
  ax = msoas.plot(figsize=(10, 10), color=msoas.colour, edgecolor='k')

  # add force area boundary to map, and background tiles
  force_boundaries[force_boundaries.force == standardise_force_name(force_name)].plot(ax=ax, facecolor="none", edgecolor='b', linewidth=2)
  ax.set_axis_off()
  ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)
  plt.title("Simulated crime density for %s Police, %d/%d - %d/%d" % (force_name, start.year, start.month, end.year, end.month), fontsize=14)
  # now embedded in tiles
  #plt.title("Map tiles by Carto, under CC BY 3.0. Data by OpenStreetMap, under ODbL.", fontsize=12)

  return plt
