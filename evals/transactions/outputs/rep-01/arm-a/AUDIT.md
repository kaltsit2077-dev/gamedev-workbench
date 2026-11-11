# Settings transaction audit

## Findings

The original `values` property returned the owned dictionary directly. Callers could therefore bypass validation and change nested bindings. The original `apply` changed owned state before checking input or storage success, replaced rather than merged nested bindings, ignored the writer result, exposed owned state to both callbacks, and had no reentrancy protection. Callback errors could escape without the required transaction semantics.

## Minimum architecture choice

Keep one synchronous `Settings` class and preserve its constructor, `values`, and `apply` interface. Add only standard-library `deepcopy` and `isfinite` plus a per-instance transaction guard. No persistence implementation, filesystem access, event bus, scheduler, dependencies, or additional service layer is introduced in production code.

`apply` validates a private full candidate before invoking callbacks. Binding patches merge into that candidate, and duplicate detection considers its final bindings, allowing a valid two-action swap. Volume validation rejects bool, nonnumeric, nonfinite, and out-of-range values; checking range before finiteness also safely rejects enormous integers. Nonblank binding strings retain their supplied text, since trimming or case normalization is not required.

A valid no-op returns success without calling either callback. Otherwise the guard covers persistence, commit, and notification. Persistence receives a deep copy, runs once, and succeeds only with the singleton `True`. Failure leaves the previous owned snapshot intact. The owned candidate is committed before notification; the listener receives a separate deep copy. Ordinary callback exceptions are contained according to the writer/listener rules, and `finally` always releases the guard. Nested requests, including nested no-ops, return `False` during either callback.

## Evidence and scope

The independent `test_settings.py` suite tests public behavior with recording, failing, mutating, and reentrant callbacks. It checks complete snapshot contents, old-versus-committed visibility during callbacks, retained callback-payload isolation, incremental patches and swaps, invalid mixed changes, exact writer success, and recovery after errors.

This is a synchronous, in-process boundary. It cannot undo external side effects of a writer that performs work and then reports failure; it does preserve the class-owned state. Thread coordination, physical game input, real storage integrations, and process-control exceptions such as `KeyboardInterrupt` were not evaluated or added to the stated interface.
