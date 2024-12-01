import requests
import time
from calibration import calibrate, get_data_from_api
import matplotlib.pyplot as plt
from dateutil import parser
from datetime import timedelta
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import linregress
from datetime import datetime
import seaborn as sns
import pytz
import pandas as pd


class exponential_decay():
    def __init__(self, start:datetime, stop:datetime, window_open:bool, coefs, locationId:str=80176):
        self.start = start.astimezone(pytz.utc)
        self.stop = stop.astimezone(pytz.utc)
        self.window_open = window_open
        self.window_state = "open" if window_open else "closed"
        self.duration = self.start - self.stop
        
        self.start_str = start.strftime("%Y%m%dT%H%M%SZ")
        self.stop_str = stop.strftime("%Y%m%dT%H%M%SZ")

        self.data_datetimes, self.data_dict = get_calibrated_past_data(locationId, coefs, self.start_str, self.stop_str)
        self.data_timedeltas = [(d - self.start).seconds/3600 for d in self.data_datetimes]

        self.color="orangered"
        if window_open:
            self.color="dodgerblue"

        self.rescaled_data = {}
        self.coefs = {}

    def __len__(self):
        return len(self.data_timedeltas)
    
    def rescale(self, rescale_index:int, species:str, p0:list[float]=(500, -0.5, 400)):
        popt, pcov = curve_fit(exponential_func, self.data_timedeltas, self.data_dict[species], p0=p0)
        self.coefs[species] = popt
        self.tau = -1/popt[1]
        self.rescaled_data[species] = (self.data_dict[species] - popt[2]) / popt[0]

    def mean(self, species):
        return np.mean(self.data_dict[species])

    def get_individual_points(self, species):
        return list(zip(self.data_timedeltas, self.rescaled_data[species]))

# Fit the function a * np.exp(b * t) + c to x and y
def exponential_func(t, a, b, c):
    return a * np.exp(b * t) + c
def get_current_data_from_api(id:str):
    auth_token = "f2aec323-a779-4ee1-b63f-d147612982fb"
    auth_string = f"?token={auth_token}"
    source_url = "https://api.airgradient.com/public/api/v1/"
    locationId = id

    endpoint = f"locations/{locationId}/measures/current"
    req_url = source_url + endpoint + auth_string
    response = requests.get(req_url).json()

    print(response)
    return response
def apply_calibration(coefs, data):
    if type(data) == int:
        return int(data * coefs[0] + coefs[1])
    else:
        return [int((d * coefs[0] + coefs[1])) for d in data]
def get_calibrated_past_data(id:str, coefs, t1:str, t2:str):
    response = get_data_from_api(id, t1, t2)

    data_dict = {}
    for label in response[0].keys():
        data_dict[label] = np.asarray([d[label] for d in response])


    data_dict["rco2"] = data_dict["rco2"] * coefs[0] + coefs[1]
    times = [parser.parse(d["timestamp"]) for d in response]

    data_dict["timedelta"] = [(t-times[0]).seconds/3600 for t in times]

    data_dict["atmp"] = [t*1.327-6.738 if t < 10 else t*1.181 - 5.113 for t in data_dict["atmp"]]
    data_dict["rhum"] = data_dict["rhum"] * 1.259 + 7.34

    return times, data_dict
def get_live_data(id, coefs):
     while True:
        raw_data = get_current_data_from_api(id)
        co2_val = raw_data["rco2"] 
        adjusted_current_co2 = apply_calibration(coefs, co2_val)
        print(f"Raw reading: {co2_val}ppm, Calibrated: {adjusted_current_co2}ppm")
        time.sleep(60)
def exponentials_plots(locationId, coefs):
    t1 = "20241117T012000Z" # EXPONENT TIMES
    t2 = "20241117T082500Z"
    
    times, data_dict = get_calibrated_past_data(locationId, coefs, t1, t2) 
        
    fig, axs = plt.subplots(nrows=3, sharex=True)
   
    for ax, label, pretty in zip(axs, ["rco2", "tvoc", "pm10"], ["CO2 (ppm)", "TVOC (ppm)", "PM10 (ppm)"]):
        popt, pcov = curve_fit(exponential_func, data_dict["timedelta"], data_dict[label], p0=(1, -1e-5, 600))
        print(popt, pcov)
        ax.plot(data_dict["timedelta"], data_dict[label], label='Observed Data')
        ax.plot(data_dict["timedelta"], exponential_func(np.asarray(data_dict["timedelta"]), *popt), label='Fit: y = %5.0f * exp(%5.4f * x) + %5.0f' % tuple(popt))
        ax.legend()
        ax.set_ylabel(pretty)
        ax.text(0.75, 0.75, rf"$\tau = {-1/popt[1]:.2f}$ hours", transform=ax.transAxes)

    plt.suptitle("Exponential Decay of CO2 and TVOC in Poorly Ventilated Residential Kitchen") 
    plt.legend()
    plt.xlabel("Time (Hours)")
    fig.tight_layout()
    plt.show()
def simple_plot(times, data_dict):
    fig, axs = plt.subplots(nrows=3, sharex=True)
    axs[0].plot(times, data_dict["rco2"])
    axs[0].set_ylabel("Calibrated CO2 (ppm)")
    axs[1].plot(times, data_dict["atmp"])
    axs[1].set_ylabel("temp)")
    axs[2].plot(times, data_dict["pm10"])
    axs[2].set_ylabel("pm10 (ppm)")
    fig.tight_layout()
    plt.show()
