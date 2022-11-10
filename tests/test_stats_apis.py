import pytest

from unittest.mock import patch, MagicMock


ingest_data_url = "/v1/core-di-stats/ingest-data"
create_ingestion_status_url = "/v1/core-di-stats/create-ingestion-status"


@pytest.mark.asyncio
async def test_get_status_by_request_id(get_api_client, *_):
    """ Ingesting data for getting valid request_id """
    response = await get_api_client.post(ingest_data_url, json={
        "tenant_id": "test_tenant_id",
        "app_id": "test_app_id",
        "entity_type": "test_entity_type",
        "src_type": "test_src_type",
        "is_batch_required": True,
        "batch_size": 0,
        "subscriber_name": ["test_subscriber_name", "test_subscriber_name_2"],
        "enrich_oncreation": True
    })
    assert response.status_code == 201
    request_id = response.json()['request_id']

    """ Getting status by request_id"""
    response = await get_api_client.get(f"/v1/core-di-stats/get-status/{request_id}")
    assert response.status_code == 200
    assert response.json().get('app_id') == "test_app_id"
    assert response.json().get('subscriber_name') == ["test_subscriber_name", "test_subscriber_name_2"]


@pytest.mark.asyncio
async def test_get_status_by_invalid_request_id(get_api_client, *_):
    """ Test get status with invalid request_id """
    invalid_request_id = "invalid_request_id"
    invalid_request_id_response = await get_api_client.get(f"/v1/core-di-stats/get-status/{invalid_request_id}")
    assert invalid_request_id_response.status_code == 404
    assert invalid_request_id_response.json().get("message") == f"Can not found request status by id {invalid_request_id}"


@pytest.mark.asyncio
async def test_missing_field_ingest_data(get_api_client, *_):
    """ Test missing field ingest data """
    response = await get_api_client.post(ingest_data_url, json={
        "tenant_id": "test_tenant_id",
        "app_id": "test_app_id",
        "entity_type": "test_entity_type",
        "src_type": "test_src_type",
        "is_batch_required": True,
        "batch_size": 0,
        "subscriber_name": ["test_subscriber_name", "test_subscriber_name_2"],
    })
    assert response.status_code == 422
    assert response.json().get("detail")[0].get("msg") == "field required"
    assert response.json().get("detail")[0].get("type") == "value_error.missing"


@pytest.mark.asyncio
async def test_create_ingestion_status_with_not_existing_request_id(get_api_client, *_):
    """ Test create ingestion status with not existing request_id """
    response = await get_api_client.post(create_ingestion_status_url, json={
        "request_id": "test_request_id",
        "source_id": "string",
        "file_uri": "string",
        "entity_type": "string",
        "is_error": True,
        "message": "string",
        "total_record_count": 0,
        "total_failed_count": 0,
        "total_success_count": 0,
        "source_queue_name": "string"
        })
    assert response.status_code == 400
    assert "request_id" in response.json().get("message")


@pytest.mark.asyncio
async def test_create_ingestion_status_with_missing_field(get_api_client, *_):
    """ Test create ingestion status with missing field """
    response = await get_api_client.post(create_ingestion_status_url, json={
        "request_id": "test_request_id",
        "source_id": "string",
        "file_uri": "string",
        "entity_type": "string",
        "is_error": True,
        "message": "string",
        "total_record_count": 0,
        "total_failed_count": 0,
        "total_success_count": 0,
        })
    assert response.status_code == 422
    assert response.json().get("detail")[0].get("msg") == "field required"
    assert response.json().get("detail")[0].get("type") == "value_error.missing"


@pytest.mark.asyncio
async def test_create_and_get_ingestion_statuses(get_api_client, *_):
    """ Ingesting data for getting valid request_id """
    response = await get_api_client.post(ingest_data_url, json={
        "tenant_id": "test_tenant_id",
        "app_id": "test_app_id",
        "entity_type": "test_entity_type",
        "src_type": "test_src_type",
        "is_batch_required": True,
        "batch_size": 0,
        "subscriber_name": ["test_subscriber_name", "test_subscriber_name_2"],
        "enrich_oncreation": True
    })
    assert response.status_code == 201
    request_id = response.json()['request_id']

    """ Creating ingestion status """
    response = await get_api_client.post(create_ingestion_status_url, json={
        "request_id": request_id,
        "source_id": "string",
        "file_uri": "string",
        "entity_type": "string",
        "status": "test",
        "is_error": True,
        "message": "string",
        "total_record_count": 0,
        "total_failed_count": 0,
        "total_success_count": 0,
        "source_queue_name": "string"
    })
    assert response.status_code == 201

    """ Getting status by request_id"""
    response = await get_api_client.get(f"/v1/core-di-stats/get-status/{request_id}")
    assert response.status_code == 200
    assert response.json().get('app_id') == "test_app_id"
    assert response.json().get('subscriber_name') == ["test_subscriber_name", "test_subscriber_name_2"]

    """Test duplicate ingestion status"""
    response = await get_api_client.post(create_ingestion_status_url, json={
        "request_id": request_id,
        "source_id": "string",
        "file_uri": "string",
        "entity_type": "string",
        "status": "test",
        "is_error": True,
        "message": "string",
        "total_record_count": 0,
        "total_failed_count": 0,
        "total_success_count": 0,
        "source_queue_name": "string"
    })
    assert response.status_code == 409
    assert "Duplicate entry" in response.json().get("message")


@pytest.mark.asyncio
@patch('solution.sp.sql_base.db_client.DBClientSP.db_update_ingestion_status')
async def test_update_ingestion_status(db_update_ingestion_status: MagicMock, get_api_client, *_):
    """ Ingesting data for getting valid request_id """
    db_update_ingestion_status.return_value = True
    response = await get_api_client.patch("/v1/core-di-stats/update-ingestion-status/test/test", json={
        "request_id": "test_request_id",
        "source_id": "string",
        "file_uri": "string",
        "entity_type": "string",
        "status": "Running",
        "is_error": True,
        "message": "string",
        "total_record_count": 0,
        "total_failed_count": 0,
        "total_success_count": 0,
        "source_queue_name": "string"
    })

    assert response.status_code == 200
    assert response.json().get('message') == "Ingestion status was successfully updated"


@pytest.mark.asyncio
async def test_update_ingestion_status_with_invalid_enum(get_api_client, *_):
    """ Ingesting data for getting valid request_id """
    response = await get_api_client.patch("/v1/core-di-stats/update-ingestion-status/test/test", json={
        "request_id": "test_request_id",
        "source_id": "string",
        "file_uri": "string",
        "entity_type": "string",
        "status": "test",
        "is_error": True,
        "message": "string",
        "total_record_count": 0,
        "total_failed_count": 0,
        "total_success_count": 0,
        "source_queue_name": "string"
    })

    assert response.status_code == 422
    assert response.json().get('detail')[0].get('msg') == "value is not a valid enumeration member; permitted: " \
                                                          "'Pending', 'Running', 'Completed', 'Failed'"
    assert response.json().get('detail')[0].get('type') == "type_error.enum"
