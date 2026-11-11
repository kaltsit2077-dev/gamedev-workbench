Repair a small game's settings transaction boundary. Settings(writer, listener) starts with volume 0.5 and bindings {jump: Space, fire: J}. The values property returns a deep copy. apply(changes) returns a bool.

1. Changes must be a nonempty dict containing only volume/bindings. Volume is a finite int/float in [0,1], never bool. Bindings is a nonempty dict patch containing only jump/fire; values are nonblank strings. Merge patches without deleting other bindings. Reject duplicate resulting bindings. Invalid changes return False and never persist/notify.
2. Persist a full candidate snapshot once; the writer must return exactly True for success. False, None, truthy non-bools or exceptions are failure. Failure leaves owned state unchanged and sends no notification.
3. Writer and listener receive separate deep copies and cannot mutate committed state. Notification occurs once after successful commit. A valid no-op returns True with no persistence or notification.
4. Reject reentrant apply while the transaction is persisting/notifying. Release that guard even after callback errors so a later valid request can succeed.
5. Listener exceptions do not roll back an already persisted commit: apply still returns True. No filesystem writes, global bus, async scheduler or new dependency.

Write AUDIT.md with findings and minimum architecture choice; RESULT.md with actual tests, limitations and measured elapsed time. Do not claim physical input or model fees.
