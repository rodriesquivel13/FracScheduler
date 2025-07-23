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
from utils import (
    regular_fractional_index_maker,
    snow_fractional_index_maker,
    regular_unfractional_dates_list,
    snow_unfractional_dates_list,
    regular_fraction_hunter,
    snow_fraction_hunter,
)
from utils.hollydays import regular_hollydays_dic, snow_hollydays_dic

controllers = Blueprint('controllers', __name__)


def build_months(year, apt_type):
    """
    Devuelve una lista de tuplas (mes, año, matriz) según el tipo de calendario:
    - regular: enero–diciembre del mismo año
    - snow: septiembre (year) → septiembre (year+1)
    """
    display_cal = calendar.Calendar(firstweekday=0)

    if apt_type == "regular":
        return [
            (m, year, display_cal.monthdayscalendar(year, m))
            for m in range(1, 13)
        ]
    else:
        first_part = [
            (m, year, display_cal.monthdayscalendar(year, m))
            for m in range(9, 13)
        ]
        second_part = [
            (m, year + 1, display_cal.monthdayscalendar(year + 1, m))
            for m in range(1, 10)
        ]
        return first_part + second_part


def choose_utils(apartament):
    """
    Según apartament_type, devuelve el trio de funciones adecuadas:
    (index_maker, unfractional_list, fraction_hunter)
    """
    typ = apartament_type.get(apartament, "regular")
    if typ == "snow":
        return (
            snow_fractional_index_maker,
            snow_unfractional_dates_list,
            snow_fraction_hunter,
        )
    return (
        regular_fractional_index_maker,
        regular_unfractional_dates_list,
        regular_fraction_hunter,
    )


@controllers.route('/')
def index():
    year                    = request.args.get('year', 2026, type=int)
    apartament              = request.args.get('apartament', 204, type=int)
    maintenance_path        = apartament_maintenance_path.get(apartament, 1)
    weekday_calendar_starts = apartament_weekday_calendar_starts.get(apartament, 1)

    # Elegimos la lógica (regular vs snow)
    idx_maker, unfract_list, _ = choose_utils(apartament)

    # Calculamos índices fraccionales actual, previo y siguiente
    fractional_indices      = idx_maker(year, weekday_calendar_starts, maintenance_path)
    fractional_indices_prev = idx_maker(year - 1, weekday_calendar_starts, maintenance_path)
    fractional_indices_next = idx_maker(year + 1, weekday_calendar_starts, maintenance_path)

    # Calculamos fechas sin fracción
    unf_dates      = unfract_list(year, weekday_calendar_starts, maintenance_path)
    unf_dates_prev = unfract_list(year - 1, weekday_calendar_starts, maintenance_path)
    unf_dates_next = unfract_list(year + 1, weekday_calendar_starts, maintenance_path)

    # Tipo y rango de meses dinámico
    apt_type          = apartament_type.get(apartament, "regular")
    months_with_index = build_months(year, apt_type)

    # Diciembre previo (solo para regular)
    display_cal       = calendar.Calendar(firstweekday=0)
    previous_december = display_cal.monthdayscalendar(year - 1, 12)
    day_names         = [calendar.day_abbr[i] for i in range(7)]

    # Fracciones seleccionadas
    selected = request.args.getlist('fractions', type=str)
    if 'all' in selected:
        selected = list(range(8)) + ['unfractional', 'all']
    else:
        selected = [int(f) if f.isdigit() else f for f in selected]
    if 'unfractional' not in selected:
        unf_dates = unf_dates_prev = unf_dates_next = []

    # Festivos dorados según tipo de calendario
    if apt_type == "snow":
        golden_holidays = set(snow_hollydays_dic(year).keys())
    else:
        golden_holidays = set(regular_hollydays_dic(year).keys())

    return render_template(
        'calendar.html',
        year=year,
        apt_type=apt_type,
        apartament=apartament,
        available_apartaments=sorted(apartament_maintenance_path.keys()),
        day_names=day_names,
        calendar=calendar,
        fraction_colors=[
            "#CC00CC", "#ADD8E6", "#4472C4", "#FF7514",
            "#C00000", "#CCA9DD", "#00B050", "#FFE5B4"
        ],
        datetime=datetime,
        months_with_index=months_with_index,
        previous_december=previous_december,
        fractional_indices=fractional_indices,
        fractional_indices_prev=fractional_indices_prev,
        fractional_indices_next=fractional_indices_next,
        unfractional_dates=unf_dates,
        unfractional_dates_prev=unf_dates_prev,
        unfractional_dates_next=unf_dates_next,
        selected_fractions=selected,
        golden_holidays=golden_holidays,
    )


