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

controllers = Blueprint('controllers', __name__)

# Colores para las fracciones
fraction_colors = [
    "#CC00CC",  # 0
    "#ADD8E6",  # 1
    "#4472C4",  # 2
    "#B3DE99",  # 3
    "#C00000",  # 4
    "#DDA0DD",  # 5
    "#00B050",  # 6
    "#FFE5B4"   # 7
]

@controllers.route('/')
def index():
    year = request.args.get('year', 2026, type=int)
    user_selected_start = request.args.get('start_day', 1, type=int)

    # Lógica interna: fracciones y unfractional para año -1, actual y +1
    fractional_indices      = fractional_index_maker(year, user_selected_start)
    fractional_indices_prev = fractional_index_maker(year - 1, user_selected_start)
    fractional_indices_next = fractional_index_maker(year + 1, user_selected_start)

    unfractional_dates      = unfractional_dates_list(year, user_selected_start)
    unfractional_dates_prev = unfractional_dates_list(year - 1, user_selected_start)
    unfractional_dates_next = unfractional_dates_list(year + 1, user_selected_start)

    # Vista fija de lunes a domingo
    display_cal      = calendar.Calendar(firstweekday=0)
    months           = [display_cal.monthdayscalendar(year,   m) for m in range(1,13)]
    previous_december = display_cal.monthdayscalendar(year - 1, 12)

    day_names = [calendar.day_abbr[i] for i in range(7)]

    # Fracciones seleccionadas
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
        start_day=user_selected_start,
        day_names=day_names,
        calendar=calendar,
        fraction_colors=fraction_colors,
        datetime=datetime,
        # Lógica interna
        fractional_indices=fractional_indices,
        fractional_indices_prev=fractional_indices_prev,
        fractional_indices_next=fractional_indices_next,
        unfractional_dates=unfractional_dates,
        unfractional_dates_prev=unfractional_dates_prev,
        unfractional_dates_next=unfractional_dates_next,
        # Vista fija
        previous_december=previous_december,
        selected_fractions=selected_fractions
    )


@controllers.route('/generate_pdf')
def generate_pdf():
    start_year = request.args.get('start_year', type=int)
    end_year   = request.args.get('end_year', type=int)
    start_day  = request.args.get('start_day', 0, type=int)
    selected_fractions = request.args.getlist('fractions', type=str)
    selected_fractions = [int(f) if f.isdigit() else f for f in selected_fractions]

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    y = 750
    c.drawString(100, y, f"Fechas de uso para fracciones: {', '.join(map(str, selected_fractions))}")
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
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"fracciones_{start_year}_{end_year}.pdf",
        mimetype='application/pdf'
    )


@controllers.route('/hunt_fraction')
def hunt_fraction():
    date_str = request.args.get('hunter_date')
    user_selected_start = request.args.get('start_day', 1, type=int)

    if not date_str:
        return "No date provided", 400

    try:
        wishful_date = datetime.strptime(date_str, "%Y-%m-%d")
        result = fraction_hunter(
            wishful_date.year,
            wishful_date.month,
            wishful_date.day,
            user_selected_start
        )
    except ValueError:
        return "Invalid date format", 400

    if isinstance(result, str):
        return result, 404

    # Lógica interna para los tres años
    fractional_indices      = fractional_index_maker(wishful_date.year, user_selected_start)
    fractional_indices_prev = fractional_index_maker(wishful_date.year - 1, user_selected_start)
    fractional_indices_next = fractional_index_maker(wishful_date.year + 1, user_selected_start)

    unfractional_dates      = unfractional_dates_list(wishful_date.year, user_selected_start)
    unfractional_dates_prev = unfractional_dates_list(wishful_date.year - 1, user_selected_start)
    unfractional_dates_next = unfractional_dates_list(wishful_date.year + 1, user_selected_start)

    # Vista fija de lunes a domingo
    display_cal      = calendar.Calendar(firstweekday=0)
    months = [
        (i, display_cal.monthdayscalendar(wishful_date.year, i + 1))
        for i in range(12)
    ]
    previous_december = display_cal.monthdayscalendar(wishful_date.year - 1, 12)
    day_names = [calendar.day_abbr[i] for i in range(7)]

    return render_template(
        'calendar.html',
        year=wishful_date.year,
        start_day=user_selected_start,
        months_with_index=months,
        day_names=day_names,
        calendar=calendar,
        fraction_colors=fraction_colors,
        datetime=datetime,
        previous_december=previous_december,
        # Lógica interna
        fractional_indices=fractional_indices,
        fractional_indices_prev=fractional_indices_prev,
        fractional_indices_next=fractional_indices_next,
        unfractional_dates=unfractional_dates,
        unfractional_dates_prev=unfractional_dates_prev,
        unfractional_dates_next=unfractional_dates_next,
        # Sólo mostramos la fracción hallada
        selected_fractions=[result[0]]
    )
