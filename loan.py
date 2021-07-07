from dataclasses import dataclass
import pandas as pd
import pickle
import seaborn as sns
from matplotlib import pyplot as plt
import logging

logging.basicConfig(filename='loans.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')


@dataclass
class Loan:
    """this class accepts loan details and returns loan info and schedule ."""
    amount: int  # amount expressed in euros.
    interest: float  # interest expressed in percent.
    term: int  # term in months.
    loan_data: dict = 0  # __post_init__ function after object creation,

    # automatically generates dictionary for dataframe.

    def __post_init__(self):
        save = Loans(self.amount, self.interest, self.term)
        save.lst_to_pkl()

        balance = self.amount
        amount_lst = []
        balance_lst = []
        interest_lst = []
        payment_lst = []

        while balance > 0:
            monthly_amount = round(self.amount / self.term, 2)
            monthly_balance = round(balance - monthly_amount, 2)
            monthly_interest = round((balance * self.interest) / 100 / 12, 2)
            balance = monthly_balance
            monthly_payment = round(monthly_amount + monthly_interest, 2)

            amount_lst.append(monthly_amount)
            balance_lst.append(monthly_balance)
            interest_lst.append(monthly_interest)
            payment_lst.append(monthly_payment)

        numeration = list(range(1, len(amount_lst) + 1))

        self.loan_data = {'Mėn. Nr.': numeration, 'Grąžintina dalis, Eur': amount_lst,
                          'Likutis, Eur': balance_lst,
                          'Priskaičiuotos palūkanos, Eur': interest_lst, 'Bendra Mokėtina suma, Eur': payment_lst}

        logging.info(f"Created loan_data dictionary:{self.loan_data}")

    def loan_info(self):
        name = f'{self.amount}-{self.interest}-{self.term}'
        return name

    def loan_schedule(self):
        data = pd.DataFrame(self.loan_data)

        sns.lineplot(x='Mėn. Nr.', y='Likutis, Eur', data=data)
        try:
            plt.savefig(f'static/likutis{self.loan_info()}.png', dpi=100)
        except FileExistsError:
            pass
        plt.clf()

        sns.lineplot(x='Mėn. Nr.', y='Priskaičiuotos palūkanos, Eur', data=data)
        try:
            plt.savefig(f'static/palukanos{self.loan_info()}.png', dpi=100)
        except FileExistsError:
            pass
        plt.switch_backend('agg')

        data.set_index('Mėn. Nr.', inplace=True)
        data.columns.name = data.index.name
        data.index.name = None
        data.loc['Viso:'] = data.sum(numeric_only=True, axis=0)
        data.loc['Viso:', 'Likutis, Eur'] = self.amount
        data.to_csv(f'static/{self.loan_info()}.csv', index=False)

        logging.info(
            f"Created loan payment schedule with the following data: "
            f"amount:{self.amount} interest:{self.interest} term:{self.term}"
        )

        return data


@dataclass
class Loans:
    amount: int  # amount expressed in euros.
    interest: float  # interest expressed in percent.
    term: int  # term in months.

    def lst_to_pkl(self):
        loan_lst = [self.amount, self.interest, self.term]
        try:
            data = self.pkl_to_lst()
            check = 0
            for lst in data:
                if lst == loan_lst:
                    check += 1
                else:
                    continue
            if check == 0:
                with open("loans", 'ab') as fp:
                    pickle.dump(loan_lst, fp)
                logging.info(f'loan data: {loan_lst} was added to pickle file')
            else:
                logging.info(f'loan data: {loan_lst} are already in pickle file ')
                pass
        except FileNotFoundError:
            with open("loans", 'wb') as fp:
                pickle.dump(loan_lst, fp)
            logging.info('pickle file created')

    @staticmethod
    def pkl_to_lst():
        data = []
        with open("loans", 'rb') as fr:
            try:
                while True:
                    data.append(pickle.load(fr))
            except EOFError:
                pass
        return data
