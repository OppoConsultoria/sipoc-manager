from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from sipoc_app.extensions import db
from sipoc_app.models import Empresa

empresas_bp = Blueprint("empresas", __name__, url_prefix="/empresas")


@empresas_bp.route("/")
@login_required
def listar():
    busca = request.args.get("q", "").strip()
    query = Empresa.query
    if busca:
        query = query.filter(Empresa.nome.ilike(f"%{busca}%"))
    empresas = query.order_by(Empresa.nome).all()
    return render_template("empresas/list.html", empresas=empresas, busca=busca)


@empresas_bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        if not nome:
            flash("Informe o nome da empresa.", "danger")
        else:
            empresa = Empresa(
                nome=nome,
                cnpj=request.form.get("cnpj", "").strip(),
                setor=request.form.get("setor", "").strip(),
                observacoes=request.form.get("observacoes", "").strip(),
                created_by_id=current_user.id,
            )
            db.session.add(empresa)
            db.session.commit()
            flash("Empresa cadastrada com sucesso.", "success")
            return redirect(url_for("empresas.visualizar", empresa_id=empresa.id))
    return render_template("empresas/form.html", empresa=None)


@empresas_bp.route("/<int:empresa_id>")
@login_required
def visualizar(empresa_id):
    empresa = db.get_or_404(Empresa, empresa_id)
    return render_template("empresas/view.html", empresa=empresa)


@empresas_bp.route("/<int:empresa_id>/editar", methods=["GET", "POST"])
@login_required
def editar(empresa_id):
    empresa = db.get_or_404(Empresa, empresa_id)
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        if not nome:
            flash("Informe o nome da empresa.", "danger")
        else:
            empresa.nome = nome
            empresa.cnpj = request.form.get("cnpj", "").strip()
            empresa.setor = request.form.get("setor", "").strip()
            empresa.observacoes = request.form.get("observacoes", "").strip()
            db.session.commit()
            flash("Empresa atualizada.", "success")
            return redirect(url_for("empresas.visualizar", empresa_id=empresa.id))
    return render_template("empresas/form.html", empresa=empresa)


@empresas_bp.route("/<int:empresa_id>/excluir", methods=["POST"])
@login_required
def excluir(empresa_id):
    empresa = db.get_or_404(Empresa, empresa_id)
    nome = empresa.nome
    db.session.delete(empresa)
    db.session.commit()
    flash(f'Empresa "{nome}" e todos os seus dados foram excluídos.', "info")
    return redirect(url_for("empresas.listar"))
