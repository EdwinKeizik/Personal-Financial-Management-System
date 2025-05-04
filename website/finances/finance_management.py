from flask import flash
from datetime import datetime


class Income:

    def __init__(self, amount, name, date, type, user_id):
        self.amount = amount
        self.name = name
        self.date = date
        self.type = type
        self.user_id = user_id

    def check_input(self):
        if not self.amount:
            flash('Amount cannot be empty', 'error')
            return False
        try:
            self.amount = float(self.amount)
        except ValueError:
            flash('Amount must be a valid number', 'error')
            return False
        else:
            if self.amount <= 0:
                flash('Amount must be greater than 0', 'error')
                return False

        if not self.name:
            flash('Name cannot be empty', 'error')
            return False
        if len(self.name) < 3:
            flash('Name must be at least 3 characters long', 'error')
            return False

        if not self.check_date():
            return False

        return True

    def check_date(self):
        if not self.date:
            flash('Date cannot be empty', 'error')
            return False
        try:
            if isinstance(self.date, str):
                self.date = datetime.strptime(self.date, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
            return False
        if  self.date > datetime.now().date():
            flash('Date cannot be in the future', 'error')
            return False
        return True


class Expenses(Income):
    pass


class Planning(Income):

    def check_date(self):
        if not self.date:
            flash('Date cannot be empty', 'error')
            return False
        try:
            if isinstance(self.date, str):
                self.date = datetime.strptime(self.date, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
            return False
        if not isinstance(self.date, datetime.date) or self.date < datetime.now().date():
            flash('Date cannot be in the past', 'error')
            return False
        return True