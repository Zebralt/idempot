# Idempotency ?

An attempt to design an easy way to render batch (or any) processes idempotent, which is that were their execution abruptly interrupted in the middle, say by the raising of an exception or a outside cause:

* the successfully computed cases should be memoized outside of runtime (so, serialized);
* the program should be able to pick up where it left off, rather than re-compute the cases from previous point;
* in the case of batch jobs, it could be interesting to detect whether the function has been modified, which means checksuming its source code to detect any changes; this would required auto-fomatting to avoid taking whitespace or comments into account;