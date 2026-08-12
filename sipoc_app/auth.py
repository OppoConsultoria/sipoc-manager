from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from sipoc_app.extensions import db
from sipoc_app.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=True)
            flash(f"Bem-vindo(a), {user.name}!", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("dashboard.home"))

        flash("E-mail ou senha inválidos.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/registro", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.home"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        password2 = request.form.get("password2", "")

        error = None
        if not name or not email or not password:
            error = "Preencha todos os campos."
        elif len(password) < 6:
            error = "A senha deve ter pelo menos 6 caracteres."
        elif password != password2:
            error = "As senhas não coincidem."
        elif User.query.filter_by(email=email).first():
            error = "Já existe uma conta com este e-mail."

        if error:
            flash(error, "danger")
        else:
            user = User(name=name, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("Conta criada com sucesso!", "success")
            return redirect(url_for("dashboard.home"))

    return render_template("auth/register.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("auth.login"))
