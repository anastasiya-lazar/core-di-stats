from unittest import TestCase

from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from solution.channel.fastapi.main import app


@patch("solution.channel.fastapi.auth_controller.Client")
@patch("solution.channel.fastapi.auth_controller.AuthTokenValidator")
class StatsTestCase(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from solution.profile import profile
        cls._db = profile.db_client
        cls._client = TestClient(app).__enter__()

    def test_get_status_by_request_id(self, *_):
        """ Ingesting data for getting valid request_id """
        response = self._client.post("/v1/core-di-stats/ingest-data", json={
            "tenant_id": "test_tenant_id",
            "app_id": "test_app_id",
            "entity_type": "test_entity_type",
            "src_type": "test_src_type",
            "is_batch_required": True,
            "batch_size": 0,
            "subscriber_name": ["test_subscriber_name", "test_subscriber_name_2"],
            "enrich_oncreation": True
        })
        self.assertEqual(response.status_code, 201)
        request_id = response.json()['request_id']

        """ Getting status by request_id"""
        response = self._client.get(f"/v1/core-di-stats/get-status/{request_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("app_id"), "test_app_id")
        self.assertEqual(response.json().get("subscriber_name"), ["test_subscriber_name", "test_subscriber_name_2"])

    def test_get_status_by_invalid_request_id(self, *_):
        """ Test get status with invalid request_id """
        invalid_request_id = "invalid_request_id"
        invalid_request_id_response = self._client.get(f"/v1/core-di-stats/get-status/{invalid_request_id}")
        self.assertEqual(invalid_request_id_response.status_code, 404)
        self.assertDictEqual(
            invalid_request_id_response.json(),
            {'code': 404, 'is_error': True,
             'message': 'Can not found request by id invalid_request_id'}
        )

    def test_missing_field_ingest_data(self, *_):
        """ Test ingest data with missing field """
        request_url = "/v1/core-di-stats/ingest-data"
        response = self._client.post(request_url, json={
            "tenant_id": "string",
            "app_id": "string",
            "entity_type": "string",
            "src_type": "string",
            "is_batch_required": True,
            "batch_size": 0,
            "subscriber_name": ["test_subscriber_name", "test_subscriber_name_2"],
        })

        self.assertNotEqual(response.status_code, 201)
        self.assertDictEqual(
            response.json(),
            {
                "detail": [
                    {"loc": ["body", "enrich_oncreation"], "msg": "field required", "type": "value_error.missing"},
                ]
            }
        )

    def test_create_ingestion_status_with_not_existing_request_id(self, *_):
        """ Test create ingestion status """
        request_url = "/v1/core-di-stats/create-ingestion-status"
        response = self._client.post(request_url, json={
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

        self.assertEqual(response.status_code, 400)
        self.assertIn("request_id", response.json()['message'])

    def test_create_ingestion_status_with_missing_field(self, *_):
        """ Test create ingestion status """
        request_url = "/v1/core-di-stats/create-ingestion-status"
        response = self._client.post(request_url, json={
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

        self.assertNotEqual(response.status_code, 201)
        self.assertDictEqual(
            response.json(),
            {
                "detail": [
                    {"loc": ["body", "request_id"], "msg": "field required", "type": "value_error.missing"},
                ]
            }
        )

    def test_create_and_get_ingestion_statuses(self, *_):
        """ Ingesting data for getting valid request_id """

        response = self._client.post("/v1/core-di-stats/ingest-data", json={
            "tenant_id": "test_tenant_id",
            "app_id": "test_app_id",
            "entity_type": "test_entity_type",
            "src_type": "test_src_type",
            "is_batch_required": True,
            "batch_size": 0,
            "subscriber_name": ["test_subscriber_name", "test_subscriber_name_2"],
            "enrich_oncreation": True
        })
        request_id = response.json()['request_id']

        """ Test create ingestion status"""
        request_url = "/v1/core-di-stats/create-ingestion-status"
        response = self._client.post(request_url, json={
            "request_id": request_id,
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

        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.json())

        """Test duplicate ingestion status"""
        response = self._client.post(request_url, json={
            "request_id": request_id,
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

        self.assertEqual(response.status_code, 400)
        self.assertIn("Duplicate entry", response.json()['message'])

    @patch('solution.sp.sql_base.db_client.DBClientSP.db_update_ingestion_status')
    def test_update_ingestion_status(self, db_update_ingestion_status: MagicMock, *_):
        """ Ingesting data for getting valid request_id """
        db_update_ingestion_status.return_value = True
        response = self._client.patch("/v1/core-di-stats/update-ingestion-status/test/test", json={
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

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), {'message': 'Ingestion status is updated successfully'})

    def test_update_ingestion_status_with_invalid_enum(self, *_):
        """ Test update ingestion status with invalid enum """
        request_url = "/v1/core-di-stats/update-ingestion-status/test/test"
        response = self._client.patch(request_url, json={
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

        self.assertNotEqual(response.status_code, 200)
        self.assertIn("value is not a valid enumeration member", response.json()['detail'][0]['msg'])

    @classmethod
    def tearDownClass(cls) -> None:
        try:
            cls._db.session.close_all()
            cls._db.engine.dispose()
            cls._db.engine = None
            cls._db.session = None
            cls._client.__exit__()
            import gc
            gc.collect()
        except Exception as e:
            print(e)
