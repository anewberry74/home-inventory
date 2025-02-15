from sqlmodel import Field, Session, SQLModel
import uuid


# Define the SQLModel
# Fields - name, device_type, role, specs, ip, os_firmware, notes
class InventoryBase(SQLModel):
    name: str | None = Field(default=None, index=True)
    device_type: str | None = Field(index=True)
    role: str | None = Field(default=None)
    specs: str | None = Field(default=None)
    ip: str | None = Field(default=None)
    os_firmware: str | None = Field(default=None)
    state: str | None = Field(default=None)
    notes: str | None = Field(default=None)


class Inventory(InventoryBase, table=True):
    # id: int | None = Field(default=None, primary_key=True)
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class InventoryItems(InventoryBase):
    # id: int
    id: uuid.UUID


class InventoryUpdate(InventoryBase):
    name: str | None = Field(default=None, index=True)
    device_type: str | None = Field(index=True)
    role: str | None = Field(default=None)
    specs: str | None = Field(default=None)
    ip: str | None = Field(default=None)
    os_firmware: str | None = Field(default=None)
    state: str | None = Field(default=None)
    notes: str | None = Field(default=None)
