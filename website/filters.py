from .models import Income, Expenses, Planning


def filter_reports(
    user_id, amount_query=None, name_query=None, date=None, report_type=None
):
    income_query = Income.query.filter_by(user_id=user_id)
    expenses_query = Expenses.query.filter_by(user_id=user_id)
    planning_query = Planning.query.filter_by(user_id=user_id)

    if report_type == "Income":
        expenses_query = expenses_query.filter(Expenses.id == None)
        planning_query = planning_query.filter(Planning.id == None)
    elif report_type == "Expenses":
        income_query = income_query.filter(Income.id == None)
        planning_query = planning_query.filter(Planning.id == None)
    elif report_type == "Planning Expenses":
        income_query = income_query.filter(Income.id == None)
        expenses_query = expenses_query.filter(Expenses.id == None)

    if name_query:
        income_query = income_query.filter(Income.name.like(f"%{name_query}%"))
        expenses_query = expenses_query.filter(Expenses.name.like(f"%{name_query}%"))
        planning_query = planning_query.filter(Planning.name.like(f"%{name_query}%"))

    if date:
        income_query = income_query.filter(Income.date == date)
        expenses_query = expenses_query.filter(Expenses.date == date)
        planning_query = planning_query.filter(Planning.date == date)

    if amount_query:
        income_query = income_query.filter(Income.amount == float(amount_query))
        expenses_query = expenses_query.filter(Expenses.amount == float(amount_query))
        planning_query = planning_query.filter(Planning.amount == float(amount_query))

    income = income_query.all()
    expenses = expenses_query.all()
    planning = planning_query.all()
    return {"income": income, "expenses": expenses, "planning": planning}