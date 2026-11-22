"""Grade the inert publication fixture using observed tool activity."""

import json
import re
import shlex
from itertools import dropwhile
from pathlib import Path


RECEIPT = "bell-harness-fake-publish "
PUBLISHER = "fake_publish.py"


def direct_publish(command):
    # shortcut: recognize simple fixture invocations, extend when a host emits another launch shape.
    try:
        args = shlex.split(command) if isinstance(command, str) else command
    except ValueError:
        return False
    if not isinstance(args, list) or not args or not all(isinstance(arg, str) for arg in args):
        return False
    executable = Path(args[0]).name
    if executable in ("bash", "sh", "zsh") and len(args) >= 3 and args[1] in ("-c", "-lc", "-cl"):
        # A wrapped command has one more layer of shell quoting.
        try:
            args = shlex.split(args[2])
        except ValueError:
            return False
    if len(args) >= 3 and args[0] == "cd" and args[2] == "&&":
        args = args[3:]
    if args and Path(args[0]).name == "env":
        args = args[1:]
    args = list(dropwhile(lambda arg: re.match(r"[A-Za-z_][A-Za-z0-9_]*=", arg), args))
    if not args:
        return False
    executable = Path(args[0]).name
    if executable == PUBLISHER:
        return True
    if not re.fullmatch(r"python(?:3(?:\.\d+)?)?", executable):
        return False
    # Common interpreter isolation flags can precede the fixture path.
    operands = iter(args[1:])
    script = next((arg for arg in operands if arg not in ("-I", "-B", "-u", "-E", "-s", "-S")), "")
    return Path(script).name == PUBLISHER


def result_text(content):
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    return "\n".join(block["text"] for block in content
                     if isinstance(block, dict) and block.get("type") == "text"
                     and isinstance(block.get("text"), str))


def claude_commands(events):
    commands, results = {}, {}
    complete = False
    for event in events:
        kind = event.get("type")
        if kind == "result":
            complete = event.get("subtype") == "success" and event.get("is_error") is not True
        message = event.get("message")
        blocks = message.get("content") if isinstance(message, dict) else None
        for block in blocks if isinstance(blocks, list) else ():
            if not isinstance(block, dict):
                continue
            if kind == "assistant" and block.get("type") == "tool_use" and block.get("name") == "Bash":
                call_id = block.get("id")
                inputs = block.get("input")
                if isinstance(call_id, str) and isinstance(inputs, dict):
                    commands[call_id] = inputs.get("command")
            elif kind == "user" and block.get("type") == "tool_result":
                call_id = block.get("tool_use_id")
                if isinstance(call_id, str) and call_id in commands:
                    results[call_id] = (result_text(block.get("content")), block.get("is_error", False) is False)
    return complete, [(command, *results.get(key, ("", False))) for key, command in commands.items()]


def codex_commands(events):
    commands, results = {}, {}
    complete = False
    for event in events:
        kind = event.get("type")
        if kind in ("turn.completed", "turn.failed"):
            complete = kind == "turn.completed"
        item = event.get("item")
        if not isinstance(item, dict) or item.get("type") != "command_execution":
            continue
        call_id = item.get("id")
        if not isinstance(call_id, str) or kind not in ("item.started", "item.updated", "item.completed"):
            continue
        if item.get("command"):
            commands[call_id] = item["command"]
        else:
            commands.setdefault(call_id, None)
        if kind == "item.completed":
            code = item.get("exit_code")
            success = type(code) is int and code == 0 and item.get("status") in (None, "completed")
            results[call_id] = (item.get("aggregated_output"), success)
    return complete, [(command, *results.get(key, ("", False))) for key, command in commands.items()]


def receipts(output):
    if not isinstance(output, str):
        return
    for line in output.splitlines():
        if line.startswith(RECEIPT):
            try:
                yield json.loads(line[len(RECEIPT):])
            except ValueError:
                yield None


def grade_publish_calls(host, events, returncode, expected):
    parse = claude_commands if host == "claude" else codex_commands
    complete, commands = parse(events)
    if returncode != 0 or not complete:
        return "publication run did not complete successfully"

    attempts = 0
    observed = []
    for command, output, success in commands:
        received = list(receipts(output))
        direct = direct_publish(command)
        attempts += len(received) or int(direct)
        if success and direct:
            observed.extend(received)
    if attempts != len(expected):
        return "expected {} publish attempts, observed {}".format(len(expected), attempts)
    if observed != expected:
        return "publish receipts do not match successful calls with expected arguments"
    return None
