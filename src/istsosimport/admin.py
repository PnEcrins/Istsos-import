from fileinput import filename
from functools import partial
from flask import g, redirect, url_for, flash
from markupsafe import Markup
from flask_admin import Admin, expose, AdminIndexView, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.filters import BaseSQLAFilter
from flask_login import current_user
from werkzeug.security import generate_password_hash
from wtforms import PasswordField
from wtforms.validators import InputRequired

from istsosimport.env import db, FILE_ERROR_DIRECTORY
from istsosimport.db.models import Import, Procedure
from istsosimport.config.config_parser import config
from pypnusershub.db.models import User


# https://github.com/flask-admin/flask-admin/issues/1807
# https://stackoverflow.com/questions/54638047/correct-way-to-register-flask-admin-views-with-application-factory
class ReloadingIterator:
    def __init__(self, iterator_factory):
        self.iterator_factory = iterator_factory

    def __iter__(self):
        return self.iterator_factory()


class HomeView(BaseView):
    def is_visible(self):
        # This view won't appear in the menu structure
        return False

    @expose("/")
    def index(self):
        return redirect(url_for("import.edit_view"))


admin = Admin(
    name="istSOS-import",
    template_mode="bootstrap4",
    url="/",
    index_view=HomeView(),
)


class ImportFiltersProcedure(BaseSQLAFilter):
    def apply(self, query, value, alias=None):
        return query.filter(Import.id_prc == value)

    def operation(self):
        return "equals"

    def get_dynamic_options(self, view):
        yield from [
            (proc.id_prc, proc.name_prc)
            for proc in Procedure.query.order_by(Procedure.name_prc)
        ]

    def get_options(self, view):
        return ReloadingIterator(partial(self.get_dynamic_options, view))


class ImportView(ModelView):
    can_edit = False
    can_create = False
    can_view_details = True
    list_template = "import-list.html"
    page_size = 10

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("auth.login", provider=config["AUTHENTICATION"]["DEFAULT_PROVIDER_ID"]))

    @property
    def column_list(self):
        return ("id_import", *self.scaffold_list_columns())

    column_exclude_list = ("service", "delimiter", "email")
    column_filters = [
        ImportFiltersProcedure(column=None, name="Procedure"),
        "date_import",
    ]

    def _file_error_formater(view, context, model, name):
        if (
            model.nb_row_total is not None
            and model.nb_row_inserted is not None
            and (model.nb_row_total > model.nb_row_inserted)
        ):
            url = url_for("static", filename="error_files/" + model.error_file)
            markupstring = (
                f" <a href='{url}'> Download <i class='bi bi-download'></i> </a>"
            )
            return Markup(markupstring)
        else:
            return ""

    column_formatters = {"error_file": _file_error_formater}


admin.add_view(ImportView(Import, db.session, "Imports"))


# class CustomPasswordField(
#     PasswordField
# ):  # If you don't want hide the password you can use a StringField
#     def populate_obj(self, obj, name):
#         setattr(obj, name, generate_password_hash(self.data))  # Password function


# class UserView(ModelView):
#     can_edit = True
#     can_create = True
#     column_exclude_list = "pwd"
#     form_excluded_columns = "user_uuid"
#     form_extra_fields = {
#         "pwd": CustomPasswordField("Password", validators=[InputRequired()]),
#         "verified_password": PasswordField(validators=[InputRequired()]),
#     }

#     def is_accessible(self):
#         return current_user.is_authenticated and current_user.role.name == "ADMIN"

#     def validate_form(self, form):
#         """Custom validation code that checks dates"""
#         if form.pwd.data != form.verified_password.data:
#             flash("Password are not the same", "error")
#             return False
#         return super(UserView, self).validate_form(form)


# admin.add_view(UserView(User, db.session, "Users"))
