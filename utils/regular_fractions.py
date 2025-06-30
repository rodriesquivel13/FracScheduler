from datetime import datetime, timedelta
from . import calendar as cd
#============= Global Variables =====================
fractions_quantity = 8
weeks_expected_per_year = 365//7

# ======== Fractions-related functions ========

def maintenance_weeks_list(current_year, weekday_calendar_starts, maintenance_path):
    """
    Select week indices for maintenance based on a path and the year characteristics.
    """
    weeks_per_fraction = weeks_expected_per_year // fractions_quantity
    reserved_weeks = weeks_expected_per_year - fractions_quantity * weeks_per_fraction
    
    def maintenance_weeks_paths(current_year, weekday_calendar_starts,reserved_weeks):
        """
        This function crafts a dictionarie with no hollyweeks in tis keys (datetimes),
        and also it bounds the dictionarie particulary.
        """
        if cd.extra_week_indicator(current_year,weekday_calendar_starts):
            reserved_weeks +=1

        calendar = cd.main_day_weeker(current_year, weekday_calendar_starts)
        gold = cd.holly_weeks(current_year, weekday_calendar_starts)

        regular = {k:v for (k,v) in calendar.items() if v not in gold}
        list = [[i//7] for i in range(len(regular.values()))]
        regular = dict(zip(regular.keys(),list))
        bound = len(regular.keys()) // 7
        max_regular_len = bound // reserved_weeks * reserved_weeks

        dic = {k: v for k, v in regular.items() if v[0] < max_regular_len}

        return {k:[(v[0] + (current_year % fractions_quantity)) % (max_regular_len // reserved_weeks)] for (k,v) in dic.items()}


    maintenance_deserved_weeks = maintenance_weeks_paths(current_year, weekday_calendar_starts,reserved_weeks)
    lenght = len(maintenance_deserved_weeks.values()) // 7 // reserved_weeks
    matching_keys = [k for (k,v) in maintenance_deserved_weeks.items() if v[0] == maintenance_path % lenght]

    calendar = cd.main_day_weeker(current_year,weekday_calendar_starts)

    dirty_list = []
    for i in matching_keys:
        dirty_list.append(calendar[i])

    maintenance_weeks = []
    for r in dirty_list:
        if r not in maintenance_weeks:
            maintenance_weeks.append(r)
        
    return maintenance_weeks
    
def fractional_day_weeker(current_year, weekday_calendar_starts, maintenance_path):
    """
    This function lists weeks which are able to distribute their to fraction's owners.
    """
    semana_santa_index = cd.semana_santa_weeker(current_year,weekday_calendar_starts)
    easter_index = cd.easter_weeker(current_year,weekday_calendar_starts)
    maintenance_weeks = maintenance_weeks_list(current_year,weekday_calendar_starts, maintenance_path)
    
    special_weeks = []
    special_weeks.append(semana_santa_index)
    special_weeks.append(easter_index)

    day_week_indexes_dic = cd.main_day_weeker(current_year,weekday_calendar_starts)  
    week_indexes_after_maintenance = {k: v for k,v in day_week_indexes_dic.items() if v not in maintenance_weeks}
    unspecial_week_indexes = {k: v for k,v in week_indexes_after_maintenance.items() if v not in special_weeks}

    recerved_fractional_week_indexes = [12,16]
    total_fractional_weeks = weeks_expected_per_year - len(maintenance_weeks)

    reorder_list = [[a] for a in range(total_fractional_weeks + 1) if a not in recerved_fractional_week_indexes]
    expanded_reorder_list = [a for a in reorder_list for _ in range(7)]
    week_fractional_indexes =  dict(zip(unspecial_week_indexes.keys(),expanded_reorder_list))

    for date in day_week_indexes_dic.keys():
        if day_week_indexes_dic[date] == semana_santa_index:
            week_fractional_indexes[date] = [recerved_fractional_week_indexes[0]]
        elif day_week_indexes_dic[date] == easter_index:
            week_fractional_indexes[date] = [recerved_fractional_week_indexes[1]]
        else:
            pass
    
    return week_fractional_indexes

def fractional_index_maker(current_year, weekday_calendar_starts, maintenance_path):
    """
    This function indexes each date with fraction's index.
    """
    fractional_calendar_week_indexed = fractional_day_weeker(current_year,weekday_calendar_starts, maintenance_path)
    week_index_list = list(fractional_calendar_week_indexed.values())
    total_fractional_weeks_quantity = weeks_expected_per_year // fractions_quantity * fractions_quantity

    fraction_index_list = []
    for i in range(len(week_index_list)):
        week_index = week_index_list[i]
        fraction_index = [((week_index[0] - (current_year % fractions_quantity))  % total_fractional_weeks_quantity) % fractions_quantity]
        fraction_index_list.append(fraction_index)

    return dict(zip(fractional_calendar_week_indexed.keys(),fraction_index_list))

def fraction_hunter(wishful_year, wishful_month, wishful_day, weekday_calendar_starts, maintenance_path):
    """
    This function searches what fraction is needed for a specific wishful date.      
    """
    current_calendar = fractional_index_maker(wishful_year, weekday_calendar_starts, maintenance_path)
    next_calendar = fractional_index_maker(wishful_year + 1, weekday_calendar_starts, maintenance_path)

    fraction_spot = {**current_calendar, **next_calendar}

    wishful_date = datetime(wishful_year, wishful_month, wishful_day)

    try: 
        return fraction_spot[wishful_date]
    except KeyError:
        return f"So sorry, your wishful date '{wishful_date}' isn't available due our current schedule"

def unfractional_dates_list(current_year, weekday_calendar_starts, maintenance_path):
    """
    This funcion has as goal crafting a list with no fractional dates, such that,
    this list must have the rest of the dates of each year.
    """
    whole_calendar = cd.main_day_sequence(current_year, weekday_calendar_starts)
    fractional_calendar = fractional_index_maker(current_year, weekday_calendar_starts, maintenance_path)

    dates = list(whole_calendar.keys())
    fractional_dates = set(fractional_calendar.keys())  # We choose set instead of list for faster searching

    return [i for i in dates if i not in fractional_dates]