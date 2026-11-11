import copy
import unittest

from settings import Settings


INITIAL = {"volume": 0.5, "bindings": {"jump": "Space", "fire": "J"}}


class SettingsTests(unittest.TestCase):
    def make_settings(self, writer_result=True):
        writes = []
        notifications = []

        def writer(snapshot):
            writes.append(snapshot)
            return writer_result

        return Settings(writer, notifications.append), writes, notifications

    def test_initial_values_and_instances_are_independent(self):
        first, writes, notes = self.make_settings()
        second, _, _ = self.make_settings()
        self.assertEqual(first.values, INITIAL)
        self.assertEqual((writes, notes), ([], []))
        self.assertTrue(first.apply({"bindings": {"jump": "K"}}))
        self.assertEqual(second.values, INITIAL)

    def test_values_is_a_deep_copy(self):
        settings, _, _ = self.make_settings()
        exposed = settings.values
        exposed["volume"] = 0
        exposed["bindings"]["jump"] = "K"
        exposed["bindings"].clear()
        self.assertEqual(settings.values, INITIAL)
        self.assertIsNot(settings.values, settings.values)

    def test_invalid_outer_changes_never_call_callbacks(self):
        for changes in (None, [], (), "volume", 0, True, {}, {"other": 1},
                        {"volume": 0.8, "other": 1}):
            with self.subTest(changes=changes):
                settings, writes, notes = self.make_settings()
                self.assertIs(settings.apply(changes), False)
                self.assertEqual(settings.values, INITIAL)
                self.assertEqual((writes, notes), ([], []))

    def test_invalid_volume_never_calls_callbacks(self):
        for volume in (True, False, None, "0.5", [], {}, complex(0.5),
                       float("nan"), float("inf"), float("-inf"),
                       -0.0001, 1.0001, 10**1000, -(10**1000)):
            with self.subTest(volume=volume):
                settings, writes, notes = self.make_settings()
                self.assertIs(settings.apply({"volume": volume}), False)
                self.assertEqual(settings.values, INITIAL)
                self.assertEqual((writes, notes), ([], []))

    def test_volume_boundaries_and_finite_fraction_succeed(self):
        for volume in (0, 1, 0.0, 1.0, 0.001, 0.999):
            with self.subTest(volume=volume):
                settings, writes, notes = self.make_settings()
                self.assertIs(settings.apply({"volume": volume}), True)
                expected = {"volume": volume, "bindings": INITIAL["bindings"]}
                self.assertEqual(settings.values, expected)
                self.assertEqual(writes, [expected])
                self.assertEqual(notes, [expected])

    def test_invalid_binding_patch_never_calls_callbacks(self):
        for patch in (None, [], (), "K", {}, {"dash": "K"},
                      {"jump": "K", "dash": "L"}, {"jump": ""},
                      {"jump": " \t\n"}, {"fire": "\u2003"},
                      {"jump": 2}, {"jump": None}, {"fire": True},
                      {"fire": []}):
            with self.subTest(patch=patch):
                settings, writes, notes = self.make_settings()
                self.assertIs(settings.apply({"bindings": patch}), False)
                self.assertEqual(settings.values, INITIAL)
                self.assertEqual((writes, notes), ([], []))

    def test_binding_patch_preserves_other_action(self):
        settings, writes, notes = self.make_settings()
        self.assertTrue(settings.apply({"bindings": {"jump": "K"}}))
        expected = {"volume": 0.5, "bindings": {"jump": "K", "fire": "J"}}
        self.assertEqual(settings.values, expected)
        self.assertEqual(writes, [expected])
        self.assertEqual(notes, [expected])

    def test_nonblank_binding_is_preserved_verbatim(self):
        settings, _, _ = self.make_settings()
        self.assertTrue(settings.apply({"bindings": {"fire": "  F  "}}))
        self.assertEqual(settings.values["bindings"]["fire"], "  F  ")

    def test_duplicate_bindings_rejected_against_merged_result(self):
        for patch in ({"jump": "J"}, {"fire": "Space"},
                      {"jump": "K", "fire": "K"}):
            with self.subTest(patch=patch):
                settings, writes, notes = self.make_settings()
                self.assertIs(settings.apply({"bindings": patch}), False)
                self.assertEqual(settings.values, INITIAL)
                self.assertEqual((writes, notes), ([], []))

    def test_binding_swap_is_one_atomic_valid_patch(self):
        settings, writes, notes = self.make_settings()
        self.assertTrue(settings.apply({"bindings": {"jump": "J", "fire": "Space"}}))
        expected = {"volume": 0.5, "bindings": {"jump": "J", "fire": "Space"}}
        self.assertEqual(settings.values, expected)
        self.assertEqual(writes, [expected])
        self.assertEqual(notes, [expected])

    def test_invalid_combined_changes_do_not_partially_apply(self):
        for changes in ({"volume": 0.8, "bindings": {"jump": "J"}},
                        {"volume": False, "bindings": {"jump": "K"}},
                        {"volume": 0.8, "bindings": {}}):
            with self.subTest(changes=changes):
                settings, writes, notes = self.make_settings()
                self.assertIs(settings.apply(changes), False)
                self.assertEqual(settings.values, INITIAL)
                self.assertEqual((writes, notes), ([], []))

    def test_full_snapshot_persisted_once_before_commit_then_notification(self):
        events = []

        def writer(snapshot):
            events.append(("write", copy.deepcopy(snapshot), settings.values))
            return True

        def listener(snapshot):
            events.append(("notify", copy.deepcopy(snapshot), settings.values))

        settings = Settings(writer, listener)
        changes = {"volume": 0.8, "bindings": {"fire": "F"}}
        expected = {"volume": 0.8, "bindings": {"jump": "Space", "fire": "F"}}
        self.assertIs(settings.apply(changes), True)
        self.assertEqual(events, [("write", expected, INITIAL),
                                  ("notify", expected, expected)])
        self.assertEqual(settings.values, expected)
        self.assertEqual(changes, {"volume": 0.8, "bindings": {"fire": "F"}})

    def test_no_op_returns_true_without_any_callback(self):
        for changes in ({"volume": 0.5}, {"bindings": {"jump": "Space"}},
                        copy.deepcopy(INITIAL)):
            with self.subTest(changes=changes):
                settings, writes, notes = self.make_settings(writer_result=False)
                self.assertIs(settings.apply(changes), True)
                self.assertEqual(settings.values, INITIAL)
                self.assertEqual((writes, notes), ([], []))

    def test_no_op_is_relative_to_latest_commit(self):
        settings, writes, notes = self.make_settings()
        self.assertTrue(settings.apply({"volume": 0.8, "bindings": {"fire": "F"}}))
        self.assertTrue(settings.apply({"volume": 0.8}))
        self.assertTrue(settings.apply({"bindings": {"fire": "F"}}))
        self.assertEqual(len(writes), 1)
        self.assertEqual(len(notes), 1)

    def test_every_writer_result_other_than_true_is_failure(self):
        for result in (False, None, 0, 1, 1.0, "yes", [True], {"ok": True}, object()):
            with self.subTest(result=result):
                settings, writes, notes = self.make_settings(writer_result=result)
                self.assertIs(settings.apply({"volume": 0.8}), False)
                self.assertEqual(settings.values, INITIAL)
                self.assertEqual(len(writes), 1)
                self.assertEqual(notes, [])

    def test_writer_failure_preserves_previously_committed_state(self):
        settings, writes, notes = self.make_settings()
        self.assertTrue(settings.apply({"bindings": {"fire": "F"}}))
        committed = settings.values
        settings.writer = lambda snapshot: False
        self.assertFalse(settings.apply({"volume": 0.8, "bindings": {"jump": "K"}}))
        self.assertEqual(settings.values, committed)
        self.assertEqual(len(writes), 1)
        self.assertEqual(len(notes), 1)

    def test_writer_exception_leaves_state_and_releases_guard(self):
        calls = []

        def writer(snapshot):
            calls.append(snapshot)
            if len(calls) == 1:
                snapshot["bindings"].clear()
                raise RuntimeError("disk rejected save")
            return True

        notes = []
        settings = Settings(writer, notes.append)
        self.assertIs(settings.apply({"volume": 0.8}), False)
        self.assertEqual(settings.values, INITIAL)
        self.assertEqual(notes, [])
        self.assertIs(settings.apply({"volume": 0.9}), True)
        self.assertEqual(settings.values["volume"], 0.9)
        self.assertEqual(len(calls), 2)
        self.assertEqual(len(notes), 1)

    def test_nontrue_writer_return_releases_guard(self):
        settings, _, notes = self.make_settings(writer_result=None)
        self.assertIs(settings.apply({"volume": 0.8}), False)
        settings.writer = lambda snapshot: True
        self.assertIs(settings.apply({"volume": 0.9}), True)
        self.assertEqual(len(notes), 1)

    def test_callback_baseexceptions_keep_bool_contract_and_release_guard(self):
        class CallbackAbort(BaseException):
            pass

        def abort(snapshot):
            raise CallbackAbort("callback aborted")

        for phase in ("writer", "listener"):
            with self.subTest(phase=phase):
                settings, writes, notes = self.make_settings()
                setattr(settings, phase, abort)
                self.assertIs(settings.apply({"volume": 0.8}), phase == "listener")
                self.assertEqual(settings.values["volume"],
                                 0.8 if phase == "listener" else 0.5)
                self.assertEqual(len(writes), 1 if phase == "listener" else 0)
                self.assertEqual(notes, [])
                settings.writer = lambda snapshot: True
                settings.listener = notes.append
                self.assertIs(settings.apply({"volume": 0.9}), True)
                self.assertEqual(len(notes), 1)

    def test_callbacks_receive_independent_owned_snapshots(self):
        held = {}

        def writer(snapshot):
            held["writer"] = snapshot
            snapshot["volume"] = 0
            snapshot["bindings"]["jump"] = "X"
            return True

        def listener(snapshot):
            held["listener"] = snapshot
            held["listener_received"] = copy.deepcopy(snapshot)
            held["listener_observed_state"] = settings.values
            snapshot["volume"] = 1
            snapshot["bindings"].clear()

        settings = Settings(writer, listener)
        expected = {"volume": 0.8, "bindings": {"jump": "Space", "fire": "F"}}
        self.assertTrue(settings.apply({"volume": 0.8, "bindings": {"fire": "F"}}))
        self.assertEqual(held["listener_received"], expected)
        self.assertEqual(held["listener_observed_state"], expected)
        self.assertIsNot(held["writer"], held["listener"])
        self.assertIsNot(held["writer"]["bindings"], held["listener"]["bindings"])
        held["writer"].clear()
        held["listener"].clear()
        self.assertEqual(settings.values, expected)

    def test_caller_mutation_after_commit_does_not_affect_state(self):
        settings, _, _ = self.make_settings()
        changes = {"bindings": {"jump": "K"}}
        self.assertTrue(settings.apply(changes))
        changes["bindings"]["jump"] = "X"
        changes["volume"] = 0
        self.assertEqual(settings.values,
                         {"volume": 0.5, "bindings": {"jump": "K", "fire": "J"}})

    def test_writer_reentry_rejected_even_for_valid_no_op(self):
        nested = []
        writes = []
        notes = []

        def writer(snapshot):
            writes.append(snapshot)
            nested.append(settings.apply({"volume": 0.9}))
            nested.append(settings.apply({"volume": 0.5}))
            return True

        settings = Settings(writer, notes.append)
        self.assertTrue(settings.apply({"volume": 0.8}))
        self.assertEqual(nested, [False, False])
        self.assertEqual(settings.values["volume"], 0.8)
        self.assertEqual(len(writes), 1)
        self.assertEqual(len(notes), 1)

    def test_listener_reentry_rejected_then_later_apply_succeeds(self):
        nested = []
        writes = []

        def listener(snapshot):
            nested.append(settings.apply({"bindings": {"jump": "K"}}))
            nested.append(settings.apply({"volume": snapshot["volume"]}))

        settings = Settings(lambda snapshot: writes.append(snapshot) or True, listener)
        self.assertIs(settings.apply({"volume": 0.8}), True)
        self.assertEqual(nested, [False, False])
        settings.listener = lambda snapshot: None
        self.assertIs(settings.apply({"bindings": {"jump": "K"}}), True)
        self.assertEqual(len(writes), 2)
        self.assertEqual(settings.values["bindings"]["jump"], "K")

    def test_listener_exception_preserves_commit_and_releases_guard(self):
        writes = []
        notifications = []

        def listener(snapshot):
            notifications.append(snapshot)
            snapshot["bindings"].clear()
            raise ValueError("UI failed")

        settings = Settings(lambda snapshot: writes.append(snapshot) or True, listener)
        self.assertIs(settings.apply({"volume": 0.8}), True)
        self.assertEqual(settings.values, {"volume": 0.8, "bindings": INITIAL["bindings"]})
        self.assertIs(settings.apply({"bindings": {"fire": "F"}}), True)
        self.assertEqual(settings.values,
                         {"volume": 0.8, "bindings": {"jump": "Space", "fire": "F"}})
        self.assertEqual(len(writes), 2)
        self.assertEqual(len(notifications), 2)

    def test_multiple_valid_patches_merge_against_latest_state(self):
        settings, writes, notes = self.make_settings()
        self.assertTrue(settings.apply({"bindings": {"jump": "K"}}))
        self.assertTrue(settings.apply({"volume": 0.7}))
        self.assertTrue(settings.apply({"bindings": {"fire": "F"}}))
        expected = {"volume": 0.7, "bindings": {"jump": "K", "fire": "F"}}
        self.assertEqual(settings.values, expected)
        self.assertEqual(writes[-1], expected)
        self.assertEqual(notes[-1], expected)
        self.assertEqual(len(writes), 3)
        self.assertEqual(len(notes), 3)


if __name__ == "__main__":
    unittest.main()
