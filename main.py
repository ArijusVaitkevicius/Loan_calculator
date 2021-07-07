from flask import Flask, render_template, request, redirect, url_for, flash
import os
from forms import LoanForm, EmailForm
from loan import Loan, Loans
from flask_mail import Message, Mail
import logging

logging.basicConfig(filename='loans.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('secret_key')

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USERNAME=os.environ.get('email_name'),
    MAIL_PASSWORD=os.environ.get('email_psw'),
    MAIL_USE_TLS=True
)
mail = Mail(app)


@app.route('/', methods=['GET', 'POST'])
@app.route('/calculator', methods=['GET', 'POST'])
def calculator_page():
    form = LoanForm()
    if form.validate_on_submit():
        loan = Loan(amount=form.amount.data,
                    interest=form.interest.data,
                    term=form.term.data)
        df = loan.loan_schedule()
        name = f'{loan.loan_info()}.png'
        flash('Grafikas sukurtas sėkmingai!', category='success')
        return render_template('graph.html', name=name, tables=[df.to_html(classes='data')],
                               titles=df.columns.values)

    return render_template('calculator.html', form=form)


@app.route('/graph/<txt0>/<txt1>/<txt2>', methods=['GET', 'POST'])
def graph_page(txt0, txt1, txt2):
    if request.method == 'GET':

        amount = int(txt0)
        interest = float(txt1)
        term = int(txt2)

        loan = Loan(amount=amount,
                    interest=interest,
                    term=term)
        df = loan.loan_schedule()

        name = f'{loan.loan_info()}.png'
        return render_template('graph.html', name=name, tables=[df.to_html(classes='data')],
                               titles=df.columns.values)
    else:
        return render_template('graph.html')


@app.route('/query_history')
def query_history_page():
    try:
        loans_lst = Loans.pkl_to_lst()
        items = loans_lst
    except FileNotFoundError:
        items = [[0, 0, 0]]
        flash('Istorija tuščia!', category='warning')

    logging.info(f'User opened query history page.')

    return render_template('query_history.html', items=items)


@app.route('/send_email/<txt0>/<txt1>/<txt2>', methods=['GET', 'POST'])
def send_email(txt0, txt1, txt2):
    csv_name = f'{txt0}-{txt1}-{txt2}.csv'
    png1_name = f'likutis{txt0}-{txt1}-{txt2}.png'
    png2_name = f'palukanos{txt0}-{txt1}-{txt2}.png'
    names = [csv_name, png1_name, png2_name]

    form = EmailForm()
    if form.validate_on_submit():
        msg = Message('Paskolos grafikai', sender='zvirbliukonamai@gmail.com', recipients=[form.email.data])
        msg.body = f'Paskolos grafikai'

        for name in names:
            with app.open_resource(f"static/{name}") as fp:
                msg.attach(f"{name}", "/static", fp.read())

        mail.send(msg)
        flash('Grafikas išsiųstas!', category='success')
        logging.info(f'loan details with data: amount:{txt0} interest:{txt1} term:{txt2}, '
                     f'was sent to email: {form.email.data}.'
                     )
        return redirect(url_for('calculator_page'))
    return render_template('send_email.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
