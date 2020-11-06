
import pandas as pd

# inclusive range of months
def month_range(start_year, start_month, end_year, end_month):

  assert start_year <= end_year
  if start_year == end_year:
    assert start_month <= end_month

  d = []
  while True:
    d.append("%4d-%02d" % (start_year, start_month))
    start_month += 1
    if start_month == 13:
      start_year += 1
      start_month = 1
    if start_year > end_year or (start_year == end_year and start_month > end_month):
      break
  return d


def lad_lookup(lads, subgeog_name):
  lookup = pd.read_csv("./data/gb_geog_lookup.csv.gz", dtype={"OA":str, "LSOA":str, "MSOA":str, "LAD":str, "LAD_NAME":str,
     "LAD_NOMIS": int, "LAD_CM_NOMIS": int, "LAD_CM": str, "LAD_URBAN": str})
  lad_lookup = lookup[lookup.LAD.isin(lads)][[subgeog_name, "LAD"]].drop_duplicates().set_index(subgeog_name, drop=True)
  return lad_lookup


def msoa_from_lsoa(lsoas):
  lookup = pd.read_csv("./data/gb_geog_lookup.csv.gz", dtype={"OA":str, "LSOA":str, "MSOA":str, "LAD":str, "LAD_NAME":str,
     "LAD_NOMIS": int, "LAD_CM_NOMIS": int, "LAD_CM": str, "LAD_URBAN": str})
  msoa_lookup = lookup[lookup.LSOA.isin(lsoas)][["LSOA", "MSOA"]].drop_duplicates().set_index("LSOA", drop=True)
  return msoa_lookup