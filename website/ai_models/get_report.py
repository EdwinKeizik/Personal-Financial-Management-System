from ..models import Income as IncomeModel, Expenses as ExpensesModel, Planning as PlanningModel, Savings as SavingsModel


def get_report_data():
    income = IncomeModel.query.all()
    expenses = ExpensesModel.query.all()
    planning = PlanningModel.query.all()

    total_income = sum(i.amount for i in income)
    total_expenses = sum(e.amount for e in expenses)
    total_planning = sum(p.amount for p in planning)

    savings = SavingsModel.query.all()

    total_savings = sum(s.amount for s in savings)

    balance = total_income - total_expenses - total_savings

    cover = total_planning - balance

    return {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'total_planning': total_planning,
        'balance': balance,
        'total_savings': total_savings,
        'amount_to_cover_planning': cover
    }