from flask import flash


class Savings:

    def __init__(self, amount, user_id):
        self.amount = amount
        self.user_id = user_id

    def check_input(self):
        is_empty_str = (
            isinstance(self.amount, str) and not self.amount.strip()
        )
        if self.amount is None or is_empty_str:
            flash('Amount cannot be empty', 'error')
            return False
        try:
            self.amount = float(self.amount)
        except ValueError:
            flash('Amount must be a valid number', 'error')
            return False
        return True


class Transfer(Savings):

    def __init__(self, amount, user_id, balance):
        super().__init__(amount, user_id)
        self.balance = balance

    def check_balance(self):
        if self.amount > self.balance:
            flash('You do not have enough money on your balance', 'error')
            return False
        return True

    def check_input(self):
        if not super().check_input():
            return False
        if not self.check_balance():
            return False
        return True


class Withdraw(Savings):

    def __init__(self, amount, user_id, saving_balance):
        super().__init__(amount, user_id)
        self.saving_balance = saving_balance

    def check_balance(self):
        if self.amount > self.saving_balance:
            flash(
                'You do not have enough money on your saving balance', 'error'
            )
            return False
        return True

    def check_input(self):
        if not super().check_input():
            return False
        if not self.check_balance():
            return False
        return True