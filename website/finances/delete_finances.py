from flask import flash

from ..models import Income as IncomeModel
from ..models import Expenses as ExpensesModel
from ..models import Planning as PlanningModel
from .. import db


def process_delete_request(request, current_user):
    delete = request.form.get('delete')
    if delete:
        delete_parts = delete.split('_')
        delete_type = delete_parts[0]
        delete_id = delete_parts[1]

        report = None
        if delete_type == 'delI':
            report = IncomeModel.query.filter_by(
                id=delete_id, user_id=current_user.id
            ).first()
        elif delete_type == 'delE':
            report = ExpensesModel.query.filter_by(
                id=delete_id, user_id=current_user.id
            ).first()
        elif delete_type == 'delP':
            report = PlanningModel.query.filter_by(
                id=delete_id, user_id=current_user.id
            ).first()

        if report:
            db.session.delete(report)
            db.session.commit()
            flash('Deleted successfully!', 'success')
        else:
            flash('Failed to delete.', 'error')