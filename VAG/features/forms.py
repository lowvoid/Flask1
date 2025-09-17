from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms import StringField , SubmitField
from flask_ckeditor import CKEditorField
from wtforms.validators import DataRequired, Length
from VAG.models import Service




def choice_query():
    return Service.query


class FeaturesForm(FlaskForm):
    service = QuerySelectField('Service', query_factory=choice_query, get_label="name")
    title = StringField("Title", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired(), Length(max=32)],
                       render_kw={"placeholder": "Short version of your title (SEO friendly)"})
    content = CKEditorField("Content", validators=[DataRequired()])
    thumbnail = FileField("Upload Image", validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField("Post")


class FeatureUpdateForm(FeaturesForm):
    thumbnail = FileField("Upload Image", validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField("Update")

class DeleteForm(FlaskForm):
    submit = SubmitField("Delete")

