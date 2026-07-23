import unittest
import mock
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from keboola.component.exceptions import UserException  # noqa: E402

from component import Component  # noqa: E402


class TestComponent(unittest.TestCase):
    # set KBC_DATADIR env to non-existing dir
    @mock.patch.dict(os.environ, {"KBC_DATADIR": "./non-existing-dir"})
    def test_run_no_cfg_fails(self):
        with self.assertRaises(ValueError):
            comp = Component()
            comp.run()

    def _component_with_client(self, jobs):
        # Bypass ComponentBase.__init__ and inject a mocked Databricks client.
        comp = Component.__new__(Component)
        comp.dbx_client = mock.Mock()
        comp.dbx_client.get_jobs.return_value = jobs
        return comp

    # Call the undecorated function (`@sync_action` wraps it with @wraps, exposing __wrapped__)
    # so we exercise the logic without the ComponentBase sync-action machinery.
    def test_list_jobs_raises_when_no_jobs(self):
        comp = self._component_with_client([])
        with self.assertRaises(UserException):
            Component.list_jobs.__wrapped__(comp)

    def test_list_jobs_returns_select_elements(self):
        comp = self._component_with_client(
            [
                {"job_id": 111, "settings": {"name": "First job"}},
                {"job_id": 222, "settings": {"name": "Second job"}},
            ]
        )
        result = Component.list_jobs.__wrapped__(comp)
        self.assertEqual([(e.value, e.label) for e in result], [("111", "First job"), ("222", "Second job")])


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
