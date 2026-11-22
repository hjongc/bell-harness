import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Record a local event receipt.")
    parser.add_argument("state_path", type=Path)
    parser.add_argument("event_json")
    args = parser.parse_args()

    try:
        event = json.loads(args.event_json)
    except json.JSONDecodeError:
        parser.error("invalid event")
    if (not isinstance(event, dict)
            or not isinstance(event.get("id"), str) or not event["id"]
            or not isinstance(event.get("message"), str)):
        parser.error("invalid event")

    records = json.loads(args.state_path.read_text(encoding="utf-8")) if args.state_path.exists() else []
    records.append({"id": event["id"], "message": event["message"]})
    args.state_path.write_text(json.dumps(records, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
