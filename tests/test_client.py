import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dbx.client import DataBricksClient, DataBricksClientClientException  # noqa: E402


def _token_response(access_token="oauth-token", expires_in=3600):
    resp = mock.Mock()
    resp.raise_for_status = mock.Mock()
    resp.json = mock.Mock(return_value={"access_token": access_token, "expires_in": expires_in})
    return resp


class TestDataBricksClientOAuth(unittest.TestCase):
    @mock.patch("dbx.client.requests.post")
    def test_oauth_token_fetched_on_init(self, mock_post):
        mock_post.return_value = _token_response("oauth-token")
        client = DataBricksClient(
            "https://dbx", ssl_verify=True, client_id="cid", client_secret="csecret"
        )
        self.assertTrue(client._use_oauth)
        self.assertEqual(client.token, "oauth-token")
        # Called the workspace OIDC token endpoint with client-credentials grant.
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://dbx/oidc/v1/token")
        self.assertEqual(kwargs["auth"], ("cid", "csecret"))
        self.assertEqual(kwargs["data"]["grant_type"], "client_credentials")
        self.assertEqual(client._auth_header["Authorization"], "Bearer oauth-token")

    @mock.patch("dbx.client.requests.post")
    def test_token_auth_does_not_call_oauth(self, mock_post):
        client = DataBricksClient("https://dbx", ssl_verify=True, token="pat-token")
        self.assertFalse(client._use_oauth)
        self.assertEqual(client.token, "pat-token")
        mock_post.assert_not_called()

    @mock.patch("dbx.client.requests.post")
    def test_ensure_token_refreshes_when_expired(self, mock_post):
        mock_post.side_effect = [_token_response("token-1"), _token_response("token-2")]
        client = DataBricksClient("https://dbx", ssl_verify=True, client_id="cid", client_secret="csecret")
        self.assertEqual(client.token, "token-1")

        # Force expiry and ensure a refresh occurs and the auth header is updated.
        client._oauth_expires_at = 0.0
        client._ensure_token()
        self.assertEqual(client.token, "token-2")
        self.assertEqual(client._auth_header["Authorization"], "Bearer token-2")
        self.assertEqual(mock_post.call_count, 2)

    @mock.patch("dbx.client.requests.post")
    def test_missing_access_token_raises(self, mock_post):
        resp = mock.Mock()
        resp.raise_for_status = mock.Mock()
        resp.json = mock.Mock(return_value={})
        mock_post.return_value = resp
        with self.assertRaises(DataBricksClientClientException):
            DataBricksClient("https://dbx", ssl_verify=True, client_id="cid", client_secret="csecret")


if __name__ == "__main__":
    unittest.main()
