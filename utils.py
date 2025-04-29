import logging
import re

from litestar.exceptions import HTTPException, NotFoundException

from db.response_clases import JsonErrorResponse, OfferWallResponse, OfferAssignment, OfferDetails


async def fix_url(text: str) -> str:
    text = text.lstrip('/')

    text = re.sub(r'^(https:)/([^/])', r'\1//\2', text)
    text = re.sub(r'^(http:)/([^/])', r'\1//\2', text)

    return text

async def get_result(wall_obj):
    all_dto = OfferWallResponse(
        token=wall_obj.token,
        name=wall_obj.name,
        url=wall_obj.url,
        description=wall_obj.description,
        offer_assignments=[
            OfferAssignment(
                offer=OfferDetails(
                    uuid=offer_offer.offer.uuid,
                    id=offer_offer.offer.id,
                    url=offer_offer.offer.url,
                    is_active=offer_offer.offer.is_active,
                    name=offer_offer.offer.name,
                    sum_to=offer_offer.offer.sum_to,
                    term_to=offer_offer.offer.term_to,
                    percent_rate=offer_offer.offer.percent_rate
                )
            )
            for offer_offer in wall_obj.offer_assignments
        ],
        popup_assignments=[
            OfferAssignment(
                offer=OfferDetails(
                    uuid=offer_offer.offer.uuid,
                    id=offer_offer.offer.id,
                    url=offer_offer.offer.url,
                    is_active=offer_offer.offer.is_active,
                    name=offer_offer.offer.name,
                    sum_to=offer_offer.offer.sum_to,
                    term_to=offer_offer.offer.term_to,
                    percent_rate=offer_offer.offer.percent_rate
                )
            )
            for offer_offer in wall_obj.popup_assignments
        ],
    )

    return all_dto

def http_exception_handler(request, exc: HTTPException):
    logging.error(exc)
    return JsonErrorResponse.to_response(
        detail=exc.detail,
        status_code=exc.status_code,
    )

def not_found_exception_handler(request, exc: NotFoundException):
    logging.error(exc)
    return JsonErrorResponse.to_response(
        detail="Resource not found.",
        status_code=404,
    )
