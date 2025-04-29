from uuid import UUID

from litestar import status_codes, Response, MediaType

from db.schema import OfferChoices
from pydantic import BaseModel, Field
from typing import List, Optional


class OfferNamesResponse(BaseModel):
    offer_names: List[str] = Field(..., example=["Loanplus"])


class OfferAssignmentDTO(BaseModel):
    uuid: UUID
    id: int
    url: Optional[str] = None
    is_active: bool

    name: OfferChoices
    sum_to: Optional[str] = None
    term_to: Optional[int] = None
    percent_rate: Optional[int] = None

    class Config:
        orm_mode = True


class OfferDetails(BaseModel):
    uuid: UUID
    id: int
    url: str
    is_active: bool
    name: str
    sum_to: str
    term_to: int
    percent_rate: int

    class Config:
        orm_mode = True

class OfferAssignment(BaseModel):
    offer: OfferDetails

    class Config:
        orm_mode = True

class OfferWallResponse(BaseModel):
    token: UUID
    name: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    offer_assignments: List[OfferAssignment]
    popup_assignments: List[OfferAssignment]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "token": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "name": "string",
                "url": "string",
                "description": "string",
                "offer_assignments": [
                    {
                        "offer": {
                            "uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                            "id": 9223372036854776000,
                            "url": "string",
                            "is_active": True,
                            "name": "Loanplus",
                            "sum_to": "string",
                            "term_to": 9223372036854776000,
                            "percent_rate": 9223372036854776000
                        }
                    }
                ],
                "popup_assignments": [
                    {
                        "offer": {
                            "uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                            "id": 9223372036854776000,
                            "url": "string",
                            "is_active": True,
                            "name": "Loanplus",
                            "sum_to": "string",
                            "term_to": 9223372036854776000,
                            "percent_rate": 9223372036854776000
                        }
                    }
                ]
            }
        }

class JsonErrorResponse:
    default_detail = "Something went wrong"
    default_status_code = status_codes.HTTP_500_INTERNAL_SERVER_ERROR

    @classmethod
    def to_response(cls, detail: str = None, status_code: int = None):
        return Response(
            media_type=MediaType.JSON,
            content={"message": detail or cls.default_detail},
            status_code=status_code or cls.default_status_code,
        )