def exponential_decay_plots(coefs, get_curves=False):
    
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

    if get_curves:
        return curves

    def individual_lines():
        fig, axs = plt.subplots(nrows=2, sharex=True)
        for ax, label, pretty in zip(axs, ["rco2", "tvoc"], [rf"$CO_2$", "TVOC"]):
            for curve in curves:
                curve.rescale(min_index, label)
                ax.plot(curve.data_timedeltas, curve.rescaled_data[label], color=curve.color, label=f"Window {curve.window_state}")
            ax.set_ylabel(pretty)
            handles, labels = ax.get_legend_handles_labels()
            ax.legend(handles=[handles[0], handles[-1]], labels=[labels[0], labels[-1]], loc='upper right', frameon=False)
        plt.xlim(-0.05, 5.2)
        plt.suptitle("Normalised Exponential Decay of CO2 and TVOC in a Residential Bedroom")
        axs[1].set_xlabel("Time since Source (Hours)")
        fig.tight_layout()
        plt.show()
    #individual_lines()

    def averaged_lines():
        fig, axs = plt.subplots(nrows=2, sharex=True)
        for ax, label, pretty in zip(axs, ["rco2", "tvoc"], [rf"$CO_2$", "TVOC"]):
            for curve_list in [false_curves, true_curves]:
                closed_points = []
                taus = []
                for curve in curve_list:
                    #p0 = (500, -0.5, 400) if pretty == "pm3" else (50, -0.5, 40)
                    curve.rescale(min_index, label)
                    taus.append(curve.tau)
                    closed_points += curve.get_individual_points(label)
                times, points = zip(*closed_points)
                #sns.lineplot(x=times, y=points, ax=ax, color=curve.color, label=rf"Window {curve.window_state}, $\tau = {np.mean(taus)*60:.1f} \pm {np.std(taus)*60:.1f} $ minutes")
                ts = np.linspace(0, 5.2, 100)
                ax.plot(ts,
                         np.exp(-ts/np.mean(taus)),
                        color=curve.color,
                        label=rf"Window {curve.window_state}, $\tau = {np.mean(taus)*60:.1f} \pm {np.std(taus)*60:.1f} $ minutes")
                ax.scatter(x=times,
                            y=points,
                            color=curve.color,
                            alpha=0.2,
                            linewidth=1,
                            marker="x")
                ax.fill_between(x=ts,
                                 y1=np.exp(-ts/(np.mean(taus) + np.std(taus))),
                                 y2=np.exp(-ts/(np.mean(taus) - np.std(taus))), 
                                 color=curve.color,
                                 alpha=0.2,
                                 linewidth=0)
            ax.set_ylabel(f"{pretty}")
            ax.legend(frameon=False)
        plt.xlim(-0.05, 5.2)
        axs[1].set_xlabel("Time since Source (Hours)")
        axs[0].set_title("CO2 and TVOC concentration above background\n relative to source concentration")
        fig.tight_layout()
        plt.show()
    averaged_lines()
def correlation_plot(data_dict):
    df = pd.DataFrame(data_dict)
    df2 = df[["pm01", "pm02", "pm10", "pm003Count", "rco2", "tvoc", "atmp", "rhum"]]

    sns.heatmap(df2.corr(numeric_only=True), cmap="coolwarm", annot=True, vmin=-1, vmax=1)
    plt.show()

    plt.scatter(df["rco2"], df["tvoc"])
    plt.show()

def overall_plot(locationId, coefs):   
    curves = exponential_decay_plots(coefs, get_curves=True)
    start_time = (min([curve.start for curve in curves]) - timedelta(hours=2)).strftime("%Y%m%dT%H%M%SZ")
    finish_time = (max([curve.stop for curve in curves]) + timedelta(hours=2)).strftime("%Y%m%dT%H%M%SZ")
    data_dict = {}
    mean_times = datetime.fromtimestamp(np.mean([curve.start.timestamp() for curve in curves]))
    times1, data_dict1 = get_calibrated_past_data(locationId, coefs, start_time, mean_times.strftime("%Y%m%dT%H%M%SZ"))
    times2, data_dict2 = get_calibrated_past_data(locationId, coefs, mean_times.strftime("%Y%m%dT%H%M%SZ"), finish_time)
    times = times1 + times2
    for data in data_dict1:
        data_dict[data] = np.asarray(list(data_dict1[data]) + list(data_dict2[data]))

    fig, axs = plt.subplots(nrows=2, sharex=True, figsize=(15, 6))
    axs[0].plot(times, data_dict["rco2"])
    axs[0].set_ylabel("Calibrated CO2 (ppm)")
    axs[1].plot(times, data_dict["tvoc"])
    axs[1].set_ylabel("tvoc (ppm)")

    for curve in curves:
        for ax in axs:
            ax.fill_between([curve.start, curve.stop], 0, 2000, color=curve.color, alpha=0.2, label=f"Window {curve.window_state}")
            
    axs[0].set_xlim(min(times), max(times))
    axs[0].set_ylim(450, 1300)
    axs[1].set_ylim(0, 1400)
    plt.xlabel("Date")
    handles, labels = ax.get_legend_handles_labels()
    axs[0].legend(handles=[handles[0], handles[-1]], labels=[labels[0], labels[-1]], loc='upper right', frameon=False)
    fig.tight_layout()
    plt.savefig("Outputs/overall_plot.png", dpi=600)
    plt.show()

def initialise():
    
    locationId = "80176"    
    coefs = calibrate(locationId)
    
    #t1 = "20241120T000000Z"
    #t2 = "20241130T093000Z"
    #times, data_dict = get_calibrated_past_data(locationId, coefs, t1, t2)    
    
    overall_plot(locationId, coefs)

    #correlation_plot(data_dict)

    #exponential_decay_plots(coefs)

    #simple_plot(times, data_dict)

    #exponentials_plots(locationId, coefs)
    
    #get_live_data(locationId, coefs)


if __name__ == "__main__":
    initialise()
