from datetime import datetime, timedelta
from utils import main_day_sequence, fractional_index_maker

if __name__ == "__main__":

    def unfractional_dates_list(current_year, weekday_calendar_starts):
        whole_calendar = main_day_sequence(current_year,weekday_calendar_starts)
        fractional_calendar = fractional_index_maker(current_year, weekday_calendar_starts)
        
        dates = list(whole_calendar.keys())
        fractional_dates = list(fractional_calendar.keys())

        for i in dates:
            unfractional_dates = []
            if i in dates and i not in fractional_dates:
                unfractional_dates.append(i)
            else:
                pass
        return unfractional_dates