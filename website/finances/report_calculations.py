from ..models import Income as IncomeModel
from ..models import Expenses as ExpensesModel
from ..models import Planning as PlanningModel
from ..models import Savings as SavingsModel


def get_financial_data(user_id):
    income = IncomeModel.query.filter_by(user_id=user_id).all()
    expenses = ExpensesModel.query.filter_by(user_id=user_id).all()
    planning = PlanningModel.query.filter_by(user_id=user_id).all()
    savings = SavingsModel.query.filter_by(user_id=user_id).all()
    return income, expenses, planning, savings


def calculate_totals(income, expenses, planning, savings):
    total_income = sum(i.amount for i in income)
    total_expenses = sum(e.amount for e in expenses)
    total_planning = sum(p.amount for p in planning)
    total_savings = sum(s.amount for s in savings)
    return total_income, total_expenses, total_planning, total_savings


def calculate_balance_and_coverage(
    total_income, total_expenses, total_savings, total_planning
):
    balance = total_income - total_expenses - total_savings
    cover = total_planning - balance
    if cover <= 0:
        cover = "0.00 You can cover all your planning expenses."
    return balance, cover


def get_period_data(
    income, expenses, planning,
    Istart_date, Iend_date,
    Estart_date, Eend_date,
    Pstart_date, Pend_date
):
    period_income = []
    if Istart_date and Iend_date:
        period_income = [
            i for i in income if Istart_date <= i.date <= Iend_date
        ]

    period_expenses = []
    if Estart_date and Eend_date:
        period_expenses = [
            e for e in expenses if Estart_date <= e.date <= Eend_date
        ]

    period_planning = []
    if Pstart_date and Pend_date:
        period_planning = [
            p for p in planning if Pstart_date <= p.date <= Pend_date
        ]

    return period_income, period_expenses, period_planning


def calculate_period_totals(period_income, period_expenses, period_planning):
    total_period_income = sum(i.amount for i in period_income)
    total_period_expenses = sum(e.amount for e in period_expenses)
    total_period_planning = sum(p.amount for p in period_planning)
    return total_period_income, total_period_expenses, total_period_planning