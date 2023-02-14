from flask import request, redirect, url_for, Blueprint, render_template
from flask.views import View
from flask_login import login_user, logout_user, login_required

from istsosimport.config.config_parser import config
from istsosimport.env import oidc, db
from istsosimport.db.models import User
from istsosimport.forms import LoginForm

blueprint = Blueprint("auth", __name__)


class LoginOIDCView(View):
    def dispatch_request(self):
        if oidc.user_loggedin:
            info = oidc.user_getinfo(["preferred_username", "email", "sub"])
            user = User.query.filter_by(user_uuid=info["sub"]).one_or_none()
            if not user:
                user = User(user_uuid=info["sub"], email=info["email"])
                db.session.add(user)
                db.session.commit()
            login_user(user)
            next = request.args.get("next")
            return redirect(next or url_for("main.test"))
        return oidc.redirect_to_auth_server(request.url)


class LogoutOIDCView(View):
    def dispatch_request(self):
        oidc.logout()
        logout_user()


class BasicAuthLogin(View):
    def dispatch_request(self):
        form = LoginForm()
        if form.validate_on_submit():
            return redirect(url_for("import.edit_view"))
        return render_template("login.html", form=form)


class BasicAuthLogout(View):
    decorators = (login_required,)

    def dispatch_request(self):
        logout_user()
        return redirect(url_for("auth.login"))


blueprint.add_url_rule(
    "/login",
    view_func=LoginOIDCView.as_view("login")
    if config["OIDC_AUTHENT"]
    else BasicAuthLogin.as_view("login"),
    methods=["GET", "POST"],
)


blueprint.add_url_rule(
    "/logout",
    view_func=LogoutOIDCView.as_view("logout")
    if config["OIDC_AUTHENT"]
    else BasicAuthLogout.as_view("logout"),
)
