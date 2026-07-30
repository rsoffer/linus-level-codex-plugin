#!/usr/bin/env python3
"""Shared Codex and Claude Code runtime hooks for Linus Level."""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

STATE_VERSION = 2
STATE_TTL_SECONDS = 30 * 24 * 60 * 60
LEVEL_PATTERN = re.compile(
    r"\b(?:linus\s+level|linus|ll)\s*(?:=|:|at|to|is)?\s*"
    r"(10(?:\.0)?|[1-9](?:\.\d)?)(?!\.\d|\d)",
    re.IGNORECASE,
)
LINUS_MENTION_PATTERN = re.compile(r"\b(?:linus\s+level|ll)\b", re.IGNORECASE)
CLEAR_PATTERN = re.compile(
    r"^\s*(?:(?:can|could|would)\s+you\s+)?(?:please\s+)?"
    r"(?:disable|clear|reset|turn\s+off)\s+(?:the\s+)?"
    r"(?:linus(?:\s+level)?|ll)\b",
    re.IGNORECASE,
)
CHECKPOINT_OPTOUT_PATTERN = re.compile(
    r"\b(?:omit|skip|exclude|without|do\s+not\s+(?:add|include|use)|"
    r"don't\s+(?:add|include|use))\b.{0,50}\b"
    r"(?:linus(?:\s+level)?\s+)?checkpoint\b",
    re.IGNORECASE,
)
CHECKPOINT_PATTERN = re.compile(
    r"(?m)^\s*(?:[-*>]\s*)?(?:`{1,3}|\*{1,2}|_{1,2})?"
    r"LL\s+(10(?:\.0)?|[1-9](?:\.\d)?)\s*·[^\n]*?"
    r"(?:`{1,3}|\*{1,2}|_{1,2})?\s*$",
    re.IGNORECASE,
)


def _read_event() -> Dict[str, Any]:
    payload = json.load(sys.stdin)
    if not isinstance(payload, dict):
        raise ValueError("hook input must be a JSON object")
    return payload


def _data_root() -> Path:
    configured = os.environ.get("CLAUDE_PLUGIN_DATA") or os.environ.get("PLUGIN_DATA")
    if configured:
        return Path(configured)

    plugin_root = (
        os.environ.get("CLAUDE_PLUGIN_ROOT")
        or os.environ.get("PLUGIN_ROOT")
        or str(Path(__file__).resolve().parent.parent)
    )
    root_hash = hashlib.sha256(plugin_root.encode("utf-8")).hexdigest()[:12]
    return Path(tempfile.gettempdir()) / f"linus-level-{root_hash}"


def _state_path(session_id: str) -> Path:
    session_hash = hashlib.sha256(session_id.encode("utf-8")).hexdigest()
    return _data_root() / "sessions" / f"{session_hash}.json"


def _prune_expired_states() -> None:
    sessions_dir = _data_root() / "sessions"
    cutoff = time.time() - STATE_TTL_SECONDS
    try:
        paths = list(sessions_dir.glob("*.json"))
    except OSError:
        return
    for path in paths:
        try:
            if path.stat().st_mtime < cutoff:
                path.unlink()
        except (FileNotFoundError, OSError):
            pass


def _read_state(session_id: str) -> Optional[Dict[str, Any]]:
    if not session_id:
        return None
    path = _state_path(session_id)
    try:
        if path.stat().st_mtime < time.time() - STATE_TTL_SECONDS:
            path.unlink()
            return None
        state = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    if (
        not isinstance(state, dict)
        or state.get("version") != STATE_VERSION
        or not isinstance(state.get("level"), (int, float))
    ):
        return None
    return state


def _write_state(
    session_id: str,
    level: float,
    source: str,
    *,
    checkpoint_opt_out_pending: bool = False,
) -> None:
    if not session_id:
        return
    path = _state_path(session_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": STATE_VERSION,
        "level": level,
        "source": source,
    }
    if checkpoint_opt_out_pending:
        payload["checkpoint_opt_out_pending"] = True
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        dir=path.parent,
        text=True,
    )
    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, separators=(",", ":"))
            handle.write("\n")
        try:
            os.chmod(temporary_name, 0o600)
        except OSError:
            pass
        os.replace(temporary_name, path)
    finally:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass


def _delete_state(session_id: str) -> None:
    if not session_id:
        return
    try:
        _state_path(session_id).unlink()
    except FileNotFoundError:
        pass


def _format_level(level: float) -> str:
    return f"{level:.1f}"


