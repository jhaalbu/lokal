from metno_locationforecast import Place, Forecast
import datetime as dt

USER_AGENT = "stedspesifik skredvarsel værdemo"
kvitenova = Place("Kvitenova", 61.98, 7.33)
kvitenova_forecast = Forecast(kvitenova, USER_AGENT)
kvitenova_forecast.update()

# Create a datetime.date object for the day in question.
tomorrow = dt.date.today() + dt.timedelta(days=1)

# Get intervals for that date.
tomorrows_intervals = kvitenova_forecast.data.intervals_for(tomorrow)

# Iterate through each of the returned intervals and print it.
print("Forecast for tomorrow in Beijing:\n")
print(tomorrows_intervals)
# for interval in tomorrows_intervals:
#     print(interval)

class WeatherData:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def get_weather(self):
        place = Place("{}".format(self.lat), "{}".format(self.lon), 0)
        forecast = Forecast(place, "complete")
        return forecast.data

    def get_weather_for_time(self, time):
        place = Place("{}".format(self.lat), "{}".format(self.lon), 0)
        forecast = Forecast(place, "complete")
        return forecast.data.time(time)

    def get_weather_for_period(self, start, end):
        place = Place("{}".format(self.lat), "{}".format(self.lon), 0)
        forecast = Forecast(place, "complete")
        return forecast.data.intervals(start, end)

    def get_weather_for_period_with_interval(self, start, end, interval):
        place = Place("{}".format(self.lat), "{}".format(self.lon), 0)
        forecast = Forecast(place, "complete")
        return forecast.data.intervals(start, end, interval)

    def get_weather_for_period_with_interval_and_time(self, start, end, interval, time):
        place = Place("{}".format(self.lat), "{}".format(self.lon), 0)
        forecast = Forecast(place, "complete")
        return forecast.data.intervals(start, end, interval, time)

    def get_weather_for_period_with_interval_and_time_and_type(self, start, end, interval, time, type):
        place = Place("{}".format(self.lat), "{}".format(self.lon), 0)
        forecast = Forecast(place, "complete")
        return forecast.data.intervals(start, end, interval, time, type)

    def get_weather_for_period_with_interval_and_type(self, start, end, interval, type):
        place = Place("{}".format(self.lat), "{}".format(self.lon), 0)
        forecast = Forecast(place, "complete")
        return forecast.data.intervals(start, end, interval, type)

    def get_weather_for_period_with_time(self, start, end, time):
        place = Place("{}".format(self.lat), "{}".format(self.lon), 0)
        forecast = Forecast(place, "complete")
        return forecast.data.intervals(start, end, time)

    def get_weather_for_period_with_type(self, start, end, type):
        place = Place("{}".format(self.lat), "{}".format(self.lon), 0)