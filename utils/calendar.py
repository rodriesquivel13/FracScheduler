from datetime import datetime, timedelta
from . import dates
#============= Global Variables =====================
fractions_quantity = 8
weeks_expected_per_year = 365//7

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
    saturday = dates.sabado_santo(year)
    calendar = main_day_weeker(year,weekday_calendar_starts)
    return calendar[saturday]

def easter_weeker(year, weekday_calendar_starts):
    """
    This functions return us the week index of semana diabla (the week inmediatly after semana santa) each year,
    depending on which weekday it starts on.
    """
    saturday = dates.easter_saturday(year)
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
        newyear = dates.new_year(current_year)
        constitution = dates.constitution_day(current_year)
        benito = dates.benito_juarez_birthday(current_year)
        revolution = dates.mexican_revolution_day(current_year)
        easter = dates.easter_saturday(current_year)
        semana_santa = dates.sabado_santo(current_year)
        christ = dates.christmas(current_year)

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
    
        valentines = dates.valentines_day(current_year)
        mom = dates.mothers_day(current_year)
        work = dates.work_day(current_year)
        independence = dates.independence_day(current_year)

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