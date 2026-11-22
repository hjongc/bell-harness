# Keep one local receipt per event

Update the receipt CLI so retrying an event in a separate invocation preserves the receipt from the first successful invocation.

Run it as `python3 receipts.py STATE_PATH EVENT_JSON`. The event is a JSON object with a nonempty string `id` and a string `message`. The state file starts absent or contains a valid list written by the CLI. Store a JSON list of objects with `id` and `message`, in the order distinct events first succeed. Either a first delivery or a retry exits 0. On a retry, leave the state file byte-for-byte unchanged even if the incoming message changed.

For malformed JSON or an event that does not meet the schema, exit 2 and include `invalid event` in stderr. Leave existing state unchanged. If the state file was absent, leave it absent.

Edit only `receipts.py`. Use the Python 3.9 standard library and local temporary data for verification.
