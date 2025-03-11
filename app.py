from flask import Flask, render_template, request
import calendar
from datetime import datetime
from utils import fractional_index_maker

app = Flask(__name__)

# Definir los colores para las fracciones
fraction_colors = [
    "#CC00CC",  # Color para la fracción 0
    "#ADD8E6",  # Color para la fracción 1
    "#4472C4",  # Color para la fracción 2
    "#B3DE99",  # Color para la fracción 3
    "#C00000",  # Color para la fracción 4
    "#DDA0DD",  # Color para la fracción 5
    "#00B050",  # Color para la fracción 6
    "#FFE5B4"   # Color para la fracción 7
]

@app.route('/')
def index():
    year = request.args.get('year', datetime.now().year, type=int)
    start_day = request.args.get('start_day', 0, type=int)  # 0: Lunes, 6: Domingo
    cal = calendar.Calendar(firstweekday=start_day)
    months = [cal.monthdayscalendar(year, i) for i in range(1, 13)]
    
    # Obtener el diccionario de fracciones
    fractional_indices = fractional_index_maker(year, start_day)
    
    # Ajustar la primera semana de enero para incluir los últimos días de diciembre
    if months[0][0][0] == 0:
        last_days_december = calendar.Calendar(firstweekday=start_day).monthdayscalendar(year - 1, 12)[-1]
        last_days_december = [day for day in last_days_december if day != 0]
        last_days_december.reverse()  # Reverse the order to start with the correct day
        for i in range(len(months[0][0])):
            if months[0][0][i] == 0:
                months[0][0][i] = last_days_december.pop()

    day_names = [calendar.day_name[(i + start_day) % 7] for i in range(7)]
    months_with_index = list(enumerate(months))
    return render_template('calendar.html', year=year, months_with_index=months_with_index, start_day=start_day, day_names=day_names, calendar=calendar, fractional_indices=fractional_indices, fraction_colors=fraction_colors, datetime=datetime)

if __name__ == '__main__':
    app.run(debug=True)