import copy
import unittest

from settings import Settings


INITIAL = {"volume": 0.5, "bindings": {"jump": "Space", "fire": "J"}}


class SettingsTests(unittest.TestCase):
    def make_settings(self):
        writes, notices = [], []

        def writer(snapshot):
            writes.append(snapshot)
            return True

        return Settings(writer, notices.append), writes, notices

    def test_initial_state_and_deep_copy_property(self):
        settings, writes, notices = self.make_settings()
        snapshot = settings.values
        self.assertEqual(snapshot, INITIAL)
        snapshot["volume"] = 0
        snapshot["bindings"]["jump"] = "Q"
        snapshot["bindings"]["extra"] = "E"
        self.assertEqual(settings.values, INITIAL)
        self.assertIsNot(settings.values["bindings"], settings.values["bindings"])
        self.assertEqual((writes, notices), ([], []))

    def test_invalid_change_matrix_has_no_side_effects(self):
        invalid = [
            None, [], (), "volume", 0, True, {}, {"unknown": 1},
            {"volume": 0.6, "unknown": 1},
            {"volume": None}, {"volume": True}, {"volume": False},
            {"volume": "0.5"}, {"volume": []}, {"volume": 1 + 0j},
            {"volume": -0.01}, {"volume": 1.01},
            {"volume": float("nan")}, {"volume": float("inf")},
            {"volume": float("-inf")}, {"volume": 10 ** 1000},
            {"bindings": None}, {"bindings": []}, {"bindings": {}},
            {"bindings": {"dash": "D"}},
            {"bindings": {"jump": "Q", "dash": "D"}},
            {"bindings": {"jump": ""}}, {"bindings": {"jump": " \t\n"}},
            {"bindings": {"fire": 1}}, {"bindings": {"jump": True}},
            {"bindings": {"jump": None}},
            {"bindings": {"jump": "J"}},
            {"bindings": {"jump": "Q", "fire": "Q"}},
            {"volume": 0.8, "bindings": {"jump": "J"}},
            {"volume": -1, "bindings": {"jump": "Q"}},
        ]
        for changes in invalid:
            with self.subTest(changes=changes):
                settings, writes, notices = self.make_settings()
                self.assertIs(settings.apply(changes), False)
                self.assertEqual(settings.values, INITIAL)
                self.assertEqual((writes, notices), ([], []))

    def test_valid_volume_endpoints_ints_and_floats(self):
        for volume in (0, 1, 0.0, 1.0, 0.25):
            with self.subTest(volume=volume):
                settings, writes, notices = self.make_settings()
                self.assertIs(settings.apply({"volume": volume}), True)
                expected = dict(INITIAL, volume=volume)
                self.assertEqual(settings.values, expected)
                self.assertEqual(writes, [expected])
                self.assertEqual(notices, [expected])

    def test_patch_preserves_other_binding_and_passes_full_snapshot(self):
        settings, writes, notices = self.make_settings()
        changes = {"volume": 0.75, "bindings": {"jump": "Q"}}
        original = copy.deepcopy(changes)
        self.assertIs(settings.apply(changes), True)
        expected = {"volume": 0.75, "bindings": {"jump": "Q", "fire": "J"}}
        self.assertEqual(settings.values, expected)
        self.assertEqual(writes, [expected])
        self.assertEqual(notices, [expected])
        self.assertEqual(changes, original)
        changes["bindings"]["jump"] = "E"
        self.assertEqual(settings.values, expected)

    def test_duplicate_check_uses_resulting_bindings_and_allows_swap(self):
        settings, writes, notices = self.make_settings()
        self.assertIs(settings.apply({"bindings": {"jump": "J"}}), False)
        self.assertIs(settings.apply({"bindings": {"jump": "J", "fire": "Space"}}), True)
        expected = {"volume": 0.5, "bindings": {"jump": "J", "fire": "Space"}}
        self.assertEqual(writes, [expected])
        self.assertEqual(notices, [expected])
        self.assertEqual(settings.values, expected)

    def test_noops_do_not_call_callbacks(self):
        settings, writes, notices = self.make_settings()
        for change in (
            {"volume": 0.5}, {"bindings": {"jump": "Space"}},
            copy.deepcopy(INITIAL),
        ):
            self.assertIs(settings.apply(change), True)
        self.assertEqual((writes, notices), ([], []))
        self.assertEqual(settings.values, INITIAL)
        self.assertIs(settings.apply({"volume": 1}), True)
        self.assertIs(settings.apply({"volume": 1.0}), True)
        self.assertEqual((len(writes), len(notices)), (1, 1))

    def test_writer_must_return_exact_true_and_guard_is_released(self):
        class Truthy:
            def __bool__(self):
                raise AssertionError("The writer result must not be coerced to bool")

        for result in (False, None, 0, 1, 1.0, "yes", [], [True], {}, {"ok": True}, Truthy()):
            with self.subTest(result=type(result).__name__):
                notices, writes = [], []

                def writer(snapshot):
                    writes.append(copy.deepcopy(snapshot))
                    snapshot["bindings"]["jump"] = "CORRUPTED"
                    return result

                settings = Settings(writer, notices.append)
                self.assertIs(settings.apply({"volume": 0.7}), False)
                self.assertEqual(settings.values, INITIAL)
                self.assertEqual(notices, [])
                self.assertEqual(len(writes), 1)
                settings.writer = lambda snapshot: True
                self.assertIs(settings.apply({"volume": 0.8}), True)
                self.assertEqual(settings.values["volume"], 0.8)
                self.assertEqual(len(notices), 1)

    def test_writer_exception_leaves_state_and_input_unchanged(self):
        notices, attempts = [], []

        def writer(snapshot):
            attempts.append(copy.deepcopy(snapshot))
            snapshot["bindings"].clear()
            raise RuntimeError("storage unavailable")

        settings = Settings(writer, notices.append)
        changes = {"volume": 0.8, "bindings": {"fire": "F"}}
        original = copy.deepcopy(changes)
        self.assertIs(settings.apply(changes), False)
        self.assertEqual(settings.values, INITIAL)
        self.assertEqual(changes, original)
        self.assertEqual(notices, [])
        self.assertEqual(len(attempts), 1)
        settings.writer = lambda snapshot: True
        self.assertIs(settings.apply(changes), True)
        self.assertEqual(settings.values["bindings"], {"jump": "Space", "fire": "F"})

    def test_callbacks_get_independent_copies_and_commit_order(self):
        events, payloads = [], []
        expected = {"volume": 0.8, "bindings": {"jump": "Q", "fire": "J"}}

        def writer(snapshot):
            events.append("persist")
            self.assertEqual(settings.values, INITIAL)
            self.assertEqual(snapshot, expected)
            payloads.append(snapshot)
            snapshot["volume"] = 0
            snapshot["bindings"]["fire"] = "MUTATED"
            return True

        def listener(snapshot):
            events.append("notify")
            self.assertEqual(settings.values, expected)
            self.assertEqual(snapshot, expected)
            payloads.append(snapshot)
            snapshot["bindings"].clear()

        settings = Settings(writer, listener)
        self.assertIs(settings.apply({"volume": 0.8, "bindings": {"jump": "Q"}}), True)
        self.assertEqual(events, ["persist", "notify"])
        self.assertIsNot(payloads[0], payloads[1])
        self.assertIsNot(payloads[0]["bindings"], payloads[1]["bindings"])
        payloads[0]["bindings"]["jump"] = "AFTER_RETURN"
        payloads[1]["volume"] = 1
        self.assertEqual(settings.values, expected)

    def test_reentrant_writer_requests_are_rejected(self):
        nested, writes, notices = [], [], []

        def writer(snapshot):
            writes.append(snapshot)
            nested.append(settings.apply({"volume": 0.9}))
            nested.append(settings.apply({"volume": 0.5}))
            return True

        settings = Settings(writer, notices.append)
        self.assertIs(settings.apply({"volume": 0.7}), True)
        self.assertEqual(nested, [False, False])
        self.assertEqual(settings.values["volume"], 0.7)
        self.assertEqual((len(writes), len(notices)), (1, 1))
        settings.writer = lambda snapshot: True
        self.assertIs(settings.apply({"volume": 0.8}), True)

    def test_reentrant_listener_requests_are_rejected(self):
        writes, notices, nested = [], [], []

        def writer(snapshot):
            writes.append(snapshot)
            return True

        def listener(snapshot):
            notices.append(snapshot)
            nested.append(settings.apply({"volume": 0.9}))
            nested.append(settings.apply({"volume": 0.7}))

        settings = Settings(writer, listener)
        self.assertIs(settings.apply({"volume": 0.7}), True)
        self.assertEqual(nested, [False, False])
        self.assertEqual(settings.values["volume"], 0.7)
        self.assertEqual((len(writes), len(notices)), (1, 1))
        self.assertIs(settings.apply({"volume": 0.8}), True)
        self.assertEqual((len(writes), len(notices)), (2, 2))

    def test_listener_exception_keeps_commit_and_releases_guard(self):
        writes, notices, nested = [], [], []

        def writer(snapshot):
            writes.append(snapshot)
            return True

        def listener(snapshot):
            notices.append(snapshot)
            nested.append(settings.apply({"volume": 0.9}))
            snapshot["bindings"].clear()
            raise ValueError("view unavailable")

        settings = Settings(writer, listener)
        self.assertIs(settings.apply({"volume": 0.7}), True)
        self.assertEqual(settings.values, dict(INITIAL, volume=0.7))
        self.assertEqual(nested, [False])
        self.assertEqual((len(writes), len(notices)), (1, 1))
        self.assertIs(settings.apply({"volume": 0.8}), True)
        self.assertEqual(settings.values, dict(INITIAL, volume=0.8))
        self.assertEqual((len(writes), len(notices)), (2, 2))

    def test_failure_after_success_preserves_last_commit(self):
        settings, writes, notices = self.make_settings()
        self.assertIs(settings.apply({"bindings": {"fire": "F"}}), True)
        committed = settings.values
        settings.writer = lambda snapshot: False
        self.assertIs(settings.apply({"volume": 0.8, "bindings": {"fire": "K"}}), False)
        self.assertEqual(settings.values, committed)
        self.assertEqual((len(writes), len(notices)), (1, 1))


if __name__ == "__main__":
    unittest.main()
