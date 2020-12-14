import numpy as np
import pandas as pd
import neworder as no
from datetime import datetime, date
from calendar import monthrange
from dateutil.relativedelta import relativedelta
from .crime import Crime
from .streamer import DataStream
from .utils import get_periodicity

class CrimeMicrosim(no.Model):
  def __init__(self, start_year, start_month, end_year, end_month, force_area):
    # timeline with monthly steps and annual checkpoints
    timeline = no.CalendarTimeline(date(start_year, start_month, 1), date(end_year, end_month, 1), 1, "m", 1)
    super().__init__(timeline, no.MonteCarlo.nondeterministic_stream)

    crime = Crime(force_area, 2017, 10, 2020, 9)
    self.crime_rates = crime.get_crime_counts()
    self.crime_outcomes = crime.get_crime_outcomes()

    self.crime_types = self.crime_rates.index.unique(level=1)
    self.geogs = self.crime_rates.index.unique(level=0)
    self.crime_categories = crime.get_category_breakdown()

    # upstream model
    self.datastream = DataStream("http://localhost:5000")

    self.crimes = pd.DataFrame()

  def step(self):

    self.crimes = self.__sample_crimes().sort_values(by="time")

    # # TODO *assumes* monthly but timeline might not be
    # start_date = self.timeline().time()
    # end_date = start_date + relativedelta(months=1)

    # # send monthly data to upstream model - if its listening
    # adjustments = self.datastream.send_recv(self.crimes[(self.crimes.time >= start_date) & (self.crimes.time < end_date)])

    # no.log("%s-%s: %d crimes. posted: %s" % (start_date, end_date, len(self.crimes[(self.crimes.time >= start_date) & (self.crimes.time < end_date)]), adjustments is not None))

    # if adjustments is not None:
    #   no.log("received %d adjustments" % len(adjustments))

  def __sample_crimes(self):
    # simulate crimes from a non-homogeneous Poisson process using a lambda derived
    # from geographical and historical/seasonal incidence for each crime type, with weekly and daily periodicities superimposed
    t = self.timeline().time()
    # NB Mo=0, Su=6
    start_weekday, days_in_month = monthrange(t.year, t.month)
    periods_in_day = 3 # night (0:00-8:00) day (8:00-4:00), evening (4:00-0:00)
    periods = days_in_month * periods_in_day
    # this is the time resolution of the lambdas in the nonhomogeneous Poisson process
    dt = self.timeline().dt() / periods
    secs_per_year = 365.2475 * 86400 # consistent with dt() implementation

    crimes = pd.DataFrame()

    for ct in self.crime_types:
      # cd = subcats.index.values
      # p = subcats.proportion.values
      # s = self.mc().sample(100, p)
      # print([d[i] for i in s])
      # extra [] to sure result is always a dataframe (even if 1 row)
      # see https://stackoverflow.com/questions/20383647/pandas-selecting-by-label-sometimes-return-series-sometimes-returns-dataframe
      subcats = self.crime_categories.loc[[ct]]

      # print(subcats.proportion)
      # continue
      time_weights = get_periodicity(start_weekday, days_in_month, ct)

      for g in self.geogs:
        if self.crime_rates.index.isin([(g, ct)]).any():
          # impose daily/weekly periodicity to the monthly frequency
          lambdas = self.crime_rates.loc[(g, ct), ("count", "%02d" % t.month)] * time_weights
          # append extra zero element at end so don't sample into next timestep
          lambdas = np.append(lambdas, 0.0)
          times = self.mc().arrivals(lambdas, dt, 1, 0.0)[0]
          #no.log(times)
          p_suspect = self.crime_outcomes.loc[(g,ct), "pSuspect"]
          #print(p_suspect)
          if len(times) > 0:
            d = [t + relativedelta(seconds=time*secs_per_year) for time in times]
            s = self.mc().hazard(p_suspect, len(times)).astype(bool)
            c = self.mc().sample(len(times), subcats.proportion.values)
            df = pd.DataFrame(index=range(len(d)), data={"MSOA": g,
                                                         "crime_type": ct,
                                                         "code": subcats.iloc[c]["code_original"].values,
                                                         "description": subcats.iloc[c]["description"].values,
                                                         "time": d,
                                                         "suspect": s,
                                                         "severity": subcats.iloc[c]["ONS_SEVERITY_weight"].values })
            crimes = crimes.append(df, ignore_index=True)

    # round to nearest minute
    crimes["time"] = crimes["time"].round("min")
    return crimes.set_index(["MSOA", "crime_type"], drop=True)


  def checkpoint(self):
    no.log("Simualated %d crimes between %s and %s" % (len(self.crimes), self.timeline().start(), self.timeline().end()))
    #no.log("Annual average = %f" % self.crime_rates.sum().mean())
    #no.log(self.crimes)




