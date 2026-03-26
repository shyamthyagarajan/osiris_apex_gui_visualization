import numpy as np
from astroquery.jplhorizons import Horizons

def fetch_horizons_data(satellite_id_list, start_time, stop_time, step_val):
  data_map = {}
  for satellite in satellite_id_list:
    position_time_obj = Horizons(id=satellite,location = '@sun', \
    epochs={'start':start_time, 'stop': stop_time, 'step': step_val})
    position_time_data = position_time_obj.vectors()

    data_map[satellite] = (np.array(position_time_data['datetime_jd']), \
        np.array(position_time_data['x']), np.array(position_time_data['y']), \
        np.array(position_time_data['z']))

  return data_map

if __name__ == "__main__":
    result = fetch_horizons_data(['99942','-64'], '2026-03-20', '2026-03-21', '1h')
    print(result)