import os
import sys
from flask import Flask, send_from_directory
from flask_cors import CORS

# NÃO MUDE: garante que "src/..." possa ser importado corretamente
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Importa DB e modelos/rotas
from src.models.chat import db, ChatSession, ChatMessage, ChatAnalytics  # db é definido aqui
from src.models.user import User
from src.routes.user import user_bp
from src.routes.chat import chat_bp

# Define pasta de estáticos (src/static)
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# ---- Configurações de produção/ambiente ----
# SECRET_KEY por variável de ambiente (obrigatório em produção)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-me-in-prod')

# DB: usa, nesta ordem:
# 1) DATABASE_URL (Postgres no Render ou outro banco gerenciado)
# 2) SQLITE_PATH (ex.: /var/data/app.db se usar Persistent Disk no Render)
# 3) fallback local: src/database/app.db
database_url = os.environ.get('DATABASE_URL')
sqlite_path = os.environ.get(
    'SQLITE_PATH',
    os.path.join(os.path.dirname(__file__), 'database', 'app.db')
)

if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # garante diretório existente ao usar SQLite
    os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{sqlite_path}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# CORS (ajuste origins conforme sua necessidade em produção)
CORS(app)

# Blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(chat_bp, url_prefix='/api')

# Inicializa DB e cria tabelas (para MVP). Em produção, considere Flask-Migrate.
with app.app_context():
    db.init_app(app)
    db.create_all()

# ----------------- Servir frontend estático -----------------
# Tenta servir arquivos em src/static/ e, se não existirem, entrega index.html
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    requested = os.path.join(static_folder_path, path)
    if path != "" and os.path.exists(requested) and os.path.isfile(requested):
        return send_from_directory(static_folder_path, path)

    index_path = os.path.join(static_folder_path, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(static_folder_path, 'index.html')

    return "index.html not found", 404

# ----------------- Execução local (dev) -----------------
if __name__ == '__main__':
    # Para desenvolvimento local apenas. Em produção no Render, use gunicorn.
    app.run(host='0.0.0.0', port=5000, debug=True)
