import requests, json
import numpy as np
import matplotlib.pyplot as plt
from dateutil import parser
import pandas as pd
import datetime
from datetime import timedelta


def get_data_from_api(t1, t2):
    auth_token = "f2aec323-a779-4ee1-b63f-d147612982fb"
    auth_string = f"?token={auth_token}"
    source_url = "https://api.airgradient.com/public/api/v1/"
    locationId = "80172"


    def constructed_url(endpoint, from_string="", to_string=""):
        return(source_url + endpoint + auth_string + from_string + to_string)


    start_string = f"&from={t1}"
    end_string = f"&to={t2}"
    endpoint = f"locations/{locationId}/measures/past"
    req_url = constructed_url(endpoint, start_string, end_string)
    response = requests.get(req_url).json()

    return response


t1 = "20241022T153000Z"
t1_parsed = parser.parse(t1)
t2 = "20241027T225500Z"
t2_parsed = parser.parse(t2)

response = get_data_from_api(t1, t2)


co2 = [d["rco2"] for d in response]
times = [parser.parse(d["timestamp"]) - timedelta(hours=1) for d in response]

ref_data = pd.read_csv("reference.csv")
ref_co2 = np.asarray(ref_data["co2_ppm"])
ref_time = [parser.parse(val) for val in np.asarray(ref_data["date"])]




plt.plot(times, co2, color="red", label="data")
plt.plot(ref_time, ref_co2, color="black", label="ref")
plt.legend()
plt.show()