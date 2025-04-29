from uuid import UUID

from litestar import Litestar, get, Router
from litestar.contrib.sqlalchemy.plugins import SQLAlchemyPlugin
from litestar.exceptions import HTTPException, NotFoundException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from db.dependencies import provide_transaction, create_db_and_migrate
from db.response_clases import OfferNamesResponse, OfferWallResponse, JsonErrorResponse
from db.schema import OfferChoices, OfferWall, OfferWallOffer, OfferWallPopupOffer

from db.settings import db_config
from utils import fix_url, get_result, http_exception_handler, not_found_exception_handler


@get("/get_offer_names", response=OfferNamesResponse)
async def get_offer_names() -> OfferNamesResponse:
    offer_names = [choice.value for choice in OfferChoices]
    return OfferNamesResponse(offer_names=offer_names)


@get("/{token:str}", response_model=OfferWallResponse)
async def get_wall_by_token(token: str, transaction: AsyncSession) -> OfferWallResponse:
    try:
        token_uuid = UUID(token)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid token format")

    stmt = select(OfferWall).options(
        joinedload(OfferWall.offer_assignments)
        .joinedload(OfferWallOffer.offer),
        joinedload(OfferWall.popup_assignments)
        .joinedload(OfferWallPopupOffer.offer),
    ).where(OfferWall.token == token_uuid).order_by(OfferWallOffer.order)

    result = await transaction.execute(stmt)
    wall_obj = result.scalars().first()

    if wall_obj is None:
        raise HTTPException(status_code=404, detail="OfferWall not found")

    return await get_result(wall_obj)


@get("/by_url/{url:path}", response_model=OfferWallResponse)
async def get_wall_by_url(url: str, transaction: AsyncSession) -> OfferWallResponse:
    result_url = await fix_url(url)

    stmt = select(OfferWall).options(
        joinedload(OfferWall.offer_assignments)
        .joinedload(OfferWallOffer.offer),
        joinedload(OfferWall.popup_assignments)
        .joinedload(OfferWallPopupOffer.offer),
    ).where(OfferWall.url == result_url).order_by(OfferWallOffer.order)
    result = await transaction.execute(stmt)
    wall_obj = result.scalars().first()

    if wall_obj is None:
        raise HTTPException(status_code=404, detail="OfferWall not found")

    return await get_result(wall_obj)


router = Router(
    route_handlers=[
        get_offer_names,
        get_wall_by_token,
        get_wall_by_url
    ],
    path="/api/offerwalls/"
)


app = Litestar(
    route_handlers=[
        router
    ],
    dependencies={"transaction": provide_transaction},
    plugins=[SQLAlchemyPlugin(db_config)],
    on_startup=[
        create_db_and_migrate
    ],
    exception_handlers={
        HTTPException: http_exception_handler,
        NotFoundException: not_found_exception_handler,
        Exception: lambda request, exc: JsonErrorResponse.to_response(),
    }
)

asgi_app = app
