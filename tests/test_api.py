from unittest import TestCase
from unittest.mock import patch

import jwt
from api import app
from api.authentication import (HASHING_ALGORITHM, SECRET_KEY,
                                authenticate_user, create_access_token,
                                get_current_user, hash_password)
from fakeredis import FakeStrictRedis
from fastapi import HTTPException
from fastapi.testclient import TestClient


@patch("database.database", FakeStrictRedis())
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
        