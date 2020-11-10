# %%
import neworder as no
from crims import model
from crims import geography

#import contextily as ctx
import matplotlib.pyplot as plt

#no.verbose()

timeline = no.Timeline(2020,2020,[1])
model = model.CrimeMicrosim(timeline, "west-yorkshire")

# df = model.crime_rates.set_index(["MSOA", "Crime type", "Month"], drop=True)
# print(df)

#no.log(model.crime_rates.loc[("E02001109", "Anti-social behaviour")])

# %%

#print(df.loc[("E02001103", "Anti-social behaviour")])

no.run(model)

force_boundaries = geography.create_forces_gdf()

ax = force_boundaries[force_boundaries.force == "west-yorkshire"].plot(figsize=(10, 10), alpha=0.3, edgecolor='k')


msoas = geography.get_msoa11_gdf()

msoas = msoas[msoas.MSOA11CD.isin(model.crimes.index.levels[0].unique())][["MSOA11CD", "geometry"]]

print(msoas.head())

msoas.plot(ax=ax, alpha=0.3, color='r', edgecolor='k')


plt.show()




# %%
# import importlib
# importlib.reload(model)


# %%
