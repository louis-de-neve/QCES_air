import requests
import numpy as np
import matplotlib.pyplot as plt
from dateutil import parser
import pandas as pd
import datetime, pytz
from datetime import timedelta
from matplotlib.animation import FuncAnimation
import scipy as sp

plt.rcParams["font.family"] = "DejaVu Serif"

def get_data_from_api(id, t1, t2):
    auth_token = "f2aec323-a779-4ee1-b63f-d147612982fb"
    auth_string = f"?token={auth_token}"
    source_url = "https://api.airgradient.com/public/api/v1/"
    locationId = id


    def constructed_url(endpoint, from_string="", to_string=""):
        return(source_url + endpoint + auth_string + from_string + to_string)


    start_string = f"&from={t1}"
    end_string = f"&to={t2}"
    endpoint = f"locations/{locationId}/measures/past"
    req_url = constructed_url(endpoint, start_string, end_string)
    response = requests.get(req_url).json()

    return response


def download_calibration_data(id):
    t1 = "20241022T153000Z"
    t2 = "20241027T235500Z"

    response = get_data_from_api(id, t1, t2)

    co2 = [d["rco2"] for d in response]
    times = [parser.parse(d["timestamp"]) - timedelta(hours=1) for d in response]

    return times, co2


def format_reference_data():
    t1_parsed = datetime.datetime(2024, 10, 22, 14, 30) # adjusted for timezone diff

    ref_data = pd.read_csv("reference.csv")
    ref_co2 = np.asarray(ref_data["co2_ppm"])
    ref_time = [parser.parse(val) for val in np.asarray(ref_data["date"])]

    ct = zip(ref_co2, ref_time)
    ct = [a for a in ct if a[1] >= t1_parsed]
    ref_co2, ref_time = zip(*ct)

    return ref_time, ref_co2


def adjust_for_jumps(times, concs):
    step0 = times[0]
    step1 = datetime.datetime(2024, 10, 27, 10, 10, tzinfo=pytz.UTC)
    steps = [step0, step1]
    step_indices = []
    for step in steps:
        step_indices.append(times.index(step))
    
    step_indices2 = step_indices.copy()
    step_indices2.append(len(times)-1)
    step_indices2.pop(0)
    step_locations = zip(step_indices, step_indices2)

    adjustment_offset = np.zeros_like(times)

    for step_start, step_stop in step_locations:
        for i, z in enumerate(adjustment_offset):
            R = step_stop-step_start-1
            if i > step_start+1 and i < step_stop:
                x = i - (step_start - 1)
                adjustment_offset[i] = - 20 * (R - x) / R
            elif i == step_start+1:
                adjustment_offset[i] = - 10
    
    new_concs = concs + adjustment_offset
    return list(new_concs), adjustment_offset


def fix_gap(ref_times, ref_concs):
    zipped = zip(ref_times, ref_concs)
    mis1 = datetime.datetime(2024, 10, 25, 23, 0)
    mis2 = datetime.datetime(2024, 10, 25, 23, 5)
    mis3 = datetime.datetime(2024, 10, 25, 23, 10)
    mis4 = datetime.datetime(2024, 10, 25, 23, 15)
    missing_steps = [mis1, mis2, mis3, mis4]
    new_zipped = []
    for t, c in zipped:
        if t in missing_steps:
            pass
        else:
            new_zipped.append((t, c))
    return zip(*new_zipped)


def plot_data(times, jumped_concs, ref_concs, concs0):

    fig, axs = plt.subplots(2, 1, figsize=(10, 6), sharex=True, height_ratios=[8, 5])

    axs[0].plot(times, ref_concs, color="black", label="Reference Data", linewidth=1)
    axs[1].plot(times, [0 for t in times], color="lightgrey", linewidth=1, linestyle="--")
    axs[1].plot(times, jumped_concs-ref_concs, color="black", label="Error", linewidth=1)

    axs[0].plot(times, jumped_concs, color="orangered", label="Calibrated Sensor Data", linewidth=1)
    

    

    axs[1].set_xlabel("November 2024")
    for ax in axs:
        ax.fill_between([times[800], times[1200]], -100, 2000, color="darkgrey", alpha=0.2, label="Calibration Period")

    axs[0].set_ylabel("CO₂ Concentration / ppm")
    axs[1].set_ylabel("Error / ppm")

    axs[0].legend(loc="upper left", frameon=False)

    axs[0].set_ylim(415, 560)
    axs[1].set_ylim(-20, 40)
    axs[0].set_yticks([550, 525, 500, 475, 450, 425])
    axs[1].set_yticks([40, 20, 0, -20])
    mean_error = (np.sum(jumped_concs-ref_concs)/len(jumped_concs))
    percent_error = (np.sum((jumped_concs-ref_concs)/ref_concs)/len(jumped_concs)*100)
    print(mean_error, percent_error)
    axs[1].text(times[20], 26, f"Mean Error: {mean_error:.2f} ppm\nMean % Error: {percent_error:.2f}%")
    axs[1].set_xlim(times[0], datetime.datetime(2024, 10, 27, 18, 00))
    axs[1].set_xticks([datetime.datetime(2024, 10, i, 0, 0) for i in range(23, 28)],
                      ["23ʳᵈ", "24ᵗʰ", "25ᵗʰ", "26ᵗʰ", "27ᵗʰ"])

    fig.tight_layout()

    plt.savefig("final_outputs/7.png", dpi=1200)
    plt.show()


def lin_regress_against_reference(times, concs, ref_concs, no_plot=False):
    t0 = times[0]
    interval = [(t - t0).total_seconds()/3600 for t in times] 
    
    print(len(concs))
    s1 = 800
    s2 = 1200

    coef = np.polyfit(list(concs[s1:s2]), list(ref_concs[s1:s2]), 1)

    concs2 = np.asarray(concs) * coef[0] + coef[1]

    if no_plot:
        return (times, concs2, coef)

    print(sp.stats.linregress(concs[s1:s2], ref_concs[s1:s2]))
    
    sc = plt.scatter(concs[s1:s2], ref_concs[s1:s2], c=interval[s1:s2])
    fig = plt.figure()
    def update(frame):
        sc.set_offsets(np.c_[concs[s1:s1+frame], ref_concs[s1:s1+frame]])
        return sc,
    ani = FuncAnimation(fig, update, frames=len(concs[s1:s2]) + 1, blit=True, repeat=False, interval=0.002)

    plt.legend()
    cbar = plt.colorbar()
    cbar.set_label("Time / hours")
    plt.xlabel('Sensor Data / ppm')
    plt.ylabel('Reference Data / ppm')
    ani.save("LDN_Air_sensor.gif")
    plt.show()
    
    plot_data(times, concs2, ref_concs)

    return times, concs2, ref_concs


def main(id="80176"):
    times, concs0 = download_calibration_data(id)
    ref_times, ref_concs = format_reference_data()

    ref_times, ref_concs = fix_gap(ref_times, ref_concs)
    
    concs, jump_offsets = adjust_for_jumps(times, concs0)
    
    times, concs, coef = lin_regress_against_reference(times, concs, ref_concs, no_plot=True)

    plot_data(times, concs, ref_concs, concs0)


if __name__ == "__main__":
    main()