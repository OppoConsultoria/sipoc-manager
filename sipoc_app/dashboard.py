from flask import Blueprint, render_template
from flask_login import login_required

from sipoc_app.extensions import db
from sipoc_app.models import Empresa, Area, Sipoc, SipocItem

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
@login_required
def home():
    total_empresas = Empresa.query.count()
    total_areas = Area.query.count()
    total_sipocs = Sipoc.query.count()
    total_itens = SipocItem.query.count()

    empresas = Empresa.query.order_by(Empresa.nome).all()
    sipocs_por_empresa = [
        {"nome": e.nome, "total": e.total_sipocs} for e in empresas if e.total_sipocs > 0
    ]

    media_etapas = 0.0
    if total_sipocs:
        total_process_steps = SipocItem.query.filter_by(categoria="process").count()
        media_etapas = round(total_process_steps / total_sipocs, 1)

    ultimos_sipocs = Sipoc.query.order_by(Sipoc.updated_at.desc()).limit(6).all()

    empresas_sem_sipoc = [e for e in empresas if e.total_sipocs == 0]

    return render_template(
        "dashboard.html",
        total_empresas=total_empresas,
        total_areas=total_areas,
        total_sipocs=total_sipocs,
        total_itens=total_itens,
        sipocs_por_empresa=sipocs_por_empresa,
        media_etapas=media_etapas,
        ultimos_sipocs=ultimos_sipocs,
        empresas_sem_sipoc=empresas_sem_sipoc,
    )
