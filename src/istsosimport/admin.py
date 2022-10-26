from fileinput import filename
from functools import partial
from flask import g, redirect, url_for, Markup
from flask_admin import Admin, expose, AdminIndexView, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.filters import BaseSQLAFilter


from istsosimport.env import db, FILE_ERROR_DIRECTORY
from istsosimport.db.models import Import, Procedure


# https://github.com/flask-admin/flask-admin/issues/1807
# https://stackoverflow.com/questions/54638047/correct-way-to-register-flask-admin-views-with-application-factory
class ReloadingIterator:
    def __init__(self, iterator_factory):
        self.iterator_factory = iterator_factory

    def __iter__(self):
        return self.iterator_factory()


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
    list_template = "import-list2.html"
    page_size = 10

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


admin.add_view(ImportView(Import, db.session))
