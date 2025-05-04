from flask import flash

from ..models import Income, Expenses, Planning
from .get_report import get_report_data


def get_user_financial_context(user_id):
    try:
        incomes = Income.query.filter_by(user_id=user_id).all()
        expenses = Expenses.query.filter_by(user_id=user_id).all()
        planning_expenses = Planning.query.filter_by(user_id=user_id).all()

        income_str = "\n".join([f"- {i.name}: €{i.amount} on {i.date} ({i.type})" for i in incomes])
        expense_str = "\n".join([f"- {e.name}: €{e.amount} on {e.date} ({e.type})" for e in expenses])
        planning_str = "\n".join([f"- {p.name}: €{p.amount} planned on {p.date}" for p in planning_expenses])

        report_data = get_report_data()

        return {
            "income_str": income_str,
            "expense_str": expense_str,
            "planning_str": planning_str,
            "total_income": report_data.get('total_income', 0),
            "total_expenses": report_data.get('total_expenses', 0),
            "total_planning": report_data.get('total_planning', 0),
            "balance": report_data.get('balance', 0),
            "total_savings": report_data.get('total_savings', 0),
            "amount_to_cover_planning": report_data.get('amount_to_cover_planning', 0)
        }
    except Exception as e:
        print(f"ERROR: Failed to get financial context for user {user_id}: {e}")
        flash("Could not retrieve your financial data.", "danger")
        return None