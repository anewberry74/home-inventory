from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi import FastAPI, Depends

# setup database connection
sqlite_file_name = "data/inventory.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# Create the database engine
connect_args = {
    "check_same_thread": False
}  # allows FastAPI to use the same SQLite database in different threads
engine = create_engine(sqlite_url, connect_args=connect_args)


# Create the database and tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# Create Session Dependency
# Session is what stores the objects in memory
# then it uses the engine to communicate with the database
def get_session():
    with Session(engine) as session:
        yield session
