from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField,TextAreaField
from wtforms.validators import DataRequired,Length


class Post(FlaskForm):
    title=StringField("Title",validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    submit=SubmitField("Post")
    
class RegistrationForm(FlaskForm):
    username=StringField("Username",validators=[DataRequired(),Length(min=3,max=25)])
    password=PasswordField("Password",validators=[DataRequired(),Length(min=6)])
    submit=SubmitField("Register")
    
class LoginForm(FlaskForm):
    username=StringField("Username",validators=[DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    submit=SubmitField("Login")
    
    