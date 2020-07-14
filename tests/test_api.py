import aiohttp
import jwt
from aiohttp import web
from api import app
from api.authentication import (
    HASHING_ALGORITHM,
    SECRET_KEY,
    authenticate_user,
    create_access_token,
    get_current_user,
    hash_password,
)
from asynctest import TestCase, patch
from database import get_status
from fakeredis import FakeStrictRedis
from fastapi import HTTPException
from fastapi.testclient import TestClient


@patch("database.redis.Redis", FakeStrictRedis)
class TestAPI(TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_create_access_token_adds_expire(self):
        token = create_access_token({"a": 1, "b": 2}, 20)
        data = jwt.decode(token, SECRET_KEY, algorithms=[HASHING_ALGORITHM])
        self.assertEqual(data["a"], 1)
        self.assertEqual(data["b"], 2)
        self.assertTrue("exp" in data)

    def test_get_current_user_raises_credentials_exception_when_wrong_username(self):
        token = create_access_token({"sub": "username:{}".format("newuser")})
        self.assertRaises(HTTPException, get_current_user, token)

    def test_get_current_user_returns_user(self):
        with patch(
            "api.authentication.user_db",
            {"newuser": {"username": "newuser", "password": hash_password("123")}},
        ):
            token = create_access_token({"sub": "username:{}".format("newuser")})
            user = get_current_user(token)
            self.assertEqual(user.username, "newuser")
            self.assertTrue(authenticate_user("newuser", "123"))

    def test_get_current_user_raises_error_when_wrong_token(self):
        token = create_access_token({"bad_key": "username:{}".format("newuser")})
        self.assertRaises(HTTPException, get_current_user, token)

    def test_login_user_returns_400_when_not_existing_user(self):
        response = self.client.post(
            "/token",
            headers={
                "content-type": "application/x-www-form-urlencoded",
                "accept": "application/json",
            },
            data={"username": "newuser", "password": "123"},
        )
        self.assertEqual(response.status_code, 400)

    def test_login_user_returns_401_when_the_password_is_wrong(self):
        with patch(
            "api.authentication.user_db",
            {"newuser": {"username": "newuser", "password": hash_password("123")}},
        ):
            response = self.client.post(
                "/token",
                headers={
                    "content-type": "application/x-www-form-urlencoded",
                    "accept": "application/json",
                },
                data={"username": "newuser", "password": "122"},
            )
            self.assertEqual(response.status_code, 401)

    def test_login_user_returns_the_token_when_the_info_is_correct(self):
        with patch(
            "api.authentication.user_db",
            {"newuser": {"username": "newuser", "password": hash_password("123")}},
        ):
            response = self.client.post(
                "/token",
                headers={
                    "content-type": "application/x-www-form-urlencoded",
                    "accept": "application/json",
                },
                data={"username": "newuser", "password": "123"},
            )
            self.assertEqual(response.status_code, 200)

    def test_proxy_returns_502_when_remote_service_has_error(self):
        with patch(
            "api.authentication.user_db",
            {"newuser": {"username": "newuser", "password": hash_password("123")}},
        ):
            response = self.client.post(
                "/token",
                headers={
                    "content-type": "application/x-www-form-urlencoded",
                    "accept": "application/json",
                },
                data={"username": "newuser", "password": "123"},
            )

            def mock_post(*args, **kwargs):
                raise aiohttp.ClientConnectionError()

            with patch("api.proxy.aiohttp.ClientSession.post", mock_post):
                response = self.client.post(
                    "/",
                    headers={
                        "Authorization": "Bearer {}".format(
                            response.json()["access_token"]
                        )
                    },
                )
                self.assertEqual(response.status_code, 502)

    def test_proxy_returns_404_when_remote_service_doesnt_return_200(self):
        with patch(
            "api.authentication.user_db",
            {"newuser": {"username": "newuser", "password": hash_password("123")}},
        ):
            response = self.client.post(
                "/token",
                headers={
                    "content-type": "application/x-www-form-urlencoded",
                    "accept": "application/json",
                },
                data={"username": "newuser", "password": "123"},
            )

            async def mock_post(*args, **kwargs):
                return web.Response(text="", status=400)

            with patch("api.proxy.aiohttp.ClientSession.post", mock_post):
                response = self.client.post(
                    "/",
                    headers={
                        "Authorization": "Bearer {}".format(
                            response.json()["access_token"]
                        )
                    },
                )
                self.assertEqual(response.status_code, 404)

    def test_proxy_returns_200_when_succesful_and_update_status(self):
        with patch(
            "api.authentication.user_db",
            {"newuser": {"username": "newuser", "password": hash_password("123")}},
        ):
            response = self.client.post(
                "/token",
                headers={
                    "content-type": "application/x-www-form-urlencoded",
                    "accept": "application/json",
                },
                data={"username": "newuser", "password": "123"},
            )

            async def mock_post(*args, **kwargs):
                return web.Response(text="", status=200)

            self.assertEqual(get_status()["n_requests"], 0)
            with patch("api.proxy.aiohttp.ClientSession.post", mock_post):
                response = self.client.post(
                    "/",
                    headers={
                        "Authorization": "Bearer {}".format(
                            response.json()["access_token"]
                        )
                    },
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(get_status()["n_requests"], 1)
