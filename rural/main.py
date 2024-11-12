import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

summer = pd.read_csv("rural/ref_city_rural_co2_hrly_summer_250724_290724.csv")
summer["timestamp"] = pd.to_datetime(summer["nsec_since_jan_1900"], unit="s", origin="1900-01-01")
summer['Hour'] = summer.timestamp.dt.hour

autumn = pd.read_csv("rural/ref_city_rural_co2_hrly_autumn_241024_281024.csv")
autumn["timestamp"] = pd.to_datetime(autumn["nsec_since_jan_1900"], unit="s", origin="1900-01-01")
autumn['Hour'] = autumn.timestamp.dt.hour

fig, axs = plt.subplots(2, 2, gridspec_kw={'width_ratios': [3, 1]})

sns.lineplot(data=summer, x="timestamp", y="rural_ref_co2_ppm", ax=axs[0][0], label="Rural")
sns.lineplot(data=summer, x="timestamp", y="city_ref_co2_ppm", ax=axs[0][0], label="City")

sns.lineplot(data=autumn, x="timestamp", y="rural_ref_co2_ppm", ax=axs[1][0])
sns.lineplot(data=autumn, x="timestamp", y="city_ref_co2_ppm", ax=axs[1][0])

sns.lineplot(data=summer, x="Hour", y="rural_ref_co2_ppm", ax=axs[0][1])
sns.lineplot(data=summer, x="Hour", y="city_ref_co2_ppm", ax=axs[0][1])

sns.lineplot(data=autumn, x="Hour", y="rural_ref_co2_ppm", ax=axs[1][1])
sns.lineplot(data=autumn, x="Hour", y="city_ref_co2_ppm", ax=axs[1][1])

axs[0][0].set_title("Summer")
axs[1][0].set_title("Autumn")

axs[0][0].set_ylabel("CO2 ppm")
axs[1][0].set_ylabel("CO2 ppm")

axs[0][1].set_ylabel("CO2 ppm")
axs[1][1].set_ylabel("CO2 ppm")

axs[0][0].set_xlabel("")
axs[1][0].set_xlabel("Time")

axs[0][1].set_xlim(0, 23)
axs[1][1].set_xlim(0, 23)

axs[0][0].set_xlim(summer["timestamp"].min(), summer["timestamp"].max())
axs[1][0].set_xlim(autumn["timestamp"].min(), autumn["timestamp"].max())

axs[0][0].legend()
plt.suptitle("CO2 ppm in rural and city reference locations")
plt.show()

