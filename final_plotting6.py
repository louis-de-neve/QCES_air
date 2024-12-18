from datetime import datetime
from calibration import calibrate
from main import exponential_decay, get_calibrated_past_data
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.family"] = "DejaVu Serif"

coefs = calibrate()
locationId = "80176"
tau = 72 * 60 # seconds
molecular_weight = 44.01 # g/mol
density = 1.98 # g/L
room_volume = (3*4.7+1.5*2)*2.5 # m3

fig, ax = plt.subplots(figsize=(6, 6))

nights = []
for i in list(range(20, 25))+list(range(28, 31)):
    night = exponential_decay(datetime(2024, 11, i, 2, 0), datetime(2024, 11, i, 5, 00), False, coefs)
    ax.scatter(night.data_timedeltas, night.data_dict["rco2"],
                label="1",
                marker="x",
                color=night.color,
                linewidth=1)
    nights.append(night)

mean_co2s = [night.mean("rco2") for night in nights]
mean_nightly_co2 = np.mean(mean_co2s) # ppm
stdev_nightly_co2 = np.std(mean_co2s) # ppm
print(stdev_nightly_co2, "ppm")

plt.plot(night.data_timedeltas, np.full_like(night.data_timedeltas, mean_nightly_co2),
         color="black", linestyle="--", linewidth=1)

bkgr = exponential_decay(datetime(2024, 11, 26, 2, 0), datetime(2024, 11, 26, 5, 0), True, coefs)
ax.scatter(bkgr.data_timedeltas, bkgr.data_dict["rco2"],
            label="2",
            color=bkgr.color,
            marker="x",
            linewidth=1)
mean_background_co2 = bkgr.mean("rco2") # ppm

plt.plot(night.data_timedeltas, np.full_like(night.data_timedeltas, mean_background_co2),
         color="black", linestyle="--", linewidth=1)

c_prime = mean_nightly_co2 - mean_background_co2 # ppm
ppm_flux = c_prime / tau # ppm/s
print(ppm_flux, "ppm/s")
mg_flux = 0.0409 * ppm_flux * molecular_weight # mg s-1 m-3
gh_flux = mg_flux * 3.6 # g hr-1 m-3
print(gh_flux)
lh_flux = gh_flux / density # L hr-1 m-3

flux = lh_flux * room_volume # L hr-1
print(flux)
handles, labels = ax.get_legend_handles_labels()

plt.legend(handles[-2:], [f"Interior (8 nights)"+"\n"+f"Mean: {mean_nightly_co2:.0f} ppm",
                          f"Exterior (26th Nov)"+"\n"+f"Mean: {mean_background_co2:.0f} ppm"],
           frameon=False,
           loc="upper right",
           bbox_to_anchor=(1, 0.5),)
plt.ylim(350, 1050)
plt.xlim(-0.05, 3.05)
plt.xlabel("Time / hours")
plt.ylabel("CO₂ Concentration / ppm")
fig.tight_layout()
plt.savefig("final_outputs/6.png", dpi=1200)





    