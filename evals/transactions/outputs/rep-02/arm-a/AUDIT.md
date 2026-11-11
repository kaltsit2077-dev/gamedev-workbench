# Settings transaction audit

## Findings

- `values` exposed the owned dictionary and its nested binding map. Callers and callbacks could alter settings without a transaction.
- `apply` accepted arbitrary changes and updated owned state before persistence. Invalid data and failed saves could leave partial or invalid state behind.
- Binding replacement deleted actions omitted from a patch; there was no validation of duplicate resulting bindings.
- The writer result was ignored, so unsuccessful persistence still triggered notification and a successful return.
- Callback exceptions escaped; notification failure incorrectly prevented the successful return of an already persisted transaction.
- Callback reentry could start another transaction while the first was incomplete. No-op requests unnecessarily invoked both callbacks.

## Minimum architecture choice

Keep the existing synchronous `Settings(writer, listener)`, `values`, and `apply(changes)` interface. One private candidate builder validates the complete request and merges a binding patch into a copied snapshot. Validation and no-op detection occur before any callback. The candidate remains private until the writer returns the singleton `True`; all other return values and callback exceptions are failures at that boundary.

The commit is one assignment following successful persistence. The listener then receives its own deep copy, independently of the writer's copy. Notification errors cannot undo that commit or change the successful boolean result. The callback boundary catches `BaseException` deliberately to preserve the unqualified callback-error and boolean-result contract, including callback aborts. A single instance flag rejects reentrant calls, including no-ops, throughout persistence and notification; `finally` always releases it.

No persistence implementation, bus, scheduler, filesystem write, or dependency was added to production code. No general transaction framework is needed for this synchronous two-callback boundary.

## Verification coverage

The independent standard-library suite covers validation matrices, both numeric boundaries, non-finite and extremely large values, whitespace-only bindings, patch merging, binding swaps and duplicate rejection, combined-change atomicity, exact writer-success identity, full-snapshot persistence order, latest-state no-ops, nested copy ownership, caller mutation, reentry in both callbacks, failed-save recovery, and successful commits despite notification errors. Assertions about listener-observed data are made outside the listener so production exception handling cannot hide a test failure.

This verifies the in-memory transaction contract. It cannot make external writes transactional if a writer changes external storage and then reports failure. Thread safety, asynchronous callbacks, hostile subclasses overriding Python operations, and durability of a real storage backend are not exercised by this fixture.
