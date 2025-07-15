from datetime import datetime
from . import hollydays
from . import calendar as cd
from . import parameters

#============= Global Variables =====================
fractions_quantity = parameters.number_of_fractions()
weeks_expected_per_year = parameters.weeks_expected_per_year()

# ======== Fractions-related functions ========
def holly_weeks(current_year, weekday_calendar_starts):
    """
    Some weeks have special hollydays which no one want to miss them. 
    Those hollydays could be deterministic or probabilistic.
    """

    def deterministic_holly_weeks(current_year,weekday_calendar_starts,type):
        """
        Deterministic hollydays are those which have an specific rule to determinate them,
        for example mexican revolution day is third monday of each november, so this funcion return us 
        the list of those weeks which have these hollydays.
        """
        if type == "regular":
            newyear = hollydays.new_year(current_year)
            constitution = hollydays.constitution_day(current_year)
            benito = hollydays.benito_juarez_birthday(current_year)
            revolution = hollydays.mexican_revolution_day(current_year)
            easter = hollydays.easter_saturday(current_year)
            semana_santa = hollydays.sabado_santo(current_year)
            christ = hollydays.christmas(current_year)
            dad = hollydays.father_day(current_year)

            special_dates = [newyear,constitution,benito,revolution,easter,semana_santa,christ,dad]
        else:
            semana_santa = hollydays.sabado_santo(current_year + 1)
            thanks = hollydays.thanksgiving(current_year)
            newyear = hollydays.new_year(current_year + 1)
            christ = hollydays.christmas(current_year)
            special_dates = [semana_santa,thanks,newyear,christ]

        calendar = cd.main_day_weeker(current_year, weekday_calendar_starts)
        week_index = []

        for i in special_dates:
            week = calendar[i]
            week_index.append(week)

        return week_index

    def probabilistic_holly_weeks(current_year,weekday_calendar_starts,type):
        """
        Others hollydays don't let us get sure about whether the week which contains the date will the week when the date will celebrated.
        For example, figure out independence day takes on tuesday and owr fractional week begins also in tusday but people wants to celecrate in previous momday.
        It's worth to say, according the earlier case, if we take the weeks which have these hollydays and we take the previous week, we cover all the cases.
        So, you can intuit what this function does.
        """
        if type == "regular":
            valentines = hollydays.valentines_day(current_year)
            mom = hollydays.mothers_day(current_year)
            work = hollydays.work_day(current_year)
            independence = hollydays.independence_day(current_year)

            special_dates = [valentines,mom,work,independence]
        else:
            special_dates = []

        calendar = cd.main_day_weeker(current_year, weekday_calendar_starts)
        week_index = []

        for i in special_dates:
            week = calendar[i]
            week_index.append(week)
        
        before_week_index = []
        for k in week_index:
            before_week_index.append([k[0] - 1])

        return week_index + before_week_index

    regular = deterministic_holly_weeks(current_year, weekday_calendar_starts)
    irregular = probabilistic_holly_weeks(current_year, weekday_calendar_starts)

    gold = []                       # This block is looking for clean the list up.
    for i in regular + irregular:
        if i not in gold:
            gold.append(i)
    gold_num = [k[0] for k in gold]
    gold_num.sort()
    gold = [[k] for k in gold_num]

    return gold

