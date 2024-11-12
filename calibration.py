import requests
import numpy as np
import matplotlib.pyplot as plt
from dateutil import parser
import pandas as pd
import datetime, pytz
from datetime import timedelta
from matplotlib.animation import FuncAnimation
import scipy as sp


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


def plot_data(times, jumped_concs, ref_concs):

    plt.plot(times, jumped_concs, color="red", label="Sensor Data")
    plt.plot(times, ref_concs, color="black", label="Reference")
    
    plt.xlabel("Date")
    plt.ylabel("Concentration / ppm")
    plt.legend()
    plt.show()


def lin_regress_against_reference(times, concs, ref_concs, no_plot=False):
    fig = plt.figure()
    t0 = times[0]
    interval = [(t - t0).total_seconds()/3600 for t in times] 
    s1 = 0
    s2 = -1

    coef = np.polyfit(list(concs[s1:s2]), list(ref_concs[s1:s2]), 1)

    concs2 = np.asarray(concs) * coef[0] + coef[1]

    if no_plot:
        return (times, concs2, coef)

    print(sp.stats.linregress(concs[s1:s2], ref_concs[s1:s2]))
    
    sc = plt.scatter(concs[s1:s2], ref_concs[s1:s2], c=interval[s1:s2])

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


def calibrate(id="80176"):
    times, concs = download_calibration_data(id)
    ref_times, ref_concs = format_reference_data()

    ref_times, ref_concs = fix_gap(ref_times, ref_concs)
    
    concs, jump_offsets = adjust_for_jumps(times, concs)
    times, concs, coef = lin_regress_against_reference(times, concs, ref_concs, no_plot=True)

    return(coef)


def main(id="80176"):
    times, concs = download_calibration_data(id)
    ref_times, ref_concs = format_reference_data()

    ref_times, ref_concs = fix_gap(ref_times, ref_concs)
    
    concs, jump_offsets = adjust_for_jumps(times, concs)
    

    times, concs, coef = lin_regress_against_reference(times, concs, ref_concs, no_plot=True)

    plot_data(times, concs, ref_concs)


if __name__ == "__main__":
    main()