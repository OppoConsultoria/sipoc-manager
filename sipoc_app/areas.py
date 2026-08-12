from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required

from sipoc_app.extensions import db
from sipoc_app.models import Area, Empresa

areas_bp = Blueprint("areas", __name__, url_prefix="/areas")


@areas_bp.route("/empresa/<int:empresa_id>/novo", methods=["GET", "POST"])
@login_required
def novo(empresa_id):
    empresa = db.get_or_404(Empresa, empresa_id)
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        if not nome:
            flash("Informe o nome da área.", "danger")
        else:
            area = Area(nome=nome, empresa_id=empresa.id)
            db.session.add(area)
            db.session.commit()
            flash("Área cadastrada com sucesso.", "success")
            return redirect(url_for("empresas.visualizar", empresa_id=empresa.id))
    return render_template("areas/form.html", empresa=empresa, area=None)


@areas_bp.route("/<int:area_id>/editar", methods=["GET", "POST"])
@login_required
def editar(area_id):
    area = db.get_or_404(Area, area_id)
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        if not nome:
            flash("Informe o nome da área.", "danger")
        else:
            area.nome = nome
            db.session.commit()
            flash("Área atualizada.", "success")
            return redirect(url_for("empresas.visualizar", empresa_id=area.empresa_id))
    return render_template("areas/form.html", empresa=area.empresa, area=area)


@areas_bp.route("/<int:area_id>/excluir", methods=["POST"])
@login_required
def excluir(area_id):
    area = db.get_or_404(Area, area_id)
    empresa_id = area.empresa_id
    db.session.delete(area)
    db.session.commit()
    flash("Área excluída.", "info")
    return redirect(url_for("empresas.visualizar", empresa_id=empresa_id))
