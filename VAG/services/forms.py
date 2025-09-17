from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField , SubmitField, TextAreaField,SelectField ,PasswordField
from wtforms.validators import DataRequired, Length , Optional




class ServiceForm(FlaskForm):
    name = StringField("Service Name", validators=[DataRequired(), Length(max=50)])
    description = TextAreaField("Description", validators=[DataRequired(), Length(max=150)])
    icon = FileField("Upload Image", validators=[FileAllowed(['jpg', 'png'])])
    is_private = SelectField("Service Type", choices=[("0", "Public"), ("1", "Private")], validators=[DataRequired()])
    join_password = PasswordField("Password", validators=[Optional()])
    invite_code = StringField("Invite Code", validators=[Optional(), Length(max=32)])
    submit = SubmitField("Create")
    generate_code = SubmitField("Generate Invite Code")

class ServiceUpdateForm(ServiceForm):
    icon = FileField("Upload Image", validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField("Update")

class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')

class JoinForm(FlaskForm):
    password = PasswordField("Enter Service Password", validators=[DataRequired()])
    submit = SubmitField("Join Private Service")

class InviteCodeForm(FlaskForm):
    invite_code = StringField("Invite Code", validators=[DataRequired()])
    submit = SubmitField("Join with Code")

class JoinByCodeForm(FlaskForm):
    invite_code = StringField("Invite Code", validators=[DataRequired(), Length(max=32)])
    submit = SubmitField("Join Service")

class GenerateInviteForm(FlaskForm):
    submit = SubmitField("Generate Invite Code")

class LeaveForm(FlaskForm):
    submit = SubmitField("Quit Service")

class PublicJoinForm(FlaskForm):
    submit = SubmitField("Join Service")
