import click
import uuid

from flask import request, redirect, url_for, Blueprint, render_template
from flask.views import View
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash
from werkzeug.exceptions import Forbidden, BadRequest

from istsosimport.config.config_parser import config
from istsosimport.env import oidc, db
from istsosimport.db.models import User, Role
from istsosimport.forms import LoginForm

blueprint = Blueprint("auth", __name__)


class LoginOIDCView(View):
    def dispatch_request(self):
        if oidc.user_loggedin:
            info = oidc.user_getinfo(["preferred_username", "email", "sub", "user_group"])
            if config["OIDC_FILTER_VALUES"]:
                user_info = oidc.user_getinfo([config["OICD_FILTER_ATTRIBUTE"]])
                if not config["OICD_FILTER_ATTRIBUTE"] in user_info:
                    raise BadRequest(f"The key {config['OICD_FILTER_ATTRIBUTE']} does not exist in the returned token ")
                if not set(user_info[config["OICD_FILTER_ATTRIBUTE"]]) & set(config["OIDC_FILTER_VALUES"]):
                    raise Forbidden("User is not allowed to access to this app")
            user = User.query.filter_by(user_uuid=info["sub"]).one_or_none()
            if user is None:
                user = User(user_uuid=info["sub"], email=info["email"])
                user.role = Role.query.filter_by(name="USER").one()
                db.session.add(user)
                db.session.commit()
            elif user.role is None:
                user.role = Role.query.filter_by(name="USER").one()
                db.session.commit()
            login_user(user)
            next = request.args.get("next")
            return redirect(next or url_for("import.edit_view"))
        return oidc.redirect_to_auth_server(request.url)


class LogoutOIDCView(View):
    def dispatch_request(self):
        oidc.logout()
        logout_user()
        return redirect(url_for("main.home"))



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


# commandes
@blueprint.cli.command()
def add_admin_user():
    user = User.query.filter_by(login="admin").one_or_none()
    if user is None:
        new_user = User(
            login="admin",
            user_uuid=str(uuid.uuid4()),
            pwd=generate_password_hash("admin"),
            email="email@tochange.com",
        )
        new_user.role = Role.query.filter_by(name="ADMIN").one()
        db.session.add(new_user)
        db.session.commit()
        click.secho("Successufully create an Admin user", fg="green")
        return
    elif user.role.name == "ADMIN":
        click.secho("A user call admin already exist and is a 'admin' role", fg="green")
    else:
        user.role = Role.query.filter_by(name="ADMIN").one()
        db.session.commit()
        click.secho("Add 'ADMIN' role for user 'Admin'", fg="green")


@blueprint.cli.command()
@click.argument("user_uuid", required=True)
def set_admin(user_uuid):
    user = User.query.filter_by(user_uuid=user_uuid).one_or_none()
    if not user:
        click.secho(f"No user found for uuid : {user_uuid}", fg="red")
        return
    user.role = Role.query.filter_by(name="ADMIN").one()
    db.session.commit()
    click.echo(f"\U0001F4A5 Successfully add role ADMIN for {user.email} \U0001F4A5")