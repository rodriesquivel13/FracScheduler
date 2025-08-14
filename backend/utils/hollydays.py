from datetime import datetime, timedelta

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

# ========== Regular Deterministic hollydays
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

# ============= Irregular Deterministic hollydays
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
            
def father_day(current_year):
    """
    Third Sunday of each june.
    """
    count = 0
    for day in range(1, 31):  # june has 30 days
        date = datetime(current_year, 6, day)
        if date.weekday() == 6:  # sunday is equal to 6
            count += 1
            if count == 3:
                return date
            
def thanksgiving(current_year):
    """
    Fourth thursday of each november
    """
    count = 0
    for day in range(1, 31):  # november has 30 days
        date = datetime(current_year, 11, day)
        if date.weekday() == 3:  # monday is equal to 0
            count += 1
            if count == 4:
                return date
            
# ========= No deterministic hollydays

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


# ========= Hollydays Dics ====
def regular_hollydays_dic(
    current_year
):
    semana_santa = sabado_santo(current_year)
    easter = easter_saturday(current_year)
    new = new_year(current_year)
    chris_1 = christmas(current_year)
    chris_2 = christmas(current_year - 1)
    constitution = constitution_day(current_year)
    benito = benito_juarez_birthday(current_year)
    revolution = mexican_revolution_day(current_year)
    father = father_day(current_year)
    thanks = thanksgiving(current_year)
    valentines = valentines_day(current_year)
    mother = mothers_day(current_year)
    work = work_day(current_year)
    independence = independence_day(current_year)
    return {
    semana_santa : "Holy Week Weekend",
    easter : "Easter Weekend",
    new : "New Year's Day",
    chris_1 : "Christmas Day",
    chris_2 : "Christmas Day",
    constitution : "Mexican Constitution Weekend",
    benito : "Benito Juárez Weekend",
    revolution : "Mexican Revolution Weekend",
    father: "Father's Day",
    thanks : "Thanksgiving Day",
    valentines: "Valentine's Day",
    mother : "Mother's Day",
    work : "Labor Day",
    independence : "Mexican Independence Day"
}

def snow_hollydays_dic(
    current_year
):
    semana_santa = sabado_santo(current_year + 1)
    easter = easter_saturday(current_year + 1)
    new = new_year(current_year + 1)
    chris = christmas(current_year)
    constitution = constitution_day(current_year + 1)
    benito = benito_juarez_birthday(current_year + 1)
    revolution = mexican_revolution_day(current_year)
    father = father_day(current_year + 1)
    thanks = thanksgiving(current_year)
    valentines = valentines_day(current_year + 1)
    mother = mothers_day(current_year + 1)
    work = work_day(current_year + 1)
    independence_1 = independence_day(current_year)
    independence_2 = independence_day(current_year + 1)
    independence_3 = independence_day(current_year - 1)

    return {
    semana_santa : "Holy Week Weekend",
    easter : "Easter Weekend",
    new : "New Year's Day",
    chris : "Christmas Day",
    constitution : "Mexican Constitution Weekend",
    benito : "Benito Juárez Weekend",
    revolution : "Mexican Revolution Weekend",
    father: "Father's Day",
    thanks : "Thanksgiving Day",
    valentines: "Valentine's Day",
    mother : "Mother's Day",
    work : "Labor Day",
    independence_1 : "Mexican Independence Day",
    independence_2 : "Mexican Independence Day",
    independence_3 : "Mexican Independence Day"
}

# ======== Test Block ========

if __name__ == "__main__":
    print(thanksgiving(2027))