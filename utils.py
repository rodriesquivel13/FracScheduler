from datetime import datetime, timedelta

# ======== Easter calculations ========
def gauss_easter(year):
    """
    Gauss' model for calculating the date of easter's beginning
    """
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4 
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    easter_month = (h + l - 7 * m + 114) // 31
    easter_day = ((h + l - 7 * m + 114) % 31) + 1
    return datetime(year,easter_month,easter_day)

def lunes_santo(year): 
    """
    Function for calculating lunes santo (Samana Santa's Monday)
    """
    return gauss_easter(year) - timedelta(days = 6)

# ======== Date-related functions ========
def first_day_first_week(year, weekday_calendar_starts): 
    """
    We'll use a calendar that lists its weeks.
    Every week in this calendar begins in monday, tuesday, wednesday,... (or 0,1,2,... according python index)
    January first belongs to the first week of each year.
    This function caculates the date of the first day of the first week of each year and calendar, depending on which weekday it starts on.  
    """
    january_first = datetime(year,1,1)
    shift = (january_first.weekday() - weekday_calendar_starts) % 7
    return january_first - timedelta(days = shift)

def main_day_sequence(year, weekday_calendar_starts):
    """
    This function crafts a dictionarie:
    -Keys are dates.
    -Values are lists, which each one has an unique natural number starting from 0.
    """
    dic = {}
    day = first_day_first_week(year, weekday_calendar_starts)
    edge_day = first_day_first_week(year + 1, weekday_calendar_starts)
    
    for i in range(0,(edge_day - day).days):
        dic[day] = [i]
        day += timedelta(days = 1)
    return dic

