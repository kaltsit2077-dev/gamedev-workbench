import unittest

from settings import Settings


INITIAL = {"volume": 0.5, "bindings": {"jump": "Space", "fire": "J"}}


class SettingsTests(unittest.TestCase):
    def make_settings(self):
        written, notified = [], []

        def writer(snapshot):
            written.append(snapshot)
            return True

        settings = Settings(writer, notified.append)
        return settings, written, notified

    def test_initial_values_are_isolated_deep_copies(self):
        settings, written, notified = self.make_settings()
        snapshot = settings.values
        self.assertEqual(snapshot, INITIAL)
        snapshot["volume"] = 0
        snapshot["bindings"]["jump"] = "Changed"
        self.assertEqual(settings.values, INITIAL)
        self.assertIsNot(settings.values["bindings"], settings.values["bindings"])
        self.assertEqual((written, notified), ([], []))

    def test_invalid_changes_are_atomic_and_silent(self):
        invalid = [
            None, [], (), "volume", 1, True, {},
            {"unknown": 1}, {"volume": 0.8, "unknown": 1},
            {"volume": True}, {"volume": False}, {"volume": "0.8"},
            {"volume": None}, {"volume": 1j}, {"volume": -0.01},
            {"volume": 1.01}, {"volume": float("nan")},
            {"volume": float("inf")}, {"volume": float("-inf")},
            {"volume": 10 ** 1000}, {"volume": -(10 ** 1000)},
            {"bindings": None}, {"bindings": []}, {"bindings": {}},
            {"bindings": {"crouch": "C"}}, {"bindings": {"jump": ""}},
            {"bindings": {"jump": " \t\n"}}, {"bindings": {"jump": 2}},
            {"bindings": {"jump": True}}, {"bindings": {"jump": None}},
            {"bindings": {"jump": "J"}},
            {"bindings": {"jump": "K", "fire": "K"}},
            {"volume": 0.8, "bindings": {"jump": "J"}},
            {"volume": 0.8, "bindings": {"unknown": "U"}},
            {"volume": 0.8, "bindings": {}},
            {"volume": False, "bindings": {"jump": "K"}},
        ]
        for changes in invalid:
            with self.subTest(changes=changes):
                settings, written, notified = self.make_settings()
                self.assertIs(settings.apply(changes), False)
                self.assertEqual(settings.values, INITIAL)
                self.assertEqual((written, notified), ([], []))

    def test_numeric_boundaries_are_accepted(self):
        for volume in (0, 1, 0.0, 1.0, 0.125):
            with self.subTest(volume=volume):
                settings, written, notified = self.make_settings()
                self.assertIs(settings.apply({"volume": volume}), True)
                expected = {"volume": volume, "bindings": INITIAL["bindings"]}
                self.assertEqual(settings.values, expected)
                self.assertEqual(written, [expected])
                self.assertEqual(notified, [expected])

    def test_binding_patch_preserves_other_action_and_volume(self):
        settings, written, notified = self.make_settings()
        self.assertTrue(settings.apply({"bindings": {"jump": "K"}}))
        expected = {"volume": 0.5, "bindings": {"jump": "K", "fire": "J"}}
        self.assertEqual(settings.values, expected)
        self.assertEqual(written, [expected])
        self.assertEqual(notified, [expected])
        self.assertTrue(settings.apply({"bindings": {"fire": "L"}}))
        self.assertEqual(settings.values["bindings"], {"jump": "K", "fire": "L"})

    def test_binding_swap_checks_final_snapshot(self):
        settings, written, notified = self.make_settings()
        self.assertTrue(settings.apply({"bindings": {"jump": "J", "fire": "Space"}}))
        self.assertEqual(settings.values["bindings"], {"jump": "J", "fire": "Space"})
        self.assertEqual(len(written), 1)
        self.assertEqual(len(notified), 1)

    def test_nonblank_binding_text_is_preserved(self):
        settings, _, _ = self.make_settings()
        self.assertTrue(settings.apply({"bindings": {"jump": "  K  "}}))
        self.assertEqual(settings.values["bindings"]["jump"], "  K  ")

    def test_input_changes_remain_independent(self):
        settings, written, notified = self.make_settings()
        changes = {"volume": 0.75, "bindings": {"jump": "K"}}
        self.assertTrue(settings.apply(changes))
        changes["bindings"]["jump"] = "Modified later"
        changes["volume"] = 0
        expected = {"volume": 0.75, "bindings": {"jump": "K", "fire": "J"}}
        self.assertEqual(settings.values, expected)
        self.assertEqual(written, [expected])
        self.assertEqual(notified, [expected])

    def test_valid_noops_do_not_call_callbacks(self):
        settings, written, notified = self.make_settings()
        for changes in (
            {"volume": 0.5}, {"bindings": {"jump": "Space"}},
            {"bindings": {"jump": "Space", "fire": "J"}},
            {"volume": 0.5, "bindings": {"fire": "J"}},
        ):
            with self.subTest(changes=changes):
                self.assertIs(settings.apply(changes), True)
        self.assertEqual((written, notified), ([], []))

    def test_noop_after_commit_is_silent(self):
        settings, written, notified = self.make_settings()
        self.assertTrue(settings.apply({"volume": 0.25}))
        self.assertTrue(settings.apply({"volume": 0.25}))
        self.assertEqual(len(written), 1)
        self.assertEqual(len(notified), 1)

    def test_writer_must_return_exactly_true(self):
        class Truthy:
            def __bool__(self):
                return True

        for result in (False, None, 1, 0, "yes", [], [True], {}, {"ok": True}, Truthy()):
            with self.subTest(result=result):
                writes, notifications = [], []

                def writer(snapshot):
                    writes.append(snapshot)
                    return result

                settings = Settings(writer, notifications.append)
                self.assertIs(settings.apply({"volume": 0.8}), False)
                self.assertEqual(settings.values, INITIAL)
                self.assertEqual(len(writes), 1)
                self.assertEqual(notifications, [])

    def test_writer_exception_leaves_state_unchanged(self):
        notifications = []

        def writer(snapshot):
            snapshot["bindings"].clear()
            raise RuntimeError("storage unavailable")

        settings = Settings(writer, notifications.append)
        self.assertIs(settings.apply({"volume": 0.8}), False)
        self.assertEqual(settings.values, INITIAL)
        self.assertEqual(notifications, [])

    def test_failed_writer_cannot_mutate_owned_state(self):
        def writer(snapshot):
            snapshot["volume"] = 1
            snapshot["bindings"]["fire"] = "Hijacked"
            return False

        notifications = []
        settings = Settings(writer, notifications.append)
        self.assertFalse(settings.apply({"bindings": {"jump": "K"}}))
        self.assertEqual(settings.values, INITIAL)
        self.assertEqual(notifications, [])

    def test_commit_order_full_snapshots_and_callback_isolation(self):
        observations, payloads = [], []
        expected = {"volume": 0.8, "bindings": {"jump": "K", "fire": "J"}}

        def writer(snapshot):
            observations.append(("writer", settings.values, snapshot.copy()))
            payloads.append(snapshot)
            snapshot["bindings"]["fire"] = "Writer mutation"
            snapshot["volume"] = 0
            return True

        def listener(snapshot):
            observations.append(("listener", settings.values, snapshot.copy()))
            payloads.append(snapshot)
            snapshot["bindings"]["jump"] = "Listener mutation"
            snapshot["volume"] = 1

        settings = Settings(writer, listener)
        self.assertTrue(settings.apply({"volume": 0.8, "bindings": {"jump": "K"}}))
        self.assertEqual([entry[0] for entry in observations], ["writer", "listener"])
        self.assertEqual(observations[0][1], INITIAL)
        self.assertEqual(observations[1][1], expected)
        self.assertEqual(settings.values, expected)
        self.assertIsNot(payloads[0], payloads[1])
        self.assertIsNot(payloads[0]["bindings"], payloads[1]["bindings"])
        for payload in payloads:
            payload.clear()
        self.assertEqual(settings.values, expected)

    def test_listener_exception_preserves_commit_and_success(self):
        writes, notifications = [], []

        def writer(snapshot):
            writes.append(snapshot)
            return True

        def listener(snapshot):
            notifications.append(snapshot)
            snapshot["bindings"].clear()
            raise ValueError("observer failed")

        settings = Settings(writer, listener)
        self.assertIs(settings.apply({"volume": 0.8}), True)
        self.assertEqual(settings.values, {"volume": 0.8, "bindings": INITIAL["bindings"]})
        self.assertEqual(len(writes), 1)
        self.assertEqual(len(notifications), 1)

    def test_writer_reentrant_change_and_noop_are_rejected(self):
        nested, writes, notifications = [], [], []

        def writer(snapshot):
            writes.append(snapshot)
            nested.append(settings.apply({"volume": 0.2}))
            nested.append(settings.apply({"volume": 0.5}))
            return True

        settings = Settings(writer, notifications.append)
        self.assertTrue(settings.apply({"volume": 0.8}))
        self.assertEqual(nested, [False, False])
        self.assertEqual(settings.values["volume"], 0.8)
        self.assertEqual(len(writes), 1)
        self.assertEqual(len(notifications), 1)

    def test_listener_reentrant_change_and_noop_are_rejected(self):
        nested, writes, notifications = [], [], []

        def writer(snapshot):
            writes.append(snapshot)
            return True

        def listener(snapshot):
            notifications.append(snapshot)
            nested.append(settings.apply({"volume": 0.2}))
            nested.append(settings.apply({"volume": 0.8}))

        settings = Settings(writer, listener)
        self.assertTrue(settings.apply({"volume": 0.8}))
        self.assertEqual(nested, [False, False])
        self.assertEqual(settings.values["volume"], 0.8)
        self.assertEqual(len(writes), 1)
        self.assertEqual(len(notifications), 1)

    def test_guard_released_after_writer_failure_and_exception(self):
        for failure in (False, None, 1, RuntimeError("storage unavailable")):
            with self.subTest(failure=failure):
                attempts, notifications = [], []

                def writer(snapshot):
                    attempts.append(snapshot)
                    if len(attempts) == 1:
                        if isinstance(failure, Exception):
                            raise failure
                        return failure
                    return True

                settings = Settings(writer, notifications.append)
                self.assertFalse(settings.apply({"volume": 0.8}))
                self.assertTrue(settings.apply({"volume": 0.8}))
                self.assertEqual(settings.values["volume"], 0.8)
                self.assertEqual(len(attempts), 2)
                self.assertEqual(len(notifications), 1)

    def test_guard_released_after_listener_exception(self):
        writes, notifications = [], []

        def writer(snapshot):
            writes.append(snapshot)
            return True

        def listener(snapshot):
            notifications.append(snapshot)
            if len(notifications) == 1:
                raise RuntimeError("observer failed")

        settings = Settings(writer, listener)
        self.assertTrue(settings.apply({"volume": 0.8}))
        self.assertTrue(settings.apply({"bindings": {"jump": "K"}}))
        self.assertEqual(settings.values, {"volume": 0.8, "bindings": {"jump": "K", "fire": "J"}})
        self.assertEqual(len(writes), 2)
        self.assertEqual(len(notifications), 2)

    def test_failed_update_preserves_previous_committed_snapshot(self):
        outcomes = iter((True, False, True))
        writes, notifications = [], []

        def writer(snapshot):
            writes.append(snapshot)
            return next(outcomes)

        settings = Settings(writer, notifications.append)
        self.assertTrue(settings.apply({"bindings": {"jump": "K"}}))
        self.assertFalse(settings.apply({"volume": 0.8, "bindings": {"fire": "L"}}))
        self.assertEqual(settings.values, {"volume": 0.5, "bindings": {"jump": "K", "fire": "J"}})
        self.assertTrue(settings.apply({"volume": 0.9}))
        self.assertEqual(settings.values, {"volume": 0.9, "bindings": {"jump": "K", "fire": "J"}})
        self.assertEqual(len(writes), 3)
        self.assertEqual(len(notifications), 2)


if __name__ == "__main__":
    unittest.main()
