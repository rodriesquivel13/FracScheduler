from datetime import datetime, timedelta
from utils import main_day_sequence, fractional_index_maker

if __name__ == "__main__":

   def unfractional_dates_list(current_year, weekday_calendar_starts):
    whole_calendar = main_day_sequence(current_year, weekday_calendar_starts)
    fractional_calendar = fractional_index_maker(current_year, weekday_calendar_starts)

    dates = list(whole_calendar.keys())
    fractional_dates = set(fractional_calendar.keys())  # Convertir a set mejora la búsqueda

    # Filtrar fechas que no están en el fractional_calendar
    unfractional_dates = [i for i in dates if i not in fractional_dates]

    return unfractional_dates
   
   debug = unfractional_dates_list(2027,3)
   for i in debug:
      print(f'{i}')
