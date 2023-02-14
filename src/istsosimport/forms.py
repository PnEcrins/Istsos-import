from flask_login import login_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
from werkzeug.security import check_password_hash

from istsosimport.db.models import User


class LoginForm(FlaskForm):
    login = StringField("Login", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])

    def validate_on_submit(self, extra_validators=None):
        form_valid = super().validate_on_submit(extra_validators)
        if form_valid:
            user = User.query.filter_by(login=self.login.data).one_or_none()
            if user is None:
                self.form_errors.append(f"No user with login {self.login.data}")
                return False
            else:
                if check_password_hash(user.pwd, self.password.data):
                    login_user(user)
                    return True
                else:
                    self.form_errors.append(f"Invalid password for user {user.login}")
                    return False
        return False
