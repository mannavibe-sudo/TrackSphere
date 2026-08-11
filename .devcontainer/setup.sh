#!/usr/bin/env bash
# Runs automatically once, the first time this Codespace is created.
# Sets up the database, backend, and frontend so they're ready to run.
set -e

echo "=== TrackSphere: setting up your environment ==="

# --- PostgreSQL: install and create the database ---
echo "--- Installing PostgreSQL ---"
sudo apt-get update -qq
sudo apt-get install -y -qq postgresql postgresql-contrib

echo "--- Creating database ---"
sudo service postgresql start
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';" || true
sudo -u postgres psql -c "CREATE DATABASE tracksphere;" || echo "Database already exists, skipping."

# --- Backend: .env, venv, dependencies, migrations ---
echo "--- Setting up backend ---"
cd backend

cat > .env <<'EOF'
APP_NAME=TrackSphere
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/tracksphere
JWT_SECRET_KEY=tracksphere-codespaces-dev-secret-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=["http://localhost:5173"]
EOF

python -m venv venv
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
alembic upgrade head

# --- Seed a Super Admin so you can log in immediately ---
python - <<'PYEOF'
import sys
sys.path.insert(0, ".")
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.models.enums import UserRole, EntityStatus

db = SessionLocal()
existing = db.query(User).filter(User.email == "admin@tracksphere.com").first()
if not existing:
    admin = User(
        company_id=None,
        name="Super Admin",
        email="admin@tracksphere.com",
        password_hash=hash_password("Admin@123"),
        role=UserRole.SUPER_ADMIN,
        status=EntityStatus.ACTIVE,
    )
    db.add(admin)
    db.commit()
    print("Super Admin created: admin@tracksphere.com / Admin@123")
else:
    print("Super Admin already exists.")
db.close()
PYEOF

cd ..

# --- Frontend: npm install ---
echo "--- Setting up frontend ---"
cd frontend
npm install
cd ..

echo ""
echo "=== Setup complete! ==="
echo "Backend:  cd backend  && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0"
echo "Frontend: cd frontend && npm run dev -- --host 0.0.0.0"
echo "Login:    admin@tracksphere.com / Admin@123"
