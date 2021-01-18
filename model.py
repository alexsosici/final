import os
from sqla_wrapper import SQLAlchemy

db = SQLAlchemy(os.getenv("DATABASE_URL", "sqlite:///localhost.sqlite"))  # this connects to a database either on Heroku or on localhost

# u modelu bi definirao kao u našoj igri klus USER...?