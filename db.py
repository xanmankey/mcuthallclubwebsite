from active_alchemy import ActiveAlchemy
from sqlalchemy_utils import database_exists, create_database

DATABASE_URL = "sqlite:///mcuthallclub.db"

if not database_exists:
    create_database(DATABASE_URL)

# Active Alchemy provides the following columns by default: id, created_at, updated_at, is_deleted, deleted_at
db = ActiveAlchemy(DATABASE_URL, connect_args={"check_same_thread": False})
