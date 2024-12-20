from typing import Annotated
import uuid

from fastapi import FastAPI, Depends, HTTPException, Query, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")


# Define the SQLModel
# Fields - name, ip, device type, role, platform, description
class InventoryBase(SQLModel):
    device_type: str = Field(index=True)
    name: str | None = Field(default=None, index=True)
    role: str | None = Field(default=None)
    specs: str | None = Field(default=None)
    ip: str | None = Field(default=None)
    os_firmware: str | None = Field(default=None)
    notes: str | None = Field(default=None)


class Inventory(InventoryBase, table=True):
    #id: int | None = Field(default=None, primary_key=True)
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class InventoryItems(InventoryBase):
    #id: int
    id: uuid.UUID


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

# Home Page
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

# Get all inventory for the web page
@app.get("/inventory", response_class=HTMLResponse)
async def read_item(request: Request, session: SessionDep):
    inventory = session.exec(select(Inventory)).all()
    return templates.TemplateResponse("inventory.html", {"request": request, "inventory": inventory})

@app.get("/inventory/add")
def get_inventory_ui(request: Request, session: SessionDep):
    inventory = session.exec(select(Inventory)).all()
    return templates.TemplateResponse('add_inventory_form.html', {"request": request, "inventory": inventory})


@app.post("/inventory/add")
async def add_inventory_ui(
    request: Request,
    device_type: str = Form(...),
    name: str = Form(...),
    role: str = Form(...),
    specs: str = Form(...),
    ip: str = Form(...),
    os_firmware: str = Form(...),
    notes: str = Form(...)
):
    inventory = Inventory(
        device_type=device_type,
        name=name,
        role=role,
        specs=specs,
        ip=ip,
        os_firmware=os_firmware,
        notes=notes
    )
    with Session(engine) as session:
        session.add(inventory)
        session.commit()
    return RedirectResponse(url="/inventory", status_code=302)


# Create a new inventory item
@app.post("/inventory/api/", response_model=InventoryItems)
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
@app.get("/inventory/api/", response_model=list[InventoryItems])
def read_inventory_items(session: SessionDep):
    inventory_items = session.exec(select(Inventory)).all()
    return inventory_items

# Get a single inventory item
@app.get("/inventory/api/{inventory_id}", response_model=InventoryItems)
def read_inventory_item(inventory_id: int, session: SessionDep):
    inventory = session.get(Inventory, inventory_id)
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory

# Delete an inventory item
@app.delete("/inventory/api/{inventory_id}")
def delete_inventory_item(inventory_id: int, session: SessionDep):
    inventory = session.get(Inventory, inventory_id)
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    session.delete(inventory)
    session.commit()
    return {"message": "Inventory item deleted successfully"}
