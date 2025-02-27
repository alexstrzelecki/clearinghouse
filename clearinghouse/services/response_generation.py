from typing import List, Any
import datetime

from clearinghouse.models.response import (
    Meta,
    GenericItemResponse,
    GenericCollectionResponse,
)


def generate_meta_data(response_type: str) -> Meta:
    return Meta(
        type=response_type,
        timestamp=datetime.datetime.now(),
    )


def generate_generic_response(response_type: str, data: Any | List[Any]) -> GenericCollectionResponse | GenericItemResponse:
    meta = generate_meta_data(response_type)
    if isinstance(data, list):
        return GenericCollectionResponse(
            meta=meta,
            data=data,
        )
    else:
        return GenericItemResponse(
            meta=meta,
            data=data,
        )