def _mode_name(level: float) -> str:
    if level < 3:
        return "builder"
    if level < 5:
        return "prototype"
    if level < 7:
        return "product-engineer"
    if level < 8.5:
        return "senior-coworker"
    if level < 9.5:
        return "staff-maintainer"
    return "mission-critical"


def _runtime_context(
    state: Dict[str, Any],
    *,
    checkpoint_required: bool = True,
) -> str:
    level = float(state["level"])
    display = _format_level(level)
    checkpoint_context = (
        "End substantive user-facing responses with a truthful "
        f"`LL {display} · ...` checkpoint; routine progress updates do not need one."
        if checkpoint_required
        else "The user explicitly omitted the Linus checkpoint for this turn; honor "
        "that instruction while applying the rest of the skill."
    )
    return (
        f"Linus runtime active: LL {display} ({_mode_name(level)} band). "
        "Load and apply the linus-level prose and its relevant references; hooks only "
        "preserve continuity and validate delivery. "
        "This tuning layer never overrides system, user, repository, tool, or safety "
        f"instructions. {checkpoint_context}"
    )


def _additional_context(event_name: str, message: str) -> Dict[str, Any]:
    return {
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": message,
        }
    }


def _levels_in_prompt(prompt: str) -> List[float]:
    levels: List[float] = []
    for match in LEVEL_PATTERN.finditer(prompt):
        level = float(match.group(1))
        if 1.0 <= level <= 10.0 and level not in levels:
            levels.append(level)
    return levels


