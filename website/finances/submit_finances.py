from flask import flash

from ..models import Income as IncomeModel
from ..models import Expenses as ExpensesModel
from ..models import Planning as PlanningModel
from .finance_management import Income as IncomeClass
from .finance_management import Expenses as ExpensesClass
from .finance_management import Planning as PlanningClass
from .. import db


def process_form_submission(request, current_user):
    submit = request.form.get('submit')

    amount = None
    name = None
    date = None
    item_type = None
    ItemClass = None
    ItemModel = None

    if submit == 'income':
        amount = request.form.get('amountI')
        name = request.form.get('nameI')
        date = request.form.get('dateI')
        item_type = "Income"
        ItemClass = IncomeClass
        ItemModel = IncomeModel
    elif submit == 'expenses':
        amount = request.form.get('amountE')
        name = request.form.get('nameE')
        date = request.form.get('dateE')
        item_type = "Expenses"
        ItemClass = ExpensesClass
        ItemModel = ExpensesModel
    elif submit == 'planning':
        amount = request.form.get('amountP')
        name = request.form.get('nameP')
        date = request.form.get('dateP')
        item_type = "Planning"
        ItemClass = PlanningClass
        ItemModel = PlanningModel
    else:
        return False

    item = ItemClass(amount, name, date, item_type, current_user.id)

    if item.check_input():
        new_item = ItemModel(
            amount=item.amount,
            name=item.name,
            date=item.date,
            type=item.type,
            user_id=current_user.id,
        )
        db.session.add(new_item)
        db.session.commit()
        flash(f'{item_type} added successfully!', 'success')
    else:
        flash(f'Failed to add {item_type}. Please check your input.', 'error')


    return True