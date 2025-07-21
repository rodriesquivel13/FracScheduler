# controllers.py
from flask import Blueprint, render_template, request, send_file
import calendar
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from models import (
    apartament_maintenance_path,
    apartament_weekday_calendar_starts,
    apartament_type,
)

# importamos ambas lógicas desde utils
from utils import (
    regular_fractional_index_maker,
    snow_fractional_index_maker,
    regular_unfractional_dates_list,
    snow_unfractional_dates_list,
    regular_fraction_hunter,
    snow_fraction_hunter,
)

controllers = Blueprint('controllers', __name__)

def choose_utils(apartment):
    """
    Según el tipo de apartamento, devolvemos 
    las tres funciones correctas: index_maker, unfract_list, hunter.
    """
    typ = apartament_type.get(apartment, "regular")
    if typ == "snow":
        return (
            snow_fractional_index_maker,
            snow_unfractional_dates_list,
            snow_fraction_hunter,
        )
    # por defecto 'regular'
    return (
        regular_fractional_index_maker,
        regular_unfractional_dates_list,
        regular_fraction_hunter,
    )

@controllers.route('/')
def index():
    year     = request.args.get('year', 2026, type=int)
    apart    = request.args.get('apartament', 204, type=int)
    maintenance_path       = apartament_maintenance_path.get(apart, 1)
    weekday_calendar_starts = apartament_weekday_calendar_starts.get(apart, 1)

    # Elegimos las 3 funciones según el tipo
    idx_maker, unfract_list, _ = choose_utils(apart)

    # Preparamos índices y listas para año actual, previo y siguiente
    fractional_indices      = idx_maker(year, weekday_calendar_starts, maintenance_path)
    fractional_indices_prev = idx_maker(year - 1, weekday_calendar_starts, maintenance_path)
    fractional_indices_next = idx_maker(year + 1, weekday_calendar_starts, maintenance_path)

    unf_dates      = unfract_list(year, weekday_calendar_starts, maintenance_path)
    unf_dates_prev = unfract_list(year - 1, weekday_calendar_starts, maintenance_path)
    unf_dates_next = unfract_list(year + 1, weekday_calendar_starts, maintenance_path)

    display_cal       = calendar.Calendar(firstweekday=0)
    months            = [display_cal.monthdayscalendar(year, m) for m in range(1, 13)]
    previous_december = display_cal.monthdayscalendar(year - 1, 12)
    day_names         = [calendar.day_abbr[i] for i in range(7)]

    # Fracciones seleccionadas por el usuario
    selected = request.args.getlist('fractions', type=str)
    if 'all' in selected:
        selected = list(range(8)) + ['unfractional', 'all']
    else:
        selected = [int(f) if f.isdigit() else f for f in selected]
    if 'unfractional' not in selected:
        unf_dates = unf_dates_prev = unf_dates_next = []

    return render_template(
        'calendar.html',
        year=year,
        months_with_index=list(enumerate(months)),
        apartament=apart,
        available_apartaments=sorted(list(apartament_maintenance_path.keys())),
        day_names=day_names,
        calendar=calendar,
        fraction_colors=[
            "#CC00CC", "#ADD8E6", "#4472C4", "#FF7514",
            "#C00000", "#CCA9DD", "#00B050", "#FFE5B4"
        ],
        datetime=datetime,
        fractional_indices=fractional_indices,
        fractional_indices_prev=fractional_indices_prev,
        fractional_indices_next=fractional_indices_next,
        unfractional_dates=unf_dates,
        unfractional_dates_prev=unf_dates_prev,
        unfractional_dates_next=unf_dates_next,
        previous_december=previous_december,
        selected_fractions=selected
    )

@controllers.route('/generate_pdf')
def generate_pdf():
    start_year = request.args.get('start_year', type=int)
    end_year   = request.args.get('end_year',   type=int)
    apart      = request.args.get('apartament', 204, type=int)
    maintenance_path       = apartament_maintenance_path.get(apart, 1)
    weekday_calendar_starts = apartament_weekday_calendar_starts.get(apart, 1)

    # sólo necesitamos el maker en el PDF
    idx_maker, _, _ = choose_utils(apart)

    sel = request.args.getlist('fractions', type=str)
    sel = [int(f) if f.isdigit() else f for f in sel]

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    y = 750
    c.drawString(100, y, f"Usage dates for fractions: {', '.join(map(str, sel))}")
    y -= 20

    for year in range(start_year, end_year + 1):
        frac_idx = idx_maker(year, weekday_calendar_starts, maintenance_path)
        c.drawString(100, y, f"Year {year}")
        y -= 20
        for date, frac in frac_idx.items():
            if frac[0] in sel:
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
    apart    = request.args.get('apartament', 204, type=int)
    maintenance_path       = apartament_maintenance_path.get(apart, 1)
    weekday_calendar_starts = apartament_weekday_calendar_starts.get(apart, 1)

    if not date_str:
        return "No date provided", 400

    # elegimos el hunter correcto
    _, _, hunter = choose_utils(apart)

    try:
        wish = datetime.strptime(date_str, "%Y-%m-%d")
        result = hunter(
            wish.year, wish.month, wish.day,
            weekday_calendar_starts, maintenance_path
        )
    except ValueError:
        return "Invalid date format", 400

    if isinstance(result, str):
        return result, 404

    # Como en index(), recalculamos para pintar
    idx_maker, unfract_list, _ = choose_utils(apart)
    frac_idx      = idx_maker(wish.year, weekday_calendar_starts, maintenance_path)
    frac_idx_prev = idx_maker(wish.year - 1, weekday_calendar_starts, maintenance_path)
    frac_idx_next = idx_maker(wish.year + 1, weekday_calendar_starts, maintenance_path)

    unf_dates      = unfract_list(wish.year, weekday_calendar_starts, maintenance_path)
    unf_dates_prev = unfract_list(wish.year - 1, weekday_calendar_starts, maintenance_path)
    unf_dates_next = unfract_list(wish.year + 1, weekday_calendar_starts, maintenance_path)

    display_cal       = calendar.Calendar(firstweekday=0)
    months            = [(i, display_cal.monthdayscalendar(wish.year, i + 1)) for i in range(12)]
    previous_december = display_cal.monthdayscalendar(wish.year - 1, 12)
    day_names         = [calendar.day_abbr[i] for i in range(7)]

    return render_template(
        'calendar.html',
        year=wish.year,
        apartament=apart,
        available_apartaments=sorted(list(apartament_maintenance_path.keys())),
        day_names=day_names,
        calendar=calendar,
        fraction_colors=[
            "#CC00CC", "#ADD8E6", "#4472C4", "#FF7514",
            "#C00000", "#CCA9DD", "#00B050", "#FFE5B4"
        ],
        datetime=datetime,
        previous_december=previous_december,
        fractional_indices=frac_idx,
        fractional_indices_prev=frac_idx_prev,
        fractional_indices_next=frac_idx_next,
        unfractional_dates=unf_dates,
        unfractional_dates_prev=unf_dates_prev,
        unfractional_dates_next=unf_dates_next,
        months_with_index=months,
        selected_fractions=[result[0]]
    )
