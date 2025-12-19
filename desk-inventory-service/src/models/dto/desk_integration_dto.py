from pydantic import BaseModel, ConfigDict, Field


class DeskConfigIntegrationDTO(BaseModel):
    """Configuration data from integration service."""

    name: str
    manufacturer: str | None = None


class DeskStateIntegrationDTO(BaseModel):
    """State data from integration service."""

    position_mm: int | None = None
    speed_mms: int | None = None
    status: str | None = None
    is_position_lost: bool = Field(default=False, alias="isPositionLost")
    is_overload_protection_up: bool = Field(
        default=False, alias="isOverloadProtectionUp"
    )
    is_overload_protection_down: bool = Field(
        default=False, alias="isOverloadProtectionDown"
    )
    is_anti_collision: bool = Field(default=False, alias="isAntiCollision")


class DeskUsageIntegrationDTO(BaseModel):
    """Usage statistics from integration service."""

    activations_counter: int = Field(default=0, alias="activationsCounter")
    sit_stand_counter: int = Field(default=0, alias="sitStandCounter")


class DeskErrorIntegrationDTO(BaseModel):
    """Error log entry from integration service."""

    model_config = ConfigDict(populate_by_name=True)

    time_s: int
    error_code: int = Field(alias="errorCode")


class DeskIntegrationDTO(BaseModel):
    """DTO for desk data from integration service."""

    id: str
    name: str
    location: str | None = None
    x: float | None = None
    y: float | None = None
    config: DeskConfigIntegrationDTO | None = None
    state: DeskStateIntegrationDTO | None = None
    usage: DeskUsageIntegrationDTO | None = None
    errors: list[DeskErrorIntegrationDTO] = Field(default=[], alias="lastErrors")
