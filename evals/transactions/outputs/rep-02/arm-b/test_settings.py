import unittest

from settings import Settings


INITIAL = {"volume": 0.5, "bindings": {"jump": "Space", "fire": "J"}}


class SettingsTransactionTests(unittest.TestCase):
    def make_settings(self, writer_result=True):
        writes = []
        notices = []

        def writer(snapshot):
            writes.append(snapshot)
            return writer_result

        return Settings(writer, notices.append), writes, notices

    def test_initial_values_are_independent_deep_copies(self):
        settings, writes, notices = self.make_settings()
        first = settings.values
        second = settings.values
        self.assertEqual(first, INITIAL)
        self.assertIsNot(first, second)
        self.assertIsNot(first["bindings"], second["bindings"])
        first["volume"] = 0
        first["bindings"]["jump"] = "Changed"
        self.assertEqual(settings.values, INITIAL)
        self.assertEqual((writes, notices), ([], []))

    def test_invalid_changes_never_write_notify_or_mutate(self):
        cases = [
            None, [], (), "volume", 0, True, {},
            {"unknown": 1}, {"volume": 0.8, "unknown": 1},
            {"volume": True}, {"volume": False}, {"volume": "0.8"},
            {"volume": None}, {"volume": []}, {"volume": -0.01},
            {"volume": 1.01}, {"volume": float("nan")},
            {"volume": float("inf")}, {"volume": float("-inf")},
            {"volume": 10 ** 1000},
            {"bindings": None}, {"bindings": []}, {"bindings": {}},
            {"bindings": {"dash": "K"}},
            {"bindings": {"jump": "K", "dash": "L"}},
            {"bindings": {"jump": ""}},
            {"bindings": {"jump": " \t\n"}},
            {"bindings": {"fire": 1}},
            {"bindings": {"jump": True}},
            {"bindings": {"jump": None}},
            {"bindings": {"jump": "J"}},
            {"bindings": {"jump": "K", "fire": "K"}},
            {"volume": 0.8, "bindings": {"jump": "J"}},
            {"volume": False, "bindings": {"jump": "K"}},
        ]
        for changes in cases:
            with self.subTest(changes=changes):
                settings, writes, notices = self.make_settings()
                self.assertIs(settings.apply(changes), False)
                self.assertEqual(settings.values, INITIAL)
                self.assertEqual((writes, notices), ([], []))

    def test_valid_volume_endpoints_and_fraction(self):
        for volume in (0, 1, 0.0, 1.0, 0.125):
            with self.subTest(volume=volume):
                settings, writes, notices = self.make_settings()
                self.assertIs(settings.apply({"volume": volume}), True)
                expected = {"volume": volume, "bindings": INITIAL["bindings"]}
                self.assertEqual(settings.values, expected)
                self.assertEqual(writes, [expected])
                self.assertEqual(notices, [expected])

    def test_binding_patch_preserves_other_binding_and_is_detached(self):
        settings, writes, notices = self.make_settings()
        patch = {"bindings": {"jump": "K"}}
        self.assertIs(settings.apply(patch), True)
        expected = {"volume": 0.5, "bindings": {"jump": "K", "fire": "J"}}
        patch["bindings"]["jump"] = "External mutation"
        self.assertEqual(settings.values, expected)
        self.assertEqual(writes, [expected])
        self.assertEqual(notices, [expected])

    def test_binding_swap_is_valid_and_subsequent_validation_uses_commit(self):
        settings, writes, notices = self.make_settings()
        self.assertIs(settings.apply({"bindings": {"jump": "J", "fire": "Space"}}), True)
        self.assertEqual(settings.values["bindings"], {"jump": "J", "fire": "Space"})
        self.assertIs(settings.apply({"bindings": {"fire": "J"}}), False)
        self.assertEqual(len(writes), 1)
        self.assertEqual(len(notices), 1)

    def test_nonblank_binding_strings_are_preserved(self):
        settings, _, _ = self.make_settings()
        self.assertIs(settings.apply({"bindings": {"jump": " K "}}), True)
        self.assertEqual(settings.values["bindings"]["jump"], " K ")

    def test_combined_change_persists_one_full_snapshot(self):
        settings, writes, notices = self.make_settings()
        expected = {"volume": 0.9, "bindings": {"jump": "K", "fire": "J"}}
        self.assertIs(settings.apply({"volume": 0.9, "bindings": {"jump": "K"}}), True)
        self.assertEqual(writes, [expected])
        self.assertEqual(notices, [expected])
        self.assertEqual(settings.values, expected)

    def test_valid_noops_do_not_persist_or_notify(self):
        settings, writes, notices = self.make_settings()
        for changes in (
            {"volume": 0.5},
            {"bindings": {"jump": "Space"}},
            {"volume": 0.5, "bindings": {"jump": "Space", "fire": "J"}},
        ):
            with self.subTest(changes=changes):
                self.assertIs(settings.apply(changes), True)
        self.assertEqual((writes, notices), ([], []))
        self.assertIs(settings.apply({"volume": 0.8}), True)
        self.assertIs(settings.apply({"volume": 0.8}), True)
        self.assertEqual(len(writes), 1)
        self.assertEqual(len(notices), 1)

    def test_only_exact_true_from_writer_commits(self):
        for result in (False, None, 0, 1, 1.0, "yes", [], [True], {}, {"ok": True}, object()):
            with self.subTest(result=result):
                settings, writes, notices = self.make_settings(result)
                self.assertIs(settings.apply({"volume": 0.9}), False)
                self.assertEqual(settings.values, INITIAL)
                self.assertEqual(writes, [{"volume": 0.9, "bindings": INITIAL["bindings"]}])
                self.assertEqual(notices, [])

    def test_writer_exception_keeps_state_and_releases_guard(self):
        calls = []
        notices = []

        def writer(snapshot):
            calls.append(snapshot)
            if len(calls) == 1:
                snapshot["bindings"].clear()
                raise RuntimeError("storage unavailable")
            return True

        settings = Settings(writer, notices.append)
        self.assertIs(settings.apply({"volume": 0.9}), False)
        self.assertEqual(settings.values, INITIAL)
        self.assertEqual(notices, [])
        self.assertIs(settings.apply({"volume": 0.7}), True)
        self.assertEqual(settings.values["volume"], 0.7)
        self.assertEqual(len(calls), 2)
        self.assertEqual(len(notices), 1)

    def test_writer_failure_then_success_releases_guard(self):
        returns = iter((False, True))
        notices = []
        settings = Settings(lambda snapshot: next(returns), notices.append)
        self.assertIs(settings.apply({"volume": 0.9}), False)
        self.assertIs(settings.apply({"volume": 0.8}), True)
        self.assertEqual(settings.values["volume"], 0.8)
        self.assertEqual(len(notices), 1)

    def test_callback_snapshots_are_separate_from_each_other_and_state(self):
        payloads = []
        listener_observed = []

        def writer(snapshot):
            payloads.append(snapshot)
            snapshot["volume"] = 0
            snapshot["bindings"]["jump"] = "Writer mutation"
            return True

        def listener(snapshot):
            listener_observed.append((snapshot["volume"], dict(snapshot["bindings"])))
            payloads.append(snapshot)
            snapshot["volume"] = 1
            snapshot["bindings"].clear()

        settings = Settings(writer, listener)
        self.assertIs(settings.apply({"volume": 0.8, "bindings": {"jump": "K"}}), True)
        expected = {"volume": 0.8, "bindings": {"jump": "K", "fire": "J"}}
        self.assertEqual(settings.values, expected)
        self.assertEqual(listener_observed, [(0.8, expected["bindings"])])
        self.assertIsNot(payloads[0], payloads[1])
        self.assertIsNot(payloads[0]["bindings"], payloads[1]["bindings"])
        payloads[0]["bindings"]["fire"] = "Retained reference mutation"
        payloads[1]["bindings"]["fire"] = "Another retained mutation"
        self.assertEqual(settings.values, expected)

    def test_failed_writer_mutation_does_not_touch_committed_state(self):
        notices = []

        def writer(snapshot):
            snapshot.clear()
            return False

        settings = Settings(writer, notices.append)
        self.assertIs(settings.apply({"volume": 0.9}), False)
        self.assertEqual(settings.values, INITIAL)
        self.assertEqual(notices, [])

    def test_writer_reads_old_state_listener_reads_committed_state_in_order(self):
        observations = []

        def writer(snapshot):
            observations.append(("persist", settings.values, snapshot))
            return True

        def listener(snapshot):
            observations.append(("notify", settings.values, snapshot))

        settings = Settings(writer, listener)
        self.assertIs(settings.apply({"volume": 0.9}), True)
        candidate = {"volume": 0.9, "bindings": INITIAL["bindings"]}
        self.assertEqual(observations, [("persist", INITIAL, candidate), ("notify", candidate, candidate)])

    def test_writer_and_listener_reentry_are_rejected_including_noops(self):
        events = []
        nested = []

        def writer(snapshot):
            events.append("persist")
            nested.append(settings.apply({"volume": 0.2}))
            nested.append(settings.apply({"volume": settings.values["volume"]}))
            return True

        def listener(snapshot):
            events.append("notify")
            nested.append(settings.apply({"bindings": {"fire": "L"}}))
            nested.append(settings.apply({"volume": snapshot["volume"]}))

        settings = Settings(writer, listener)
        self.assertIs(settings.apply({"volume": 0.9}), True)
        self.assertEqual(nested, [False, False, False, False])
        self.assertEqual(events, ["persist", "notify"])
        self.assertEqual(settings.values, {"volume": 0.9, "bindings": INITIAL["bindings"]})
        self.assertIs(settings.apply({"volume": 0.8}), True)
        self.assertEqual(events, ["persist", "notify", "persist", "notify"])

    def test_listener_exception_preserves_commit_and_releases_guard(self):
        writes = []
        notices = []

        def writer(snapshot):
            writes.append(snapshot)
            return True

        def listener(snapshot):
            notices.append(snapshot)
            snapshot["bindings"].clear()
            self.assertIs(settings.apply({"volume": 0.2}), False)
            raise ValueError("observer failed")

        settings = Settings(writer, listener)
        self.assertIs(settings.apply({"volume": 0.9}), True)
        self.assertEqual(settings.values, {"volume": 0.9, "bindings": INITIAL["bindings"]})
        self.assertIs(settings.apply({"volume": 0.8}), True)
        self.assertEqual(settings.values, {"volume": 0.8, "bindings": INITIAL["bindings"]})
        self.assertEqual(len(writes), 2)
        self.assertEqual(len(notices), 2)

    def test_failed_update_preserves_previously_committed_values(self):
        returns = iter((True, False))
        notices = []
        settings = Settings(lambda snapshot: next(returns), notices.append)
        self.assertIs(settings.apply({"volume": 0.8, "bindings": {"jump": "K"}}), True)
        committed = settings.values
        self.assertIs(settings.apply({"volume": 0.1, "bindings": {"fire": "L"}}), False)
        self.assertEqual(settings.values, committed)
        self.assertEqual(notices, [committed])


if __name__ == "__main__":
    unittest.main()
