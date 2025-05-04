from flask import flash, redirect, url_for

from ..models import Savings as SavingsModel
from .. import db
from .finance_collector import Transfer, Withdraw


def handle_transfer(request, current_user, balance):
    transfer_amount_str = request.form.get('transfer-amount')

    if not transfer_amount_str:
        flash('Please enter a transfer amount.', 'error')
        return redirect(url_for('report.home'))

    try:
        transfer_amount = abs(float(transfer_amount_str))
    except ValueError:
        flash('Invalid transfer amount. Please enter a number.', 'error')
        return redirect(url_for('report.home'))

    user_id = current_user.id
    transfer = Transfer(transfer_amount, user_id, balance)

    if transfer.check_input():
        new_transfer = SavingsModel(amount=transfer.amount, user_id=user_id)
        db.session.add(new_transfer)
        db.session.commit()
        flash('Transfer added successfully!', 'success')
    else:
        flash('Failed to add transfer. Please check your input.', 'error')

    return redirect(url_for('report.home'))


def handle_withdraw(request, current_user, total_savings):
    transfer_amount_str = request.form.get('transfer-amount')

    if not transfer_amount_str:
        flash('Please enter a withdrawal amount.', 'error')
        return redirect(url_for('report.home'))

    try:
        transfer_amount = -abs(float(transfer_amount_str))
    except ValueError:
        flash('Invalid withdrawal amount. Please enter a number.', 'error')
        return redirect(url_for('report.home'))

    user_id = current_user.id
    transfer = Withdraw(transfer_amount, user_id, total_savings)

    if transfer.check_input():
        new_transfer = SavingsModel(amount=transfer.amount, user_id=user_id)
        db.session.add(new_transfer)
        db.session.commit()
        flash('Withdrawal added successfully!', 'success')
    else:
        flash('Failed to add transfer. Please check your input.', 'error')

    return redirect(url_for('report.home'))