def main_day_weeker(year,weekday_calendar_starts):
    """
    This function takes a day index (or value) from main_day_sequence and become it in week index starting from 0.
    """
    dic = main_day_sequence(year,weekday_calendar_starts)
    for day_index in dic.values():
        week_index = (day_index[0] // 7)
        day_index[0] = week_index
    return dic

def new_weekday(year,weekday_calendar_starts):
    """
    This funtion re-define weekday number, depending on which day calendar starts on.
    """
    dic = main_day_sequence(year,weekday_calendar_starts)
    for day_index in dic.values():
        week_index = (day_index[0] % 7)
        day_index[0] = week_index
    return dic

"""
The really interesting thing here is, what does it happens with 365 % 7?,
could those days acumulate itself into an "extra week"?.
we're gonna work on this doubts later soon.
"""
weeks_expected_per_year = 365//7

def extra_week_indicator(year,weekday_calendar_starts):
    """
    We expect years have 52 weeks but actually, by how we defined the first day of each year,
    some years have a 53rd week.
    This function tell us whether a year have that extra week.
    """
    dic = main_day_weeker(year, weekday_calendar_starts)
    week_list=  []
    for week_index in dic.values():
        if week_index[0] not in week_list:
            week_list.append(week_index[0])
        pass
    count_weeks = len(week_list)
    if count_weeks > weeks_expected_per_year:
        return True
    return False

def semana_santa_weeker(year, weekday_calendar_starts):
    """
    This functions return us the week index of semana semana each year, depending on which weekday it starts on.
    """
    monday = lunes_santo(year)
    week_beginnig = monday + timedelta(days = weekday_calendar_starts)
    calendar = main_day_weeker(year,weekday_calendar_starts)
    return calendar[week_beginnig]

def semana_diabla_weeker(year, weekday_calendar_starts):
    """
    This functions return us the week index of semana diabla (the week inmediatly after semana santa) each year,
    depending on which weekday it starts on.
    """
    monday = gauss_easter(year) + timedelta(days = 1)
    week_beginnig = monday + timedelta(days = weekday_calendar_starts)
    calendar = main_day_weeker(year,weekday_calendar_starts)
    return calendar[week_beginnig]

# ======== Fractions-related functions ========

fractions_quantity = 8

def maintenance_weeks_maker(current_year, weekday_calendar_starts):
    """
    This function preselects some week's indexes for maintenace and update them according of some year's features.
    """
    maintenance_weeks = [[8],[21],[34],[47]]
    if extra_week_indicator(current_year,weekday_calendar_starts):
        maintenance_weeks.append([27])
    else:
        pass

    def mexican_revolution_day(current_year):
        """
        Since 2006 mexican government decreed day of the revolution will celebrated on third monday of november in each year.
        So, this function calculates when is that particular monday.
        """
        count = 0
        for day in range(1, 31):  # november has 30 days
            fecha = datetime(current_year, 11, day)
            if fecha.weekday() == 0:  # monday is equal to 0
                count += 1
                if count == 3:
                    return fecha

    november_third_monday = mexican_revolution_day(current_year)
    day_week_indexes_dic = main_day_weeker(current_year,weekday_calendar_starts) 
    

    if day_week_indexes_dic[november_third_monday] == [47]:
        maintenance_weeks[3] = [48]
    else:
        pass
    return maintenance_weeks

def fractional_day_weeker(current_year, weekday_calendar_starts):
    """
    This function lists weeks which are able to distribute their to fraction's owners.
    """
    semana_santa_index = semana_santa_weeker(current_year,weekday_calendar_starts)
    semana_diabla_index = semana_diabla_weeker(current_year,weekday_calendar_starts)
    maintenance_weeks = maintenance_weeks_maker(current_year,weekday_calendar_starts)
    
    special_weeks = []
    special_weeks.append(semana_santa_index)
    special_weeks.append(semana_diabla_index)

    day_week_indexes_dic = main_day_weeker(current_year,weekday_calendar_starts)  
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
        elif day_week_indexes_dic[date] == semana_diabla_index:
            week_fractional_indexes[date] = [recerved_fractional_week_indexes[1]]
        else:
            pass
    
    return week_fractional_indexes

def fractional_day_sequence(current_year, weekday_calendar_starts):
    """
    This function lists days which are able to distribute them to fraction's owners.
    """
    fractional_calendar_week_indexed = fractional_day_weeker(current_year,weekday_calendar_starts)
    week_index_list = list(fractional_calendar_week_indexed.values())

    day_index_list = []
    for i in range(len(week_index_list)):
        week_index = week_index_list[i]
        day_index = [week_index[0] * 7 + i % 7]
        day_index_list.append(day_index)

    return dict(zip(fractional_calendar_week_indexed.keys(),day_index_list))

initial_year = 2027

def fractional_index_maker(current_year, weekday_calendar_starts):
    """
    This function indexes each date with fraction's index.
    """
    fractional_calendar_week_indexed = fractional_day_weeker(current_year,weekday_calendar_starts)
    week_index_list = list(fractional_calendar_week_indexed.values())
    total_fractional_weeks_quantity = weeks_expected_per_year // fractions_quantity * fractions_quantity

    fraction_index_list = []
    for i in range(len(week_index_list)):
        week_index = week_index_list[i]
        fraction_index = [((week_index[0] - current_year + initial_year)  % total_fractional_weeks_quantity) % fractions_quantity]
        fraction_index_list.append(fraction_index)

    return dict(zip(fractional_calendar_week_indexed.keys(),fraction_index_list))


def fraction_hunter(wishful_year, wishful_month, wishful_day, weekday_calendar_starts):
    """
    This function searches what fraction is needed for a specific wishful date.      
    """
    calendar_1 = fractional_index_maker(wishful_year, weekday_calendar_starts)
    calendar_2 = fractional_index_maker(wishful_year + 1, weekday_calendar_starts)

    fraction_spot = {**calendar_1, **calendar_2}

    wishful_date = datetime(wishful_year, wishful_month, wishful_day)

    try: 
        return fraction_spot[wishful_date]
    except KeyError:
        return f"So sorry, your wishful date '{wishful_date}' isn't available due our current schedule "



def unfractional_dates_list(current_year, weekday_calendar_starts):
    """
    This funcion has as goal crafting a list with no fractional dates, such that,
    this list must have the rest of the dates of each year.
    """
    whole_calendar = main_day_sequence(current_year, weekday_calendar_starts)
    fractional_calendar = fractional_index_maker(current_year, weekday_calendar_starts)

    dates = list(whole_calendar.keys())
    fractional_dates = set(fractional_calendar.keys())  # We choose set instead of list for faster searching

    return [i for i in dates if i not in fractional_dates]


# ======== Test Block ========


if __name__ == "__main__":
    
   test = main_day_weeker(2029,1)
   date = test[datetime(2029,11,20)]
   
   print(f"Mexican Revolution is week  '{date}'")