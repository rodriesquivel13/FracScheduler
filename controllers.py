from flask import Blueprint, render_template, request, send_file 
import calendar
from datetime import datetime
from utils import (
    fractional_index_maker,
    unfractional_dates_list,
    fraction_hunter
)
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

# Importamos los diccionarios desde models.py
from models import apartament_maintenance_path, apartament_weekday_calendar_starts

controllers = Blueprint('controllers', __name__)

# La función map_level_to_internal ya no se utiliza, pero se conserva por compatibilidad.
def map_level_to_internal(level):
    if level in (2, 5, 8):
        return 1
    elif level in (3, 6, 9):
        return 2
    elif level in (4, 7, 10):
        return 3
    else:
        return 1  # Fallback a Tuesday

@controllers.route('/')
def index():
    year = request.args.get('year', 2026, type=int)
    # Se recibe el apartament en lugar de un nivel; se asigna un default (204)
    apartament = request.args.get('apartament', 204, type=int)
    maintenance_path = apartament_maintenance_path.get(apartament, 1)
    weekday_calendar_starts = apartament_weekday_calendar_starts.get(apartament, 1)
    
    # Se actualizan las llamadas a las funciones de utils.py con los nuevos parámetros
    fractional_indices      = fractional_index_maker(year, weekday_calendar_starts, maintenance_path)
    fractional_indices_prev = fractional_index_maker(year - 1, weekday_calendar_starts, maintenance_path)
    fractional_indices_next = fractional_index_maker(year + 1, weekday_calendar_starts, maintenance_path)

    unfractional_dates      = unfractional_dates_list(year, weekday_calendar_starts, maintenance_path)
    unfractional_dates_prev = unfractional_dates_list(year - 1, weekday_calendar_starts, maintenance_path)
    unfractional_dates_next = unfractional_dates_list(year + 1, weekday_calendar_starts, maintenance_path)

    display_cal       = calendar.Calendar(firstweekday=0)
    months            = [display_cal.monthdayscalendar(year, m) for m in range(1, 13)]
    previous_december = display_cal.monthdayscalendar(year - 1, 12)
    day_names = [calendar.day_abbr[i] for i in range(7)]

    selected_fractions = request.args.getlist('fractions', type=str)
    if 'all' in selected_fractions:
        selected_fractions = list(range(8)) + ['unfractional', 'all']
    else:
        selected_fractions = [int(f) if f.isdigit() else f for f in selected_fractions]

    if 'unfractional' not in selected_fractions:
        unfractional_dates = []
        unfractional_dates_prev = []
        unfractional_dates_next = []

    return render_template(
        'calendar.html',
        year=year,
        months_with_index=list(enumerate(months)),
        # Se envían al template el apartament seleccionado y la lista de apartaments disponibles
        apartament=apartament,
        available_apartaments=sorted(list(apartament_maintenance_path.keys())),
        day_names=day_names,
        calendar=calendar,
        fraction_colors=[
            "#CC00CC",  # 0
            "#ADD8E6",  # 1
            "#4472C4",  # 2
            "#B3DE99",  # 3
            "#C00000",  # 4
            "#DDA0DD",  # 5
            "#00B050",  # 6
            "#FFE5B4"   # 7
        ],
        datetime=datetime,
        fractional_indices=fractional_indices,
        fractional_indices_prev=fractional_indices_prev,
        fractional_indices_next=fractional_indices_next,
        unfractional_dates=unfractional_dates,
        unfractional_dates_prev=unfractional_dates_prev,
        unfractional_dates_next=unfractional_dates_next,
        previous_december=previous_december,
        selected_fractions=selected_fractions
    )

@controllers.route('/generate_pdf')
def generate_pdf():
    start_year = request.args.get('start_year', type=int)
    end_year   = request.args.get('end_year', type=int)
    apartament = request.args.get('apartament', 204, type=int)
    maintenance_path = apartament_maintenance_path.get(apartament, 1)
    weekday_calendar_starts = apartament_weekday_calendar_starts.get(apartament, 1)
    
    selected_fractions = request.args.getlist('fractions', type=str)
    selected_fractions = [int(f) if f.isdigit() else f for f in selected_fractions]

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    y = 750
    c.drawString(100, y, f"Usage dates for fractions: {', '.join(map(str, selected_fractions))}")
    y -= 20

    for year in range(start_year, end_year + 1):
        fractional_indices = fractional_index_maker(year, weekday_calendar_starts, maintenance_path)
        c.drawString(100, y, f"Year {year}")
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
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"fractions_{start_year}_{end_year}.pdf",
        mimetype='application/pdf'
    )

@controllers.route('/hunt_fraction')
def hunt_fraction():
    date_str = request.args.get('hunter_date')
    apartament = request.args.get('apartament', 204, type=int)
    maintenance_path = apartament_maintenance_path.get(apartament, 1)
    weekday_calendar_starts = apartament_weekday_calendar_starts.get(apartament, 1)
    
    if not date_str:
        return "No date provided", 400

    try:
        wishful_date = datetime.strptime(date_str, "%Y-%m-%d")
        result = fraction_hunter(
            wishful_date.year,
            wishful_date.month,
            wishful_date.day,
            weekday_calendar_starts,
            maintenance_path
        )
    except ValueError:
        return "Invalid date format", 400

    if isinstance(result, str):
        return result, 404

    fractional_indices      = fractional_index_maker(wishful_date.year, weekday_calendar_starts, maintenance_path)
    fractional_indices_prev = fractional_index_maker(wishful_date.year - 1, weekday_calendar_starts, maintenance_path)
    fractional_indices_next = fractional_index_maker(wishful_date.year + 1, weekday_calendar_starts, maintenance_path)

    unfractional_dates      = unfractional_dates_list(wishful_date.year, weekday_calendar_starts, maintenance_path)
    unfractional_dates_prev = unfractional_dates_list(wishful_date.year - 1, weekday_calendar_starts, maintenance_path)
    unfractional_dates_next = unfractional_dates_list(wishful_date.year + 1, weekday_calendar_starts, maintenance_path)

    display_cal = calendar.Calendar(firstweekday=0)
    months = [(i, display_cal.monthdayscalendar(wishful_date.year, i + 1)) for i in range(12)]
    previous_december = display_cal.monthdayscalendar(wishful_date.year - 1, 12)
    day_names = [calendar.day_abbr[i] for i in range(7)]

    return render_template(
        'calendar.html',
        year=wishful_date.year,
        apartament=apartament,
        available_apartaments=sorted(list(apartament_maintenance_path.keys())),
        day_names=day_names,
        calendar=calendar,
        fraction_colors=[
            "#CC00CC",  # 0
            "#ADD8E6",  # 1
            "#4472C4",  # 2
            "#B3DE99",  # 3
            "#C00000",  # 4
            "#DDA0DD",  # 5
            "#00B050",  # 6
            "#FFE5B4"   # 7
        ],
        datetime=datetime,
        previous_december=previous_december,
        fractional_indices=fractional_indices,
        fractional_indices_prev=fractional_indices_prev,
        fractional_indices_next=fractional_indices_next,
        unfractional_dates=unfractional_dates,
        unfractional_dates_prev=unfractional_dates_prev,
        unfractional_dates_next=unfractional_dates_next,
        months_with_index=months,
        selected_fractions=[result[0]]
    )
