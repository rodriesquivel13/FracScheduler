from flask import Flask, render_template, request
import calendar
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    year = request.args.get('year', datetime.now().year, type=int)
    start_day = request.args.get('start_day', 0, type=int)  # 0: Lunes, 6: Domingo
    cal = calendar.Calendar(firstweekday=start_day)
    months = [cal.monthdayscalendar(year, i) for i in range(1, 13)]
    
    # Adjust the first week of January to include the last days of December
    if months[0][0][0] == 0:
        last_days_december = calendar.Calendar(firstweekday=start_day).monthdayscalendar(year - 1, 12)[-1]
        last_days_december = [day for day in last_days_december if day != 0]
        last_days_december.reverse()  # Reverse the order to start with the correct day
        for i in range(len(months[0][0])):
            if months[0][0][i] == 0:
                months[0][0][i] = last_days_december.pop()

    day_names = [calendar.day_name[(i + start_day) % 7] for i in range(7)]
    return render_template('calendar.html', year=year, months=months, start_day=start_day, day_names=day_names, calendar=calendar)

if __name__ == '__main__':
    app.run(debug=True)