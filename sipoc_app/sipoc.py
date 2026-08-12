from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from sipoc_app.extensions import db
from sipoc_app.models import Sipoc, SipocEtapa, SipocEtapaItem, Empresa, Area, ITEM_CATEGORIAS

sipoc_bp = Blueprint("sipoc", __name__, url_prefix="/sipoc")


def _salvar_etapas(sipoc, form):
    """Substitui as etapas do SIPOC (e seus itens) pelas enviadas no formulário.

    Cada etapa é identificada por uma chave única (etapa_key[]) gerada no
    cliente, usada para agrupar os campos etapa_item__<key>__<categoria>[]
    daquela etapa especificamente.
    """
    sipoc.etapas.clear()

    nomes = form.getlist("etapa_nome[]")
    chaves = form.getlist("etapa_key[]")

    ordem = 0
    for nome, chave in zip(nomes, chaves):
        nome = nome.strip()
        if not nome:
            continue
        ordem += 1
        etapa = SipocEtapa(nome=nome, ordem=ordem)
        for categoria in ITEM_CATEGORIAS:
            valores = form.getlist(f"etapa_item__{chave}__{categoria}[]")
            item_ordem = 0
            for valor in valores:
                texto = valor.strip()
                if texto:
                    item_ordem += 1
                    etapa.itens.append(
                        SipocEtapaItem(categoria=categoria, texto=texto, ordem=item_ordem)
                    )
        sipoc.etapas.append(etapa)


@sipoc_bp.route("/")
@login_required
def listar():
    empresa_id = request.args.get("empresa_id", type=int)
    area_id = request.args.get("area_id", type=int)
    busca = request.args.get("q", "").strip()

    query = Sipoc.query
    if empresa_id:
        query = query.filter(Sipoc.empresa_id == empresa_id)
    if area_id:
        query = query.filter(Sipoc.area_id == area_id)
    if busca:
        query = query.filter(Sipoc.nome_processo.ilike(f"%{busca}%"))

    sipocs = query.order_by(Sipoc.updated_at.desc()).all()
    empresas = Empresa.query.order_by(Empresa.nome).all()
    areas = Area.query.filter_by(empresa_id=empresa_id).order_by(Area.nome).all() if empresa_id else []

    return render_template(
        "sipoc/list.html",
        sipocs=sipocs,
        empresas=empresas,
        areas=areas,
        empresa_id=empresa_id,
        area_id=area_id,
        busca=busca,
    )


@sipoc_bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    empresas = Empresa.query.order_by(Empresa.nome).all()
    empresa_id_pre = request.args.get("empresa_id", type=int)

    if not empresas:
        flash("Cadastre uma empresa antes de criar um SIPOC.", "warning")
        return redirect(url_for("empresas.novo"))

    if request.method == "POST":
        nome_processo = request.form.get("nome_processo", "").strip()
        empresa_id = request.form.get("empresa_id", type=int)
        area_id = request.form.get("area_id", type=int) or None

        if not nome_processo or not empresa_id:
            flash("Informe o nome do processo e a empresa.", "danger")
        else:
            sipoc = Sipoc(
                nome_processo=nome_processo,
                objetivo=request.form.get("objetivo", "").strip(),
                empresa_id=empresa_id,
                area_id=area_id,
                created_by_id=current_user.id,
            )
            _salvar_etapas(sipoc, request.form)
            if not sipoc.etapas:
                flash("Adicione ao menos uma etapa do processo.", "danger")
                return render_template(
                    "sipoc/form.html", sipoc=None, empresas=empresas, empresa_id_pre=empresa_id_pre
                )
            db.session.add(sipoc)
            db.session.commit()
            flash("SIPOC criado com sucesso.", "success")
            return redirect(url_for("sipoc.visualizar", sipoc_id=sipoc.id))

    return render_template(
        "sipoc/form.html", sipoc=None, empresas=empresas, empresa_id_pre=empresa_id_pre
    )


@sipoc_bp.route("/<int:sipoc_id>")
@login_required
def visualizar(sipoc_id):
    sipoc = db.get_or_404(Sipoc, sipoc_id)
    return render_template("sipoc/view.html", sipoc=sipoc)


@sipoc_bp.route("/<int:sipoc_id>/editar", methods=["GET", "POST"])
@login_required
def editar(sipoc_id):
    sipoc = db.get_or_404(Sipoc, sipoc_id)
    empresas = Empresa.query.order_by(Empresa.nome).all()

    if request.method == "POST":
        nome_processo = request.form.get("nome_processo", "").strip()
        empresa_id = request.form.get("empresa_id", type=int)
        area_id = request.form.get("area_id", type=int) or None

        if not nome_processo or not empresa_id:
            flash("Informe o nome do processo e a empresa.", "danger")
        else:
            sipoc.nome_processo = nome_processo
            sipoc.objetivo = request.form.get("objetivo", "").strip()
            sipoc.empresa_id = empresa_id
            sipoc.area_id = area_id
            _salvar_etapas(sipoc, request.form)
            db.session.commit()
            flash("SIPOC atualizado.", "success")
            return redirect(url_for("sipoc.visualizar", sipoc_id=sipoc.id))

    return render_template("sipoc/form.html", sipoc=sipoc, empresas=empresas, empresa_id_pre=None)


@sipoc_bp.route("/<int:sipoc_id>/excluir", methods=["POST"])
@login_required
def excluir(sipoc_id):
    sipoc = db.get_or_404(Sipoc, sipoc_id)
    empresa_id = sipoc.empresa_id
    nome = sipoc.nome_processo
    db.session.delete(sipoc)
    db.session.commit()
    flash(f'SIPOC "{nome}" excluído.', "info")
    return redirect(url_for("empresas.visualizar", empresa_id=empresa_id))


@sipoc_bp.route("/<int:sipoc_id>/relatorio")
@login_required
def relatorio(sipoc_id):
    sipoc = db.get_or_404(Sipoc, sipoc_id)
    return render_template("sipoc/relatorio.html", sipoc=sipoc)


@sipoc_bp.route("/api/areas/<int:empresa_id>")
@login_required
def areas_por_empresa(empresa_id):
    areas = Area.query.filter_by(empresa_id=empresa_id).order_by(Area.nome).all()
    return {"areas": [{"id": a.id, "nome": a.nome} for a in areas]}
