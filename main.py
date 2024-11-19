import requests
import time
from calibration import calibrate, get_data_from_api
import matplotlib.pyplot as plt
from dateutil import parser
from datetime import timedelta
import numpy as np
from scipy.optimize import curve_fit

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

    return times, data_dict


def get_live_data(id, coefs):
     while True:
        raw_data = get_current_data_from_api(id)
        co2_val = raw_data["rco2"] 
        adjusted_current_co2 = apply_calibration(coefs, co2_val)
        print(f"Raw reading: {co2_val}ppm, Calibrated: {adjusted_current_co2}ppm")
        time.sleep(60)


def exponentials_plots(data_dict):
    # Fit the function a * np.exp(b * t) + c to x and y
    def function1(t, a, b, c):
        return a * np.exp(b * t) + c

    
    fig, axs = plt.subplots(nrows=3, sharex=True)
   
    for ax, label, pretty in zip(axs, ["rco2", "tvoc", "pm10"], ["CO2 (ppm)", "TVOC (ppm)", "PM10 (ppm)"]):
        popt, pcov = curve_fit(function1, data_dict["timedelta"], data_dict[label], p0=(1, -1e-5, 600))
        print(popt, pcov)
        ax.plot(data_dict["timedelta"], data_dict[label], label='Observed Data')
        ax.plot(data_dict["timedelta"], function1(np.asarray(data_dict["timedelta"]), *popt), label='Fit: y = %5.0f * exp(%5.4f * x) + %5.0f' % tuple(popt))
        ax.legend()
        ax.set_ylabel(pretty)
        ax.text(0.75, 0.75, rf"$\tau = {-1/popt[1]:.2f}$ hours", transform=ax.transAxes)

    plt.suptitle("Exponential Decay of CO2 and TVOC in Poorly Ventilated Residential Kitchen") 
    plt.legend()
    plt.xlabel("Time (Hours)")
    fig.tight_layout()
    plt.show()


def initialise():
    locationId = "80176"    
    coefs = calibrate(locationId)
    t1 = "20241117T012000Z"
    t2 = "20241119T103500Z"
    
    times, data_dict = get_calibrated_past_data(locationId, coefs, t1, t2)
    
    fig, axs = plt.subplots(nrows=3, sharex=True)
    axs[0].plot(times, data_dict["rco2"])
    axs[0].set_ylabel("Calibrated CO2 (ppm)")
    axs[1].plot(times, data_dict["tvoc"])
    axs[1].set_ylabel("tvoc (ppm)")
    axs[2].plot(times, data_dict["pm10"])
    axs[2].set_ylabel("pm10 (ppm)")
    fig.tight_layout()
    plt.show()
    

    
    
    
    
    #exponentials_plots(data_dict)
    #USE: # t1 = "20241117T012000Z"
    #t2 = "20241117T082500Z"

    #get_live_data(locationId, coefs)




if __name__ == "__main__":
    initialise()
