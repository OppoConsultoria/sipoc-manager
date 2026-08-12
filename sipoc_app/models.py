from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from sipoc_app.extensions import db, login_manager

CATEGORIAS = ("supplier", "input", "process", "output", "customer")
CATEGORIA_LABEL = {
    "supplier": "Fornecedor",
    "input": "Entrada",
    "process": "Etapa do Processo",
    "output": "Saída",
    "customer": "Cliente",
}


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class Empresa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    cnpj = db.Column(db.String(30))
    setor = db.Column(db.String(120))
    observacoes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    created_by = db.relationship("User")
    areas = db.relationship(
        "Area", backref="empresa", cascade="all, delete-orphan", order_by="Area.nome"
    )
    sipocs = db.relationship(
        "Sipoc", backref="empresa", cascade="all, delete-orphan",
        order_by="Sipoc.nome_processo",
    )

    @property
    def total_sipocs(self):
        return len(self.sipocs)


class Area(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresa.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sipocs = db.relationship("Sipoc", backref="area")

    @property
    def total_sipocs(self):
        return len(self.sipocs)


class Sipoc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_processo = db.Column(db.String(255), nullable=False)
    objetivo = db.Column(db.Text)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresa.id"), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey("area.id"))
    created_by_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    created_by = db.relationship("User")
    itens = db.relationship(
        "SipocItem",
        backref="sipoc",
        cascade="all, delete-orphan",
        order_by="SipocItem.ordem",
    )

    def itens_por_categoria(self, categoria):
        return [i for i in self.itens if i.categoria == categoria]

    @property
    def contagem(self):
        return {c: len(self.itens_por_categoria(c)) for c in CATEGORIAS}

    @property
    def total_itens(self):
        return len(self.itens)


class SipocItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sipoc_id = db.Column(db.Integer, db.ForeignKey("sipoc.id"), nullable=False)
    categoria = db.Column(db.String(20), nullable=False)
    texto = db.Column(db.String(500), nullable=False)
    ordem = db.Column(db.Integer, default=0)
