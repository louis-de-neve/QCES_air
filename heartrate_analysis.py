from heartrate.hr_extractor import get_hr

def hr_plot(locationId, coefs):
    hr_data = get_hr()
    t1 = hr_data["start_time"].min().strftime("%Y%m%dT%H%M%SZ")
    t2 = hr_data["end_time"].max().strftime("%Y%m%dT%H%M%SZ")
    
    times, data_dict = get_calibrated_past_data(locationId, coefs, t1, t2)
    
    #fig, ax = plt.subplots()
    #ax2 = ax.twinx()
    #ax.plot(times, data_dict["rco2"])
    #sns.lineplot(data=hr_data, x="start_time", y="MA", ax=ax2)
    #plt.show()

    data_copy = list(data_dict["rco2"].copy())

    hr_data = hr_data[hr_data["start_time"].dt.hour < 10]

    #print(len(hr_data))

    while len(data_copy) > len(hr_data["MA"]):
        data_copy.pop(0)

    #print(np.shape(data_copy), np.shape(hr_data["MA"]))
    plt.scatter(hr_data["MA"], data_copy, c=hr_data["start_time"])
    plt.ylabel("CO2 (ppm)")
    plt.xlabel("Heart Rate (bpm)")


    slope, intercept, r_value, p_value, std_err = linregress(hr_data["MA"], data_copy)

    plt.plot([40, 60], [40*slope + intercept, 60*slope + intercept], color="red")

    plt.text(50, 970, rf"$R^2$ = {r_value**2:.2f}")


    plt.show()