from flask import g, redirect, url_for
from flask_admin import Admin, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView

from istsosimport.env import db
from istsosimport.db.models import Import


class HomeView(AdminIndexView):
    @expose("/")
    def index(self):
        return redirect(url_for("import.edit_view"))


admin = Admin(
    name="Istsos-import",
    template_mode="bootstrap4",
    # url="/",
    index_view=HomeView(),
)


class ImportView(ModelView):
    can_edit = False
    can_create = False
    can_view_details = True
    list_template = "import-list2.html"
    page_size = 10


admin.add_view(ImportView(Import, db.session))
