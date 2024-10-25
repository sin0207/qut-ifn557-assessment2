from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, StringField, SelectField
from wtforms.widgets import TextArea
from wtforms.validators import InputRequired, email

# form used in basket
class CheckoutForm(FlaskForm):
    first_name = StringField("Your first name", validators=[InputRequired()])
    last_name = StringField("Your last name", validators=[InputRequired()])
    email = StringField("Your email", validators=[InputRequired(), email()])
    phone = StringField("Your phone number", validators=[InputRequired()])
    submit = SubmitField("Submit")

class ContactForm(FlaskForm):
    first_name = StringField("Your first name", validators=[InputRequired()])
    last_name = StringField("Your last name", validators=[InputRequired()])
    email = StringField("Your email", validators=[InputRequired(), email()])
    question_type = SelectField("Question type", choices=["General", "Order", "Product", "Other"], validators=[InputRequired()])
    question = StringField("Your question", validators=[InputRequired()], widget=TextArea())
    submit = SubmitField("Submit")
