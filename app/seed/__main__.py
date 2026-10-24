from app.config import Settings
from app.persistence.db import Database
from app.seed import seed

db = Database(Settings().database)
seed(db)
db.close()
print("Demo identities, policies and six sources are ready.")
