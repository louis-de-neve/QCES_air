from main import exponential_decay_plots, get_calibrated_past_data
from calibration import calibrate

import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
from datetime import datetime, timedelta

plt.rcParams["font.family"] = "DejaVu Serif"

locationId="80176"
coefs = calibrate(locationId)

curves = exponential_decay_plots(coefs, get_curves=True)
start_time = (min([curve.start for curve in curves]) - timedelta(hours=2)).strftime("%Y%m%dT%H%M%SZ")
finish_time = (max([curve.stop for curve in curves]) + timedelta(hours=2)).strftime("%Y%m%dT%H%M%SZ")

mean_times = datetime.fromtimestamp(np.mean([curve.start.timestamp() for curve in curves]))

data_dict = {}
times1, data_dict1 = get_calibrated_past_data(locationId, coefs, start_time, mean_times.strftime("%Y%m%dT%H%M%SZ"))
times2, data_dict2 = get_calibrated_past_data(locationId, coefs, mean_times.strftime("%Y%m%dT%H%M%SZ"), finish_time)
times = times1 + times2
for data in data_dict1:
    data_dict[data] = np.asarray(list(data_dict1[data]) + list(data_dict2[data]))


fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(10, 6), width_ratios=[8, 3])
axs = axs.flatten()


axs[0].plot(times, data_dict["rco2"], color="black", linewidth=1)
axs[1].plot(times, data_dict["rco2"], color="black", linewidth=1)
axs[2].plot(times, data_dict["tvoc"], color="black", linewidth=1)
axs[3].plot(times, data_dict["tvoc"], color="black", linewidth=1)
axs[0].set_ylabel("CO₂ Concentration / ppm")
axs[2].set_ylabel("TVOC Concentration / ppm")

axs[0].spines['right'].set_visible(False)
axs[1].spines['left'].set_visible(False)
axs[2].spines['right'].set_visible(False)
axs[3].spines['left'].set_visible(False)


for curve in curves:
    for ax in axs:
        ax.fill_between([curve.start, curve.stop], 0, 2000,
                        color=curve.color,
                        alpha=0.17,
                        label=f"Window {curve.window_state}",
                        linewidth=0)
        
xticks = [datetime(2024, 11, i, 0, 0) for i in range(20, 31)]
xlabels = ["20ᵗʰ", "21ˢᵗ", "22ⁿᵈ", "23ʳᵈ", "24ᵗʰ", "25ᵗʰ", "26ᵗʰ", "27ᵗʰ", "28ᵗʰ", "29ᵗʰ", "30ᵗʰ"]
for ax in axs:
    ax.set_xticks(xticks, xlabels)
axs[0].set_xticks(xticks, np.full_like(xticks, ""))
axs[1].set_xticks(xticks, np.full_like(xticks, ""))

axs[0].set_ylim(350, 1300)
axs[1].set_ylim(350, 1300)
axs[2].set_ylim(0, 1400)
axs[3].set_ylim(0, 1400)

axs[0].set_xlim(min(times), datetime(2024, 11, 24, 20, 15))
axs[1].set_xlim(datetime(2024, 11, 28, 1, 0), max(times))
axs[2].set_xlim(min(times), datetime(2024, 11, 24, 20, 15))
axs[3].set_xlim(datetime(2024, 11, 28, 1, 0), max(times))

axs[0].yaxis.tick_left()
axs[2].yaxis.tick_left()
axs[1].set_yticks([])
axs[3].set_yticks([])



fig.text(0.5, 0.01, "November 2024", ha='center')

handles, labels = ax.get_legend_handles_labels()
axs[1].legend(handles=[handles[0], handles[-1]], labels=[labels[0], labels[-1]],
              loc='upper right',
              frameon=False,
              bbox_to_anchor=(0.5, 1))
fig.tight_layout()
fig.subplots_adjust(wspace=0.05)
fig.subplots_adjust(hspace=0.075)

d = 1  # proportion of vertical to horizontal extent of the slanted line
kwargs = dict(marker=[(-1, -d), (1, d)], markersize=12,
              linestyle="none", color='k', mec='k', mew=1, clip_on=False)
axs[0].plot([1, 1], [1, 0], transform=axs[0].transAxes, **kwargs)
axs[1].plot([0, 0], [1, 0], transform=axs[1].transAxes, **kwargs)
axs[2].plot([1, 1], [1, 0], transform=axs[2].transAxes, **kwargs)
axs[3].plot([0, 0], [1, 0], transform=axs[3].transAxes, **kwargs)




plt.savefig("final_outputs/3.png", dpi=1200)
