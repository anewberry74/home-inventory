from typing import Annotated
import uuid
from uuid import UUID

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select


# Define the SQLModel
# Fields - name, ip, device type, role, platform, description
class InventoryBase(SQLModel):
    name: str = Field(index=True)
    ip: str | None = Field(default=None, index=True)
    device_type: str | None = Field(default=None)
    role: str | None = Field(default=None)
    platform: str | None = Field(default=None)
    description: str | None = Field(default=None)


class Inventory(InventoryBase, table=True):
    #id: int | None = Field(default=None, primary_key=True)
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class InventoryItems(InventoryBase):
    #id: int
    id: UUID


# setup database connection
sqlite_file_name = "inventory.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# Create the database engine
connect_args = {"check_same_thread": False}  # allows FastAPI to use the same SQLite database in different threads
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

# Create a dependency for the session
SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

# Create Database Tables on Startup
# ToDO - This is not the best way to create tables
# look at using Alembic for migrations
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Create a new inventory item
@app.post("/inventory/", response_model=InventoryItems)
def create_inventory_item(inventory: InventoryBase, session: SessionDep):
    db_inventory = select(Inventory).where(Inventory.name == inventory.name)

    if session.exec(db_inventory).first():
        raise HTTPException(status_code=400, detail="Name already exists")
    
    inventory = Inventory.model_validate(inventory)
    session.add(inventory)
    session.commit()
    session.refresh(inventory)
    return inventory

# Get all inventory items
@app.get("/inventory/", response_model=list[InventoryItems])
def read_inventory_items(session: SessionDep):
    inventory_items = session.exec(select(Inventory)).all()
    return inventory_items

# Get a single inventory item
@app.get("/inventory/{inventory_id}", response_model=InventoryItems)
def read_inventory_item(inventory_id: int, session: SessionDep):
    inventory = session.get(Inventory, inventory_id)
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory

# Delete an inventory item
@app.delete("/inventory/{inventory_id}")
def delete_inventory_item(inventory_id: int, session: SessionDep):
    inventory = session.get(Inventory, inventory_id)
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    session.delete(inventory)
    session.commit()
    return {"message": "Inventory item deleted successfully"}
