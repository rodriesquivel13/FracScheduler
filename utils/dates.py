from datetime import datetime, timedelta

#============= Global Variables =====================
fractions_quantity = 8
weeks_expected_per_year = 365//7

# ======== Dates Numerical Calculations ========
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

def sabado_santo(year): 
    """
    Function for calculating Sabado santo (Samana Santa's Saturday)
    """
    return gauss_easter(year) - timedelta(days = 1)

def easter_saturday(year):
    """
    Function for calculation easter's saturday.
    """
    return gauss_easter(year) + timedelta(days = 6)

def new_year(current_year):
    """
    January first calculation
    """
    return datetime(current_year,1,1)

def christmas(current_year):
    """
    christmas calculation
    """
    return datetime(current_year,12,25)

def constitution_day(current_year):
    """
    First Monday of each February. It ever be a "puente"
    """
    count = 0 
    for day in range(1,29):
        date = datetime(current_year,2,day)
        if date.weekday() == 0:
            count += 1
            if count == 1:
                return date
            
def benito_juarez_birthday(current_year):
    """
    Third Monday of each March. It ever be a "puente"
    """
    count = 0
    for day in range(1, 32):  # March has 31 days
        date = datetime(current_year, 3, day)
        if date.weekday() == 0:  # monday is equal to 0
            count += 1
            if count == 3:
                return date

def mexican_revolution_day(current_year):
    """
    Since 2006 mexican government decreed day of the revolution will celebrated on third monday of november in each year.
     So, this function calculates when is that particular monday.
        """
    count = 0
    for day in range(1, 31):  # november has 30 days
        date = datetime(current_year, 11, day)
        if date.weekday() == 0:  # monday is equal to 0
            count += 1
            if count == 3:
                return date
            
def valentines_day(current_year):
    """
    Valentine's Day calculation
    """
    return datetime(current_year,2,14)

def mothers_day(current_day):
    """
    Mother's Day Calculation
    """
    return datetime(current_day,5,10)
def work_day(current_year):
    """
    Sometimes it could be a "puente" only if it is monday or friday.
    """
    date = datetime(current_year,5,1)
    return date

def independence_day(current_year):
    """
    Sometimes it could be a "puente" only if it is monday or friday.
    """
    date = datetime(current_year,9,16)
    return date

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

def extra_week_indicator(year,weekday_calendar_starts):
    """
    We expect years have 52 weeks but actually,
    by how we defined the first day of each year,
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
    This functions return us the week index of semana semana each year, 
    depending on which weekday it starts on.
    """
    saturday = sabado_santo(year)
    calendar = main_day_weeker(year,weekday_calendar_starts)
    return calendar[saturday]

def easter_weeker(year, weekday_calendar_starts):
    """
    This functions return us the week index of semana diabla (the week inmediatly after semana santa) each year,
    depending on which weekday it starts on.
    """
    saturday = easter_saturday(year)
    calendar = main_day_weeker(year,weekday_calendar_starts)
    return calendar[saturday]
    
def holly_weeks(current_year, weekday_calendar_starts):
    """
    Some weeks have special dates which no one want to miss them. 
    Those dates could be deterministic or probabilistic.
    """

    def deterministic_holly_weeks(current_year,weekday_calendar_starts):
        """
        Deterministic hollydays are those which have an specific rule to determinate them,
        for example mexican revolution day is third monday of each november, so this funcion return us 
        the list of those weeks which have these hollydays.
        """
        newyear = new_year(current_year)
        constitution = constitution_day(current_year)
        benito = benito_juarez_birthday(current_year)
        revolution = mexican_revolution_day(current_year)
        easter = easter_saturday(current_year)
        semana_santa = sabado_santo(current_year)
        christ = christmas(current_year)

        special_dates = [newyear,constitution,benito,revolution,easter,semana_santa,christ]
        calendar = main_day_weeker(current_year, weekday_calendar_starts)
        week_index = []

        for i in special_dates:
            week = calendar[i]
            week_index.append(week)

        return week_index

    def probabilistic_holly_weeks(current_year,weekday_calendar_starts):
        """
        Others dates don't let us get sure about whether the week which contains the date will the week when the date will celebrated.
        For example, figure out independence day takes on tuesday and owr fractional week begins also in tusday but people wants to celecrate in previous momday.
        It's worth to say, according the earlier case, if we take the weeks which have these dates and we take the previous week, we cover all the cases.
        So, you can intuit what this function does.
        """
    
        valentines = valentines_day(current_year)
        mom = mothers_day(current_year)
        work = work_day(current_year)
        independence = independence_day(current_year)

        special_dates = [valentines,mom,work,independence]
        calendar = main_day_weeker(current_year, weekday_calendar_starts)
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
        if extra_week_indicator(current_year,weekday_calendar_starts):
            reserved_weeks +=1

        calendar = main_day_weeker(current_year, weekday_calendar_starts)
        gold = holly_weeks(current_year, weekday_calendar_starts)

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

    calendar = main_day_weeker(current_year,weekday_calendar_starts)

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
    semana_santa_index = semana_santa_weeker(current_year,weekday_calendar_starts)
    easter_index = easter_weeker(current_year,weekday_calendar_starts)
    maintenance_weeks = maintenance_weeks_list(current_year,weekday_calendar_starts, maintenance_path)
    
    special_weeks = []
    special_weeks.append(semana_santa_index)
    special_weeks.append(easter_index)

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
    whole_calendar = main_day_sequence(current_year, weekday_calendar_starts)
    fractional_calendar = fractional_index_maker(current_year, weekday_calendar_starts, maintenance_path)

    dates = list(whole_calendar.keys())
    fractional_dates = set(fractional_calendar.keys())  # We choose set instead of list for faster searching

    return [i for i in dates if i not in fractional_dates]

# ======== Test Block ========

if __name__ == "__main__":
    print(f'ff')