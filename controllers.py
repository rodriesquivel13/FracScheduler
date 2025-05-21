from flask import Blueprint, render_template, request, send_file
import calendar
from datetime import datetime
from utils import fractional_index_maker, unfractional_dates_list, fraction_hunter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

controllers = Blueprint('controllers', __name__)

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

@controllers.route('/')
def index():
    year = request.args.get('year',2027, type=int)
    start_day = request.args.get('start_day', 1, type=int)  # 0: Lunes, 6: Domingo
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

@controllers.route('/generate_pdf')
def generate_pdf():
    start_year = request.args.get('start_year', type=int)
    end_year = request.args.get('end_year', type=int)
    start_day = request.args.get('start_day', 0, type=int)  # 0: Lunes, 6: Domingo
    selected_fractions = request.args.getlist('fractions', type=str)
    selected_fractions = [int(f) if f.isdigit() else f for f in selected_fractions]

    # Crear un buffer para el PDF
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    y = 750

    c.drawString(100, y, f"Fechas de uso correspondientes a las fracciones: {', '.join(map(str, selected_fractions))}")
    y -= 20

    for year in range(start_year, end_year + 1):
        cal = calendar.Calendar(firstweekday=start_day)
        fractional_indices = fractional_index_maker(year, start_day)
        c.drawString(100, y, f"Año {year}")
        y -= 20

        for date, frac in fractional_indices.items():
            if frac[0] in selected_fractions:
                c.drawString(100, y, date.strftime("%Y-%m-%d"))
                y -= 20
                if y < 50:
                    c.showPage()
                    y = 750

    c.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name=f"fracciones_{start_year}_{end_year}.pdf", mimetype='application/pdf')

@controllers.route('/hunt_fraction')
def hunt_fraction():
    from utils import fraction_hunter  # Asegúrate que esté accesible

    date_str = request.args.get('hunter_date')  # formato: yyyy-mm-dd
    start_day = request.args.get('start_day', 1, type=int)

    if not date_str:
        return "No date provided", 400

    try:
        wishful_date = datetime.strptime(date_str, "%Y-%m-%d")
        result = fraction_hunter(wishful_date.year, wishful_date.month, wishful_date.day, start_day)
    except ValueError:
        return "Invalid date format", 400

    # Si retorna string (error personalizado), mostrarlo
    if isinstance(result, str):
        return result, 404

    # Redirige al calendario, con la fracción correspondiente preseleccionada
    return render_template('calendar.html',
        year=wishful_date.year,
        start_day=start_day,
        months_with_index=[(i, calendar.Calendar(firstweekday=start_day).monthdayscalendar(wishful_date.year, i+1)) for i in range(12)],
        day_names=[calendar.day_name[(i + start_day) % 7] for i in range(7)],
        calendar=calendar,
        fractional_indices=fractional_index_maker(wishful_date.year, start_day),
        previous_december=calendar.Calendar(firstweekday=start_day).monthdayscalendar(wishful_date.year - 1, 12),
        fraction_colors=fraction_colors,
        datetime=datetime,
        selected_fractions=[result[0]],  # Esto selecciona el checkbox correcto
        unfractional_dates=[],  # Por ahora no mostramos unfractional
    )
