from main import exponential_decay
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
from calibration import calibrate
import seaborn as sns
coefs = calibrate()

false_curves = []
false_curves.append(exponential_decay(datetime(2024, 11, 19, 5, 45), datetime(2024, 11, 19, 10, 55), False, coefs))
false_curves.append(exponential_decay(datetime(2024, 11, 20, 5, 45), datetime(2024, 11, 20, 9, 30), False, coefs))
false_curves.append(exponential_decay(datetime(2024, 11, 20, 16, 00), datetime(2024, 11, 20, 19, 15), False, coefs))
false_curves.append(exponential_decay(datetime(2024, 11, 21, 14, 00), datetime(2024, 11, 21, 17, 35), False, coefs))
false_curves.append(exponential_decay(datetime(2024, 11, 22, 13, 55), datetime(2024, 11, 22, 18, 40), False, coefs))
false_curves.append(exponential_decay(datetime(2024, 11, 23, 18, 5), datetime(2024, 11, 23, 20, 00), False, coefs))
false_curves.append(exponential_decay(datetime(2024, 11, 29, 5, 35), datetime(2024, 11, 29, 9, 20), False, coefs))
false_curves.append(exponential_decay(datetime(2024, 11, 30, 6, 30), datetime(2024, 11, 30, 11, 00), False, coefs))
true_curves = []
true_curves.append(exponential_decay(datetime(2024, 11, 22, 5, 40), datetime(2024, 11, 22, 9, 25), True, coefs))
true_curves.append(exponential_decay(datetime(2024, 11, 23, 6, 20), datetime(2024, 11, 23, 11, 30), True, coefs))
true_curves.append(exponential_decay(datetime(2024, 11, 24, 8, 25), datetime(2024, 11, 24, 12, 00), True, coefs))
true_curves.append(exponential_decay(datetime(2024, 11, 28, 12, 25), datetime(2024, 11, 28, 15, 40), True, coefs))  
curves = false_curves + true_curves
min_index = min([len(curve) for curve in curves]) - 1

plt.rcParams["font.family"] = "DejaVu Serif"

fig, axs = plt.subplots(nrows=2, ncols=2, sharex=True, figsize=(10, 6))
axs = axs.flatten()
for axis_b, axis_a, label, pretty in zip([axs[1], axs[3]],[axs[0], axs[2]], ["rco2", "tvoc"], [rf"CO₂ Concentration", "TVOC Concentration"]):
    for curve_list in [false_curves, true_curves]:
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
        axis_b.plot(ts,
                    np.exp(-ts/np.mean(taus)),
                color=curve.color,
                linewidth=1,
                label=rf"Window {curve.window_state}"+"\n"+f"τ = {np.mean(taus)*60:.0f} ± {np.std(taus)*60:.0f} min"+"\n"+f"R² = {correlation_coefficient**2:.3f}")
        axis_a.scatter(x=times,
                    y=points,
                    color=curve.color,
                    linewidth=1,
                    marker="x")
        axis_b.fill_between(x=ts,
                            y1=np.exp(-ts/(np.mean(taus) + np.std(taus))),
                            y2=np.exp(-ts/(np.mean(taus) - np.std(taus))), 
                            color=curve.color,
                            alpha=0.2,
                            linewidth=0)
    axis_a.set_ylabel(f"{pretty}")
    axis_b.legend(frameon=False, labelspacing=1.5, loc="upper right")

tick_locs = axs[0].get_yticks()
axs[1].set_yticks(tick_locs, [" " for _ in tick_locs])
tick_locs = axs[2].get_yticks()
axs[3].set_yticks(tick_locs, [" " for _ in tick_locs])

axs[1].text(0.04, 0.92, "y = exp(-x/τ)", transform=axs[1].transAxes, fontname="DejaVu Serif")

plt.xlim(-0.05, 5.2)
axs[0].set_ylim(-0.05, 1.1)
axs[1].set_ylim(-0.05, 1.1)
axs[2].set_ylim(-0.15, 1.2)
axs[3].set_ylim(-0.15, 1.2)
axs[2].set_xlabel("Time / hours")
axs[3].set_xlabel("Time / hours")
fig.tight_layout()

plt.savefig("final_outputs/4.png", dpi=1200)
