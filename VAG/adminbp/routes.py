from flask import Blueprint
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from VAG import admin , db , bcrypt
from VAG.models import User, Feature ,Service , Contact
from flask_admin import AdminIndexView
adminbp = Blueprint('adminbp', __name__)

class UsermodelView(ModelView):
    def on_model_change(self, form, model, is_created):
        if hasattr(form, 'password') and form.password.data:
            model.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

    def is_accessible(self):
        return current_user.is_authenticated and current_user.id == 1

class ServicemodelView(ModelView):
    def on_model_change(self, form, model, is_created):
        if hasattr(form, 'join_password') and form.join_password.data:
            model.join_password = bcrypt.generate_password_hash(
                form.join_password.data
            ).decode('utf-8')
            
    def is_accessible(self):
        return current_user.is_authenticated and current_user.id == 1



class MymodelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.id == 1

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.id == 1

admin.add_view(UsermodelView(User,db.session))
admin.add_view(MymodelView(Feature,db.session))
admin.add_view(ServicemodelView(Service,db.session))
admin.add_view(MymodelView(Contact,db.session))