def _handle_user_prompt(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    session_id = str(event.get("session_id") or "")
    prompt = str(event.get("prompt") or "")
    checkpoint_disabled = bool(CHECKPOINT_OPTOUT_PATTERN.search(prompt))

    if CLEAR_PATTERN.search(prompt):
        _delete_state(session_id)
        return _additional_context(
            "UserPromptSubmit",
            "The user cleared the session Linus Level. Do not carry the previous "
            "level forward; use any higher-priority repository default or infer a new "
            "level only if the user asks for Linus calibration.",
        )

    levels = _levels_in_prompt(prompt)
    if len(levels) == 1:
        _write_state(
            session_id,
            levels[0],
            "explicit",
            checkpoint_opt_out_pending=checkpoint_disabled,
        )
        return _additional_context(
            "UserPromptSubmit",
            _runtime_context(
                {"version": STATE_VERSION, "level": levels[0], "source": "explicit"},
                checkpoint_required=not checkpoint_disabled,
            ),
        )

    state = _read_state(session_id)
    if state:
        _write_state(
            session_id,
            float(state["level"]),
            str(state.get("source") or "explicit"),
            checkpoint_opt_out_pending=checkpoint_disabled,
        )
        if checkpoint_disabled:
            state["checkpoint_opt_out_pending"] = True
        else:
            state.pop("checkpoint_opt_out_pending", None)

    if len(levels) > 1:
        active = (
            f" The existing LL {_format_level(float(state['level']))} remains active."
            if state
            else ""
        )
        checkpoint_context = (
            " The user explicitly omitted the Linus checkpoint for this turn."
            if checkpoint_disabled and state
            else ""
        )
        return _additional_context(
            "UserPromptSubmit",
            "Multiple Linus Levels were mentioned. Treat this as comparison or "
            "discussion; do not silently select a new active level."
            + active
            + checkpoint_context,
        )

    if state:
        return _additional_context(
            "UserPromptSubmit",
            _runtime_context(state, checkpoint_required=not checkpoint_disabled),
        )

    if LINUS_MENTION_PATTERN.search(prompt):
        return _additional_context(
            "UserPromptSubmit",
            "Linus Level was requested without one unambiguous value. Infer the level "
            "from repository maturity and task risk using the linus-level skill, state "
            "the choice briefly when it changes behavior, and do not pretend the hook "
            "persisted an inferred value.",
        )

    return None


def _handle_session_start(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    session_id = str(event.get("session_id") or "")
    source = str(event.get("source") or "")
    if source == "clear":
        _delete_state(session_id)
        return None
    state = _read_state(session_id)
    if not state:
        return None
    checkpoint_opt_out_pending = bool(state.get("checkpoint_opt_out_pending"))
    if checkpoint_opt_out_pending and source != "compact":
        _write_state(
            session_id,
            float(state["level"]),
            str(state.get("source") or "explicit"),
        )
        state.pop("checkpoint_opt_out_pending", None)
        checkpoint_opt_out_pending = False
    return _additional_context(
        "SessionStart",
        _runtime_context(
            state,
            checkpoint_required=not checkpoint_opt_out_pending,
        ),
    )


def _handle_subagent_start(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    state = _read_state(str(event.get("session_id") or ""))
    if not state:
        return None
    return _additional_context(
        "SubagentStart",
        _runtime_context(
            state,
            checkpoint_required=not bool(state.get("checkpoint_opt_out_pending")),
        ),
    )


def _checkpoint_error(message: str, expected_level: float) -> Optional[str]:
    checkpoints = list(CHECKPOINT_PATTERN.finditer(message))
    if not checkpoints:
        return (
            "Add the required final Linus checkpoint. It must truthfully state the "
            "active level, whether user approval is needed, and whether material "
            "questions or decisions remain."
        )

    checkpoint = checkpoints[-1].group(0).strip()
    if message[checkpoints[-1].end() :].strip():
        return "Move the Linus checkpoint to the end of the final response."
    actual_level = float(checkpoints[-1].group(1))
    if abs(actual_level - expected_level) > 0.001:
        return (
            f"Correct the final checkpoint level: the active level is "
            f"LL {_format_level(expected_level)}, not LL {_format_level(actual_level)}."
        )

    lower = checkpoint.lower()
    approval_status = re.compile(
        r"\b(?:no approval|approval needed|decision needed|"
        r"awaiting confirmation|blocked)\b"
    )
    input_status = re.compile(
        r"\b(?:no open questions|[1-9]\d*\s+open\s+(?:questions?|decisions?)|"
        r"decision needed|awaiting confirmation)\b"
    )
    if not approval_status.search(lower) or not input_status.search(lower):
        return (
            "Complete the final checkpoint with both approval status and open-input "
            "status, for example `No approval · No open questions`."
        )
    gated_terms = re.compile(
        r"\b(?:approval needed|decision needed|awaiting confirmation|"
        r"\d+\s+open\s+(?:question|decision)s?)\b"
    )
    if "no approval" in lower and gated_terms.search(lower):
        return (
            "Correct the final checkpoint: `No approval` contradicts an approval, "
            "confirmation, open-question, or open-decision gate."
        )
    if "no open questions" in lower and re.search(
        r"\b(?:approval needed|decision needed|awaiting confirmation|"
        r"[1-9]\d*\s+open\s+(?:questions?|decisions?))\b",
        lower,
    ):
        return (
            "Correct the final checkpoint: `No open questions` contradicts a pending "
            "approval, confirmation, or decision."
        )
    return None


def _handle_stop(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if event.get("stop_hook_active"):
        return None
    session_id = str(event.get("session_id") or "")
    state = _read_state(session_id)
    message = event.get("last_assistant_message")
    if not state:
        return None
    if state.get("checkpoint_opt_out_pending"):
        _write_state(
            session_id,
            float(state["level"]),
            str(state.get("source") or "explicit"),
        )
        return None
    if not isinstance(message, str) or not message.strip():
        return None
    error = _checkpoint_error(message, float(state["level"]))
    if not error:
        return None
    return {
        "decision": "block",
        "reason": (
            "Linus runtime final check: "
            + error
            + " Revise the final response only; do not repeat completed work."
        ),
    }


def _handle_session_end(event: Dict[str, Any]) -> None:
    session_id = str(event.get("session_id") or "")
    reason = str(event.get("reason") or "")
    if reason in {"clear", "logout"}:
        _delete_state(session_id)
        return
    state = _read_state(session_id)
    if state and state.get("checkpoint_opt_out_pending"):
        _write_state(
            session_id,
            float(state["level"]),
            str(state.get("source") or "explicit"),
        )


def _dispatch(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    event_name = str(event.get("hook_event_name") or "")
    if event_name == "UserPromptSubmit":
        return _handle_user_prompt(event)
    if event_name == "SessionStart":
        return _handle_session_start(event)
    if event_name == "SubagentStart":
        return _handle_subagent_start(event)
    if event_name == "Stop":
        return _handle_stop(event)
    if event_name == "SessionEnd":
        _handle_session_end(event)
    return None


def main() -> int:
    try:
        _prune_expired_states()
        result = _dispatch(_read_event())
    except Exception as exc:  # Fail open: hooks should not break the agent loop.
        print(f"Linus Level hook warning: {exc}", file=sys.stderr)
        return 0
    if result is not None:
        json.dump(result, sys.stdout, separators=(",", ":"))
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
