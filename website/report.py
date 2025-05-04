from flask import Blueprint, flash, render_template, request
from flask_login import login_required, current_user
from datetime import datetime

from .finances.submit_finances import process_form_submission
from .finances.report_calculations import (
    get_financial_data,
    calculate_totals,
    calculate_balance_and_coverage,
    get_period_data,
    calculate_period_totals,
)
from .finances.savings_handler import handle_transfer, handle_withdraw

report = Blueprint("report", __name__)


@report.route("/report", methods=["GET", "POST"])
@login_required
def home():
    income, expenses, planning, savings = get_financial_data(current_user.id)
    (
        total_income,
        total_expenses,
        total_planning,
        total_savings,
    ) = calculate_totals(income, expenses, planning, savings)
    balance, cover = calculate_balance_and_coverage(
        total_income, total_expenses, total_savings, total_planning
    )
    if request.method == "POST":
        process_form_submission(request, current_user)

        submit = request.form.get("submit")
        if submit == "transfer":
            return handle_transfer(request, current_user, balance)
        elif submit == "withdraw":
            return handle_withdraw(request, current_user, total_savings)


    Istart_date_str = request.args.get("Istart_date")
    Iend_date_str = request.args.get("Iend_date")
    Estart_date_str = request.args.get("Estart_date")
    Eend_date_str = request.args.get("Eend_date")
    Pstart_date_str = request.args.get("Pstart_date")
    Pend_date_str = request.args.get("Pend_date")

    Istart_date = (
        datetime.strptime(Istart_date_str, "%Y-%m-%d").date()
        if Istart_date_str
        else None
    )
    Iend_date = (
        datetime.strptime(Iend_date_str, "%Y-%m-%d").date()
        if Iend_date_str
        else None
    )
    Estart_date = (
        datetime.strptime(Estart_date_str, "%Y-%m-%d").date()
        if Estart_date_str
        else None
    )
    Eend_date = (
        datetime.strptime(Eend_date_str, "%Y-%m-%d").date()
        if Eend_date_str
        else None
    )
    Pstart_date = (
        datetime.strptime(Pstart_date_str, "%Y-%m-%d").date()
        if Pstart_date_str
        else None
    )
    Pend_date = (
        datetime.strptime(Pend_date_str, "%Y-%m-%d").date()
        if Pend_date_str
        else None
    )

    period_income, period_expenses, period_planning = get_period_data(
        income,
        expenses,
        planning,
        Istart_date,
        Iend_date,
        Estart_date,
        Eend_date,
        Pstart_date,
        Pend_date,
    )
    (
        total_period_income,
        total_period_expenses,
        total_period_planning,
    ) = calculate_period_totals(period_income, period_expenses, period_planning)

    return render_template(
        "report.html",
        user=current_user,
        total_income=total_income,
        total_expenses=total_expenses,
        total_planning=total_planning,
        balance=balance,
        cover=cover,
        total_savings=total_savings,
        total_period_income=total_period_income,
        total_period_expenses=total_period_expenses,
        total_period_planning=total_period_planning,
        Istart_date=Istart_date_str,
        Iend_date=Iend_date_str,
        Estart_date=Estart_date_str,
        Eend_date=Eend_date_str,
        Pstart_date=Pstart_date_str,
        Pend_date=Pend_date_str,
    )