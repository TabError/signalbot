import pytest

from tests.unit.conftest import TestCommon


class TestUsernameValidation(TestCommon):
    @pytest.mark.parametrize(
        "username",
        [
            "Usr.99",
            "UserName.99",
            "username.999999999",
            "UserName99.99",
            "_Use_rName99_.99",
            "usernameeeeeeeeeeeeeeeeeeeeeeeee.999999999",
        ],
    )
    def test_valid_username(self, username: str):
        assert self.signal_bot._recipients._is_username(username)

    @pytest.mark.parametrize(
        "username",
        [
            "Us.99",
            "Usr.9",
            ".UserName99",
            ".UserName.99",
            "UserName99",
            "UserName99.",
            "username.9999999999",
            "user@name.999",
            "UserName99.0",
            "UserName99.00",
            "UserName99.000000000",
            ".usernameeeeeeeeeeeeeeeeeeeeeeeeee.99",
        ],
    )
    def test_invalid_username(self, username: str):
        assert not self.signal_bot._recipients._is_username(username)
