from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from datetime import datetime

from .filters import filter_reports
from .finances.submit_finances import process_form_submission
from .finances.delete_finances import process_delete_request

views = Blueprint("views", __name__)


@views.route("/", methods=["GET", "POST"])
@login_required
def home():
    if request.method == "POST":
        process_form_submission(request, current_user)
        process_delete_request(request, current_user)

    amount_query = request.args.get("Fprice")
    name_query = request.args.get("Fname")
    date_str = request.args.get("Fdate")
    report_type = request.args.get("Ftype")
    date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else None

    filtered_reports = filter_reports(
        user_id=current_user.id,
        amount_query=amount_query,
        name_query=name_query,
        date=date,
        report_type=report_type,
    )

    return render_template(
        "index.html",
        user=current_user,
        income=filtered_reports["income"],
        expenses=filtered_reports["expenses"],
        planning=filtered_reports["planning"],
    )