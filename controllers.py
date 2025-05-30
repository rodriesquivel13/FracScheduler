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
    # Se obtiene el año
    year = request.args.get('year', 2027, type=int)
    # Este valor se usará en la lógica interna para asignar fracciones y demás cálculos.
    user_selected_start = request.args.get('start_day', 1, type=int)
    
    # Cálculos de lógica interna:
    fractional_indices = fractional_index_maker(year, user_selected_start)
    unfractional_dates = unfractional_dates_list(year, user_selected_start)
    
    # Para la visualización, fija la presentación utilizando lunes como primer día.
    display_cal = calendar.Calendar(firstweekday=0)
    months = [display_cal.monthdayscalendar(year, month) for month in range(1, 13)]
    previous_december = display_cal.monthdayscalendar(year - 1, 12)
    
    # Cabecera fija de lunes a domingo.
    day_names = [calendar.day_abbr[i] for i in range(7)]
    
    # Procesar las fracciones seleccionadas.
    selected_fractions = request.args.getlist('fractions', type=str)
    if 'all' in selected_fractions:
        selected_fractions = list(range(8)) + ['unfractional', 'all']
    else:
        selected_fractions = [int(f) if f.isdigit() else f for f in selected_fractions]
    
    # Si no se selecciona 'unfractional', se omiten esas fechas.
    if 'unfractional' not in selected_fractions:
        unfractional_dates = []

    return render_template('calendar.html',
                           year=year,
                           months_with_index=list(enumerate(months)),
                           start_day=user_selected_start,  # Se mantiene el valor lógico seleccionado
                           day_names=day_names,
                           calendar=calendar,
                           fractional_indices=fractional_indices,
                           fraction_colors=fraction_colors,
                           datetime=datetime,
                           previous_december=previous_december,
                           selected_fractions=selected_fractions,
                           unfractional_dates=unfractional_dates)

@controllers.route('/generate_pdf')
def generate_pdf():
    start_year = request.args.get('start_year', type=int)
    end_year = request.args.get('end_year', type=int)
    # Aquí el valor start_day se usa para la lógica interna (al calcular las fechas con fracción)
    start_day = request.args.get('start_day', 0, type=int)
    selected_fractions = request.args.getlist('fractions', type=str)
    selected_fractions = [int(f) if f.isdigit() else f for f in selected_fractions]

    # Crear un buffer para el PDF
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    y = 750

    c.drawString(100, y, f"Fechas de uso correspondientes a las fracciones: {', '.join(map(str, selected_fractions))}")
    y -= 20

    for year in range(start_year, end_year + 1):
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
    return send_file(buffer, as_attachment=True, download_name=f"fracciones_{start_year}_{end_year}.pdf",
                     mimetype='application/pdf')

@controllers.route('/hunt_fraction')
def hunt_fraction():
    # Ruta para buscar la fracción de una fecha dada.
    date_str = request.args.get('hunter_date')  # Formato: yyyy-mm-dd
    user_selected_start = request.args.get('start_day', 1, type=int)

    if not date_str:
        return "No date provided", 400

    try:
        wishful_date = datetime.strptime(date_str, "%Y-%m-%d")
        result = fraction_hunter(wishful_date.year, wishful_date.month, wishful_date.day, user_selected_start)
    except ValueError:
        return "Invalid date format", 400

    if isinstance(result, str):
        return result, 404

    # Para la visualización, se utiliza siempre un calendario con lunes como primer día.
    display_cal = calendar.Calendar(firstweekday=0)
    months = [(i, display_cal.monthdayscalendar(wishful_date.year, i + 1)) for i in range(12)]
    day_names = [calendar.day_abbr[i] for i in range(7)]
    
    return render_template('calendar.html',
                           year=wishful_date.year,
                           start_day=user_selected_start,  # Lógica interna sigue usando el valor seleccionado
                           months_with_index=months,
                           day_names=day_names,
                           calendar=calendar,
                           fractional_indices=fractional_index_maker(wishful_date.year, user_selected_start),
                           previous_december=display_cal.monthdayscalendar(wishful_date.year - 1, 12),
                           fraction_colors=fraction_colors,
                           datetime=datetime,
                           selected_fractions=[result[0]],
                           unfractional_dates=[])
