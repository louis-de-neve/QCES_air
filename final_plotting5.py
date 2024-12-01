from main import exponential_decay
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
from calibration import calibrate
import seaborn as sns
coefs = calibrate()

false_curves = []
false_curves.append(exponential_decay(datetime(2024, 11, 17, 1, 20), datetime(2024, 11, 17, 8, 20), False, coefs))

min_index = min([len(curve) for curve in false_curves]) - 1

plt.rcParams["font.family"] = "DejaVu Serif"

fig, axs = plt.subplots(ncols=1, sharex=True, figsize=(6, 6))
for axis_a, label, pretty, color in zip([axs, axs], ["rco2", "pm10"], [rf"CO₂", "PM₁₀"], ["orangered", "dodgerblue"]):
    for curve_list in [false_curves]:
        closed_points = []
        taus = []
        for curve in curve_list:
            curve.rescale(min_index, label)
            taus.append(curve.tau)
            closed_points += curve.get_individual_points(label)
        times, points = zip(*closed_points)
        #sns.lineplot(x=times, y=points, ax=axis_b,
        #             color=curve.color,
        #             linewidth=0)
        ts = np.linspace(0, 5.2, 100)
        correlation_coefficient = np.corrcoef(np.exp(-np.asarray(times)/np.mean(taus)), points)[0, 1]
        axis_a.plot(ts,
                    np.exp(-ts/np.mean(taus)),
                color="black",
                linewidth=1,)
        axis_a.scatter(x=times,
                    y=points,
                    color=color,
                    marker="x",
                    linewidth=1,
                    label=rf"{pretty}"+"\n"+f"τ = {np.mean(taus)*60:.0f} min"+"\n"+f"R² = {correlation_coefficient**2:.3f}")
        axis_a.fill_between(x=ts,
                            y1=np.exp(-ts/(np.mean(taus) + np.std(taus))),
                            y2=np.exp(-ts/(np.mean(taus) - np.std(taus))), 
                            color=curve.color,
                            alpha=0.2,
                            linewidth=0)
axs.set_ylabel(f"Relative Concentration")
axs.legend(frameon=False, labelspacing=1, loc="upper right", handletextpad=0)

plt.text(0.8, 0.2, "y = exp(-x/τ)", transform=axs.transAxes, fontname="DejaVu Serif")

plt.xlim(-0.05, 5.2)
plt.ylim(-0.05, 1.1)
plt.ylim(-0.05, 1.1)
plt.xlabel("Time / hours")
plt.xlabel("Time / hours")
fig.tight_layout()
plt.savefig("final_outputs/5.png", dpi=1200)
