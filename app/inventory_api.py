# This file contains the API routes for the inventory items
import uuid
from fastapi import HTTPException, Depends, APIRouter
from sqlmodel import select, Session
import models
from db_conn import get_session
from util.ping_device import subnet_scan

inventory_api = APIRouter()


# Create a new inventory item
@inventory_api.post("/inventory/api/", response_model=models.InventoryItems)
def create_inventory_item(
    inventory: models.InventoryBase, session: Session = Depends(get_session)
):
    db_inventory = select(models.Inventory).where(
        models.Inventory.name == inventory.name
    )

    if session.exec(db_inventory).first():
        raise HTTPException(status_code=400, detail="Name already exists")
    inventory = models.Inventory.model_validate(inventory)
    session.add(inventory)
    session.commit()
    session.refresh(inventory)
    return inventory


# Get all inventory items
@inventory_api.get("/inventory/api/", response_model=list[models.InventoryItems])
def read_inventory_items(session: Session = Depends(get_session)):
    inventory_items = session.exec(select(models.Inventory)).all()
    return inventory_items


# Get a single inventory item
@inventory_api.get(
    "/inventory/api/{inventory_id}", response_model=models.InventoryItems
)
def read_inventory_item(
    inventory_id: uuid.UUID, session: Session = Depends(get_session)
):
    inventory = session.get(models.Inventory, inventory_id)
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory


# Delete an inventory item
@inventory_api.delete("/inventory/api/{inventory_id}")
def delete_inventory_item(
    inventory_id: uuid.UUID, session: Session = Depends(get_session)
):
    inventory = session.get(models.Inventory, inventory_id)
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    session.delete(inventory)
    session.commit()
    return {"message": "Inventory item deleted successfully"}


# Update an inventory item
@inventory_api.patch(
    "/inventory/api/{inventory_id}", response_model=models.InventoryItems
)
def update_inventory_item(
    inventory_id: uuid.UUID,
    inventory: models.InventoryUpdate,
    session: Session = Depends(get_session),
):
    db_inventory = session.get(models.Inventory, inventory_id)
    if db_inventory is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    inventory = models.InventoryUpdate.model_validate(inventory)
    for key, value in inventory.dict().items():
        setattr(db_inventory, key, value)
    session.add(db_inventory)
    session.commit()
    session.refresh(db_inventory)
    return db_inventory


# Update inventory item state (up or down)
@inventory_api.patch(
    "/inventory/api/{inventory_id}/state", response_model=models.InventoryItems
)
def update_inventory_item_state(
    inventory_id: uuid.UUID, session: Session = Depends(get_session)
):
    # Get the inventory item
    inventory = session.get(models.Inventory, inventory_id)
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    # Get the IP address from the inventory item
    ipaddr = inventory.ip
    # Get the status of the device
    status, ip_address = subnet_scan(ipaddr)
    # Update the inventory item with the new state
    inventory.state = status
    session.add(inventory)
    session.commit()
    session.refresh(inventory)
    return inventory
