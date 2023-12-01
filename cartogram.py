import matplotlib.pyplot as plt
import matplotlib
import cartopy
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import shapely.geometry as sgeom  #for box drawing
import geopandas as gpd
import numpy as np
import mapclassify as mc
import pandas as pd

my_colormap = matplotlib.cm.Reds
edgecolor = "black"

newusa = gdf.copy()
col = "Opioid Dispensing Rate per 100"


# A function that draws inset map
def add_insetmap(axes_extent, map_extent, state_name, facecolor, edgecolor, geometry):
    # create new axes, set its projection
    use_projection = ccrs.Mercator()  # preserves shape
    geodetic = ccrs.Geodetic(globe=ccrs.Globe(datum="WGS84"))
    sub_ax = plt.axes(axes_extent, projection=use_projection)  # normal units
    sub_ax.set_extent(map_extent, geodetic)  # map extents

    # option to add basic land, coastlines of the map
    # can comment out if you don't need them
    sub_ax.add_feature(cartopy.feature.LAND)
    sub_ax.coastlines()
    sub_ax.set_title(state_name)

    # add map `geometry`
    sub_ax.add_geometries(
        [geometry], ccrs.Mercator(), facecolor=facecolor, edgecolor=edgecolor, lw=0.4,
    )

    # plot box around the map
    extent_box = sgeom.box(map_extent[0], map_extent[2], map_extent[1], map_extent[3])
    sub_ax.add_geometries([extent_box], ccrs.PlateCarree(), color="none")


# excluding non-conterminous states
usa_main = newusa[~newusa["State"].isin(["AK", "HI"])]
usa_main.crs = {"init": "epsg:4326"}
usa_main = usa_main.to_crs(epsg=2163)

# non-conterminous states, namely, Alaska and Hawaii
usa_more = newusa[newusa["State"].isin(["AK", "HI"])]  # include these
usa_more.crs = {"init": "epsg:4326"}
usa_more = usa_more.to_crs(epsg=2163)

# plot 1st part, using usa_main and grab its axis as 'ax2'
ax2 = usa_main.plot(
    column=col, legend=False, cmap=matplotlib.cm.Reds, ec=edgecolor, lw=0.4
)

# manipulate colorbar/legend
fig = ax2.get_figure()
cax = fig.add_axes([0.9, 0.25, 0.02, 0.5])  # [left,bottom,width,height]
sm = plt.cm.ScalarMappable(
    cmap=my_colormap, norm=plt.Normalize(vmin=min(newusa[col]), vmax=max(newusa[col]))
)

# # clear the array of the scalar mappable
sm._A = []
cb = fig.colorbar(sm, cax=cax)

cb.set_label("Opioid dispensing rate 2019")
ax2.set_frame_on(False)
ax2.set_xticks([])
ax2.set_yticks([])
ax2.set_xticklabels([])
ax2.set_yticklabels([])
ax2.set_title("Opioid dispensing rate 2019")

# plot Alaska, Hawaii as inset maps
for index, state in usa_more.dissolve(by='State').iterrows():
    st_name = index
    facecolor = my_colormap(state[col] / max(newusa[col]))
    if st_name == "AK":
        map_extent = (-180, -125, 46, 73)
        axes_extent = (0.04, 0.06, 0.29, 0.275)
    elif st_name == "HI":
        map_extent = (-162, -152, 15, 25)
        axes_extent = (0.27, 0.06, 0.15, 0.15)
    add_insetmap(
        axes_extent, map_extent, st_name, facecolor, edgecolor, state["geometry"]
    )
plt.show()