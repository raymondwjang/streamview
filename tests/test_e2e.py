import pytest

from streamview.runner import Runner
from streamview.socket_manager import ConnectionManager


class TestE2e:

    @pytest.fixture
    def manager(self):
        return ConnectionManager()

    @pytest.fixture
    def runner(self):
        return Runner()

    def test_pipeline(self, runner, manager):
        runner.run_streamers(manager)
