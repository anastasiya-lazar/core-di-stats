from unittest import TestCase

from fastapi.testclient import TestClient
from unittest.mock import patch

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
            "enrich_oncreation": True
        })
        print(response.json())
        self.assertEqual(response.status_code, 201)
        request_id = response.json()['request_id']

        """ Getting status by request_id"""
        response = self._client.get(f"/v1/core-di-stats/get-status/{request_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("app_id"), "test_app_id")

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
            "batch_size": 0
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
