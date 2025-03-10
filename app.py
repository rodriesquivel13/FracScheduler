from flask import Flask, render_template
import calendar
from datetime import datetime

app = Flask(__name__)

def generate_year_calendar(year):
    """Generate a full year calendar for display."""
    cal = calendar.Calendar()
    year_data = {}

    for month in range(1, 13):
        month_days = cal.monthdayscalendar(year, month)
        month_name = calendar.month_name[month]
        year_data[month_name] = month_days

    return year_data, year

@app.route('/')
@app.route('/<int:year>')
def index(year=None):
    """Render the calendar for a specific year."""
    if not year:
        year = datetime.now().year

    year_calendar, year = generate_year_calendar(year)
    return render_template('calendar.html', year_calendar=year_calendar, year=year)

if __name__ == '__main__':
    app.run(debug=True)