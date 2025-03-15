from flask import Flask, render_template, request
import calendar
from datetime import datetime
from utils import fractional_index_maker, unfractional_dates_list

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
    
    # Obtener diciembre del año anterior
    previous_december = cal.monthdayscalendar(year - 1, 12)

    # Obtener las fechas no fraccionadas
    unfractional_dates = unfractional_dates_list(year, start_day)

    # Obtener las fracciones seleccionadas
    selected_fractions = request.args.getlist('fractions', type=str)
    if 'all' in selected_fractions:
        selected_fractions = list(range(8)) + ['unfractional', 'all']
    else:
        selected_fractions = [int(f) if f.isdigit() else f for f in selected_fractions]

    # Asegurarse de que 'unfractional' solo esté seleccionado si está en selected_fractions
    if 'unfractional' not in selected_fractions:
        unfractional_dates = []

    day_names = [calendar.day_name[(i + start_day) % 7] for i in range(7)]
    months_with_index = list(enumerate(months))
    return render_template('calendar.html', year=year, months_with_index=months_with_index, start_day=start_day, day_names=day_names, calendar=calendar, fractional_indices=fractional_indices, fraction_colors=fraction_colors, datetime=datetime, previous_december=previous_december, selected_fractions=selected_fractions, unfractional_dates=unfractional_dates)

if __name__ == '__main__':
    app.run(debug=True)