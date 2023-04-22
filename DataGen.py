import pandas as pd
import numpy as np
import datetime

workday = [50, 25, 10, 10, 20, 45, 100, 300, 500, 300, 125, 150,
           200, 210, 200, 210, 290, 550, 500, 350, 250, 200, 140, 100]
workday = [x/550 for x in workday]
offday = [100, 75, 68, 50, 5, 10, 15, 20, 50, 100, 190, 250,
          310, 400, 395, 390, 380, 375, 350, 300, 250, 200, 150, 115]
offday = [x/400 for x in offday]
months = [90, 113, 150, 178, 223, 240, 225, 223, 220, 212, 195, 175]
months = [x/240 for x in months]

holidays = [(1, 1), (1, 18), (2, 2), (2, 14), (2, 15), (3, 17), (4, 22), (5, 5), (5, 9), (5, 31), (6, 14), (6, 20),
            (7, 4), (9, 6), (10, 11), (10, 31), (11, 11), (11, 25), (11, 26), (11, 29), (12, 24), (12, 25), (12, 31)]


def lerp(alpha, zero, one):
    return (alpha * one) + ((1-alpha) * zero)


month_lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
month_temps = [(33.5, 6.5, 6), (38, 7, 5), (46.5, 8.5, 7), (53.5, 9.5, 7), (62, 10, 6),
               (72, 11, 3), (79, 11, 2), (78, 11,
                                          2), (68.5, 10.5, 3), (56.5, 9.5, 4),
               (43.5, 7.5, 5), (33, 6, 6)]
dirty_arr = []
year_day = -1
for month in range(12):
    m_w = month_temps[month]
    m_l = month_lengths[month]
    for day in range(m_l):
        year_day += 1

        isRainyday = np.random.randint(0, high=m_l) <= m_w[2]

        for time in range(24):
            dt = datetime.datetime(
                year=2022, month=month+1, day=day+1, hour=time)

            isHoliday = (dt.month, dt.day) in holidays
            isWorkday = not (dt.weekday() in [0, 6] or isHoliday)
            timeweight = workday[time] if isWorkday == 1 else (
                offday[time] * 0.9)

            for loc in range(20):

                loc_mean = np.random.randint(10, high=100)

                temp = np.random.normal(m_w[0], m_w[1])
                r = np.random.rand()
                rain = lerp(r, 0.75, 1.0) if isRainyday else lerp(r, 0, 0.75)

                r_weight = np.interp(rain, [0, 0.6, 1], [1, 0.9, 0])
                t_weight = np.interp(temp, [0, 30, 50, 85, 95, 104], [
                                     0, 0, 0.4, 1, 0.9, 0.8])
                w_weight = np.minimum(r_weight, t_weight)

                demand = int((loc_mean * 1.5) * timeweight * w_weight)

                dirty_arr.append([dt, isHoliday, temp, rain, loc_mean, demand])

dirty = pd.DataFrame(dirty_arr, columns=[
                     'datetime', 'holiday', 'apparent_temperature', 'weather_intensity', 'station_mean', 'demand'])

compression_opts = dict(method='zip', archive_name='dirty_data.csv')
dirty.to_csv('dirty_data.zip', index=False, compression=compression_opts)
