import requests
import time
from calibration import calibrate, get_data_from_api
import matplotlib.pyplot as plt
from dateutil import parser
from datetime import timedelta
import numpy as np

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


def get_past_data(id:str, coefs, t1:str, t2:str):
    response = get_data_from_api(id, t1, t2)
    pm2 = np.asarray([d["pm02"] for d in response])
    co2 = np.asarray([d["rco2"] for d in response])
    times = [parser.parse(d["timestamp"]) - timedelta(hours=1) for d in response]



    return times, co2*coefs[0]+coefs[1], pm2


def get_live_data(id, coefs):
     while True:
        raw_data = get_current_data_from_api(id)
        co2_val = raw_data["rco2"] 
        adjusted_current_co2 = apply_calibration(coefs, co2_val)
        print(f"Raw reading: {co2_val}ppm, Calibrated: {adjusted_current_co2}ppm")
        time.sleep(60)


def initialise():
    locationId = "80176"    
    coefs = calibrate(locationId)
    t1 = "20241105T080000Z"
    t2 = "20241106T235500Z"
    
    times, concs, pm2 = get_past_data(locationId, coefs, t1, t2)
    
    plt.plot(times, concs)
    plt.show()

    plt.plot(times, pm2)
    plt.show()

    get_live_data(locationId, coefs)

    

   



if __name__ == "__main__":
    initialise()