@controllers.route('/generate_pdf')
def generate_pdf():
    start_year              = request.args.get('start_year', type=int)
    end_year                = request.args.get('end_year',   type=int)
    apartament              = request.args.get('apartament', 204, type=int)
    maintenance_path        = apartament_maintenance_path.get(apartament, 1)
    weekday_calendar_starts = apartament_weekday_calendar_starts.get(apartament, 1)

    idx_maker, _, _ = choose_utils(apartament)

    sel = request.args.getlist('fractions', type=str)
    sel = [int(f) if f.isdigit() else f for f in sel]

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    y = 750
    c.drawString(100, y, f"Usage dates for fractions: {', '.join(map(str, sel))}")
    y -= 20

    for yr in range(start_year, end_year + 1):
        frac_idx = idx_maker(yr, weekday_calendar_starts, maintenance_path)
        c.drawString(100, y, f"Year {yr}")
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
    date_str                = request.args.get('hunter_date')
    apartament              = request.args.get('apartament', 204, type=int)
    maintenance_path        = apartament_maintenance_path.get(apartament, 1)
    weekday_calendar_starts = apartament_weekday_calendar_starts.get(apartament, 1)

    if not date_str:
        return "No date provided", 400

    _, _, hunter = choose_utils(apartament)

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

    idx_maker, unfract_list, _ = choose_utils(apartament)
    frac_idx      = idx_maker(wish.year, weekday_calendar_starts, maintenance_path)
    frac_idx_prev = idx_maker(wish.year - 1, weekday_calendar_starts, maintenance_path)
    frac_idx_next = idx_maker(wish.year + 1, weekday_calendar_starts, maintenance_path)

    unf_dates      = unfract_list(wish.year, weekday_calendar_starts, maintenance_path)
    unf_dates_prev = unfract_list(wish.year - 1, weekday_calendar_starts, maintenance_path)
    unf_dates_next = unfract_list(wish.year + 1, weekday_calendar_starts, maintenance_path)

    apt_type          = apartament_type.get(apartament, "regular")
    months_with_index = build_months(wish.year, apt_type)

    display_cal       = calendar.Calendar(firstweekday=0)
    previous_december = display_cal.monthdayscalendar(wish.year - 1, 12)
    day_names         = [calendar.day_abbr[i] for i in range(7)]

    # Festivos dorados para el año buscado
    if apt_type == "snow":
        golden_holidays = set(snow_hollydays_dic(wish.year).keys())
    else:
        golden_holidays = set(regular_hollydays_dic(wish.year).keys())

    return render_template(
        'calendar.html',
        year=wish.year,
        apt_type=apt_type,
        apartament=apartament,
        available_apartaments=sorted(apartament_maintenance_path.keys()),
        day_names=day_names,
        calendar=calendar,
        fraction_colors=[
            "#CC00CC", "#ADD8E6", "#4472C4", "#FF7514",
            "#C00000", "#CCA9DD", "#00B050", "#FFE5B4"
        ],
        datetime=datetime,
        months_with_index=months_with_index,
        previous_december=previous_december,
        fractional_indices=frac_idx,
        fractional_indices_prev=frac_idx_prev,
        fractional_indices_next=frac_idx_next,
        unfractional_dates=unf_dates,
        unfractional_dates_prev=unf_dates_prev,
        unfractional_dates_next=unf_dates_next,
        selected_fractions=[result[0]],
        golden_holidays=golden_holidays,
    )
