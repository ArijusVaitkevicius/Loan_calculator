from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, FloatField, StringField
from wtforms.validators import DataRequired, NumberRange, Email


class LoanForm(FlaskForm):
    amount = IntegerField(label="Įveskite paskolos sumą:",
                          validators=[DataRequired(),
                                      NumberRange(min=100, max=100000,
                                                  message='Galima paskolos suma nuo 100 iki 100 000 eur. ')])
    interest = FloatField(label="Įveskite paskolos palūkanų normą:",
                          validators=[DataRequired(),
                                      NumberRange(min=1, max=100,
                                                  message='Galima paskolos palūkanų norma nuo 1 iki 100 proc. ')])
    term = IntegerField(label="Įveskite paskolos terminą mėnesiais:",
                        validators=[DataRequired(),
                                    NumberRange(min=1, max=600,
                                                message='Galima paskolos terminas nuo 1 iki 600 mėn. ')])
    submit = SubmitField(label='Skaičiuoti paskolą')


class EmailForm(FlaskForm):
    email = StringField(label='El. pašto adresas:', validators=[Email(message='Neteisingas el.pašto adresas.')])
    submit = SubmitField(label='Siųsti')
