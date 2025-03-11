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
    day_names = [calendar.day_name[(i + start_day) % 7] for i in range(7)]
    return render_template('calendar.html', year=year, months=months, start_day=start_day, day_names=day_names, calendar=calendar)

if __name__ == '__main__':
    app.run(debug=True)