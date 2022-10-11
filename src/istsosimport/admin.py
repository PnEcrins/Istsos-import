from flask import g, redirect, url_for
from flask_admin import Admin, expose, AdminIndexView, BaseView
from flask_admin.contrib.sqla import ModelView

from istsosimport.env import db
from istsosimport.db.models import Import


class HomeView(BaseView):
    @expose("/")
    def index(self):
        return redirect(url_for("import.edit_view"))


admin = Admin(
    name="Istsos-import",
    template_mode="bootstrap4",
    url="/",
    index_view=HomeView(),
)


class ImportView(ModelView):
    can_edit = False
    can_create = False
    can_view_details = True
    list_template = "import-list2.html"
    page_size = 10

    @property
    def column_list(self):
        return ("id_import", *self.scaffold_list_columns())

    column_exclude_list = ["service", "delimiter"]


admin.add_view(ImportView(Import, db.session))
