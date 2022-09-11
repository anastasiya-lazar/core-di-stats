from fastapi import APIRouter, Depends, HTTPException, status

from bst_core.shared.logger import get_logger

from core.api.dtos import MediatorIngestionSchema, StatusResponseSchema
from core.impl.rest_controller import RestController
from solution.channel.fastapi.auth_controller import AuthTokenApiKey

logger = get_logger(__name__)

auth = AuthTokenApiKey(name="api")

router = APIRouter(dependencies=[Depends(auth)],  prefix='/v1/core-di-stats')
rest_controller = RestController()


@router.post("/ingestData", status_code=201)
async def ingest_stats_data(payload: MediatorIngestionSchema):
    try:
        return await rest_controller.ingest_data(payload)
    except HTTPException as e:
        raise e
    except Exception:
        logger.error("Error:", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An error occurred, please read service logs")


@router.get("/get_status/{request_id}", response_model=StatusResponseSchema)
async def get_latest_schema_version(request_id: str):
    try:
        return await rest_controller.get_status_by_request_id(request_id)
    except HTTPException as e:
        raise e
    except Exception:
        logger.error("Error:", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An error occurred, please read service logs")

