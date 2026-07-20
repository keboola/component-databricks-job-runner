import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from keboola.component.exceptions import UserException  # noqa: E402

from configuration import AuthType, Configuration  # noqa: E402


class TestConfiguration(unittest.TestCase):
    def test_token_auth_valid(self):
        cfg = Configuration(**{"#api_token": "secret", "base_url": "https://dbx", "job_id": "5"})
        self.assertEqual(cfg.auth_type, AuthType.TOKEN)
        self.assertEqual(cfg.api_token, "secret")
        self.assertEqual(cfg.job_id, 5)

    def test_token_auth_missing_token_fails(self):
        with self.assertRaises(UserException):
            Configuration(**{"auth_type": "token", "base_url": "https://dbx"})

    def test_service_principal_valid(self):
        cfg = Configuration(
            **{
                "auth_type": "service_principal",
                "client_id": "client-id",
                "#client_secret": "client-secret",
                "base_url": "https://dbx",
            }
        )
        self.assertEqual(cfg.auth_type, AuthType.SERVICE_PRINCIPAL)
        self.assertEqual(cfg.client_id, "client-id")
        self.assertEqual(cfg.client_secret, "client-secret")

    def test_job_parameters_default_empty(self):
        cfg = Configuration(**{"#api_token": "secret", "base_url": "https://dbx"})
        self.assertEqual(cfg.job_parameters, [])
        self.assertEqual(cfg.job_parameters_dict(), {})

    def test_job_parameters_parsed_to_dict(self):
        cfg = Configuration(
            **{
                "#api_token": "secret",
                "base_url": "https://dbx",
                "job_parameters": [
                    {"key": "environment", "value": "production"},
                    {"key": "run_date", "value": "2026-07-20"},
                    {"key": "", "value": "ignored"},
                ],
            }
        )
        self.assertEqual(
            cfg.job_parameters_dict(),
            {"environment": "production", "run_date": "2026-07-20"},
        )

    def test_service_principal_missing_credentials_fails(self):
        with self.assertRaises(UserException):
            Configuration(**{"auth_type": "service_principal", "client_id": "client-id", "base_url": "https://dbx"})
        with self.assertRaises(UserException):
            Configuration(
                **{"auth_type": "service_principal", "#client_secret": "secret", "base_url": "https://dbx"}
            )


if __name__ == "__main__":
    unittest.main()