def maintenance_weeks_list(current_year, weekday_calendar_starts, maintenance_path,type):
    """
    Select week indices for maintenance based on a path and the year characteristics.
    """
    weeks_per_fraction = weeks_expected_per_year // fractions_quantity
    reserved_weeks = weeks_expected_per_year - fractions_quantity * weeks_per_fraction
    
    def maintenance_weeks_paths(current_year, weekday_calendar_starts,reserved_weeks):
        """
        This function crafts a dictionarie with no hollyweeks in its keys (datetimes),
        and also it bounds the dictionarie particulary.
        """
        if cd.extra_week_indicator(current_year,weekday_calendar_starts):
            reserved_weeks += 1
        calendar = cd.main_day_weeker(current_year, weekday_calendar_starts)
        gold = holly_weeks(current_year, weekday_calendar_starts)

        if type == "regular":
            regular = {k:v for (k,v) in calendar.items() if v not in gold}
            list = [[i//7] for i in range(len(regular.values()))]
            regular = dict(zip(regular.keys(),list))
            bound = len(regular.keys()) // 7
            max_regular_len = bound // reserved_weeks * reserved_weeks
            dic = {k: v for k, v in regular.items() if v[0] < max_regular_len}

            return {k:[(v[0] + (current_year % fractions_quantity)) % (max_regular_len // reserved_weeks)] for (k,v) in dic.items()}
        
        else:
            full_snow_calendar = {k:v for k,v in calendar.items() if v[0] < weeks_expected_per_year // 2}
            full_sand_calendar = {k:[v[0] - weeks_expected_per_year // 2] for k,v in calendar.items() if v[0] >= weeks_expected_per_year // 2}

            snow_reserved_weeks = [[18],[25]]
            if cd.extra_week_indicator(current_year,weekday_calendar_starts):
                sand_reserved_weeks = [[12],[19],[26]]
            else:
                sand_reserved_weeks = [[18],[25]]

            snow_maintenance_dic = {k:v for k,v in full_snow_calendar.items() if v in snow_reserved_weeks}
            sand_maintenance_dic = {k:v for k,v in full_sand_calendar.items() if v in sand_reserved_weeks}

            pre_dic = {**snow_maintenance_dic,**sand_maintenance_dic}
            return {k:[0] for k in pre_dic.keys()}

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
    
def fractional_day_weeker(current_year, weekday_calendar_starts, maintenance_path,type):
    """
    This function lists weeks which are able to distribute their to fraction's owners.
    """
    semana_santa_index = cd.semana_santa_weeker(current_year,weekday_calendar_starts)
    easter_index = cd.easter_weeker(current_year,weekday_calendar_starts)
    maintenance_weeks = maintenance_weeks_list(current_year,weekday_calendar_starts, maintenance_path)
    
    if type == "regular":
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
    
    else:
        day_week_indexes_dic = cd.main_day_weeker(current_year,weekday_calendar_starts)

        snow_weeks_in_a_row = 6
        full_snow_calendar = {k:v for k,v in day_week_indexes_dic.items() if v[0] < weeks_expected_per_year // 2}
        clean_snow_calendar = {k:v for k,v in full_snow_calendar.items() if v not in maintenance_weeks}
        snow_index_list = [[i] for i in range(fractions_quantity // 2) for _ in range(snow_weeks_in_a_row * 7)]
        indexed_snow_calendar = dict(zip(clean_snow_calendar.keys(),snow_index_list))

        sand_weeks_in_a_row = 2
        full_sand_calendar = {k:[v[0] - weeks_expected_per_year // 2] for k,v in day_week_indexes_dic.items() if v[0] >= weeks_expected_per_year // 2}
        clean_sand_calendar = {k:v for k,v in full_sand_calendar.items() if v not in maintenance_weeks}
        sand_index_list = [[i] for _ in range(3) for i in range(fractions_quantity // 2) for __ in range(sand_weeks_in_a_row * 7)]
        indexed_sand_calendar = dict(zip(clean_sand_calendar,sand_index_list))

        return {**indexed_snow_calendar,**indexed_sand_calendar}
        

def fractional_index_maker(current_year, weekday_calendar_starts, maintenance_path,type):
    """
    This function indexes each date with fraction's index.
    """
    fractional_calendar_week_indexed = fractional_day_weeker(current_year,weekday_calendar_starts, maintenance_path)
    total_fractional_weeks_quantity = weeks_expected_per_year // fractions_quantity * fractions_quantity
    if type == "regular":
        week_index_list = list(fractional_calendar_week_indexed.values())

        fraction_index_list = []
        for i in range(len(week_index_list)):
            week_index = week_index_list[i]
            fraction_index = [((week_index[0] - (current_year % fractions_quantity))  % total_fractional_weeks_quantity) % fractions_quantity]
            fraction_index_list.append(fraction_index)

        return dict(zip(fractional_calendar_week_indexed.keys(),fraction_index_list))
    
    else:
        season_fractional_weeeks_quantity = total_fractional_weeks_quantity // 2
        season_fractions_quantity = fractions_quantity // 2
        lenght_list = list(fractional_calendar_week_indexed.items())
        half = len(lenght_list) // 2

        snow_fractional_calendar_week_indexed = dict(lenght_list[:half])
        snow__week_index_list = list(snow_fractional_calendar_week_indexed.values())
        snow_fraction_index_list = []
        for i in range(len(snow__week_index_list)):
            snow_week_index = snow__week_index_list[i]
            snow_fraction_index = [((snow_week_index[0] - (current_year % season_fractions_quantity))  % season_fractional_weeeks_quantity) % season_fractions_quantity]
            snow_fraction_index_list.append(snow_fraction_index)
        snow_fractional_index_maker = dict(zip(snow_fractional_calendar_week_indexed.keys(),snow_fraction_index_list))

        sand_fractional_calendar_week_indexed = dict(lenght_list[half:])
        sand__week_index_list = list(sand_fractional_calendar_week_indexed.values())
        sand_fraction_index_list = []
        for i in range(len(sand__week_index_list)):
            sand_week_index = sand__week_index_list[i]
            sand_fraction_index = [((sand_week_index[0] - (current_year % season_fractions_quantity))  % season_fractional_weeeks_quantity) % season_fractions_quantity + season_fractions_quantity]
            sand_fraction_index_list.append(sand_fraction_index)
        sand_fractional_index_maker = dict(zip(sand_fractional_calendar_week_indexed.keys(),sand_fraction_index_list))  
        
        return {**snow_fractional_index_maker,**sand_fractional_index_maker}

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
        return f"So sorry, your wishful date isn't available due our current schedule"

def unfractional_dates_list(current_year, weekday_calendar_starts, maintenance_path):
    """
    This funcion has as goal crafting a list with no fractional hollydays, such that,
    this list must have the rest of the hollydays of each year.
    """
    whole_calendar = cd.main_day_sequence(current_year, weekday_calendar_starts)
    fractional_calendar = fractional_index_maker(current_year, weekday_calendar_starts, maintenance_path)

    hollydays = list(whole_calendar.keys())
    fractional_dates = set(fractional_calendar.keys())  # We choose set instead of list for faster searching

    return [i for i in hollydays if i not in fractional_dates]



# ======== Test Block ========

if __name__ == "__main__":
    print(f'ff')

