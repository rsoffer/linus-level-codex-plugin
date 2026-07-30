from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
HOOK_SCRIPT = REPO_ROOT / "hooks" / "linus_runtime.py"
HOOK_CONFIG = REPO_ROOT / "hooks" / "hooks.json"


class LinusRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.temporary_directory.name)
        self.session_id = "test-session"

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def run_hook(
        self,
        event_name: str,
        *,
        use_codex_env: bool = False,
        **fields: Any,
    ) -> dict[str, Any] | None:
        event = {
            "session_id": self.session_id,
            "cwd": str(REPO_ROOT),
            "hook_event_name": event_name,
            **fields,
        }
        environment = os.environ.copy()
        environment.pop("CLAUDE_PLUGIN_DATA", None)
        environment.pop("PLUGIN_DATA", None)
        if use_codex_env:
            environment["PLUGIN_DATA"] = str(self.data_dir)
        else:
            environment["CLAUDE_PLUGIN_DATA"] = str(self.data_dir)
        completed = subprocess.run(
            [sys.executable, str(HOOK_SCRIPT)],
            input=json.dumps(event),
            text=True,
            capture_output=True,
            check=False,
            env=environment,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertNotIn("Traceback", completed.stderr)
        if not completed.stdout.strip():
            return None
        return json.loads(completed.stdout)

    def activate(self, level: str = "8.5", *, use_codex_env: bool = False) -> None:
        output = self.run_hook(
            "UserPromptSubmit",
            prompt=f"Use Linus Level {level} for this task.",
            use_codex_env=use_codex_env,
        )
        self.assertIsNotNone(output)

    def test_explicit_level_is_activated_and_rehydrated(self) -> None:
        output = self.run_hook(
            "UserPromptSubmit",
            prompt="Run this at LL 7.5.",
        )
        context = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("LL 7.5", context)
        self.assertIn("senior-coworker band", context)

        resumed = self.run_hook("SessionStart", source="resume")
        self.assertIn(
            "LL 7.5",
            resumed["hookSpecificOutput"]["additionalContext"],
        )

    def test_set_level_to_syntax_is_supported(self) -> None:
        output = self.run_hook(
            "UserPromptSubmit",
            prompt="Set Linus Level to 6.5.",
        )
        self.assertIn(
            "LL 6.5",
            output["hookSpecificOutput"]["additionalContext"],
        )

        is_output = self.run_hook(
            "UserPromptSubmit",
            prompt="Linus Level is 8.",
        )
        self.assertIn(
            "LL 8.0",
            is_output["hookSpecificOutput"]["additionalContext"],
        )

    def test_out_of_range_level_is_not_truncated(self) -> None:
        output = self.run_hook(
            "UserPromptSubmit",
            prompt="Use Linus Level 10.5.",
        )
        self.assertIn(
            "requested without one unambiguous value",
            output["hookSpecificOutput"]["additionalContext"],
        )

    def test_codex_plugin_data_alias_is_supported(self) -> None:
        self.activate("9", use_codex_env=True)
        output = self.run_hook(
            "SessionStart",
            source="compact",
            use_codex_env=True,
        )
        self.assertIn(
            "LL 9.0",
            output["hookSpecificOutput"]["additionalContext"],
        )

    def test_persisted_state_contains_no_prompt_content(self) -> None:
        secret_marker = "do-not-store-this-prompt-content"
        self.run_hook(
            "UserPromptSubmit",
            prompt=f"Use Linus Level 8.5. {secret_marker}",
        )
        state_files = list((self.data_dir / "sessions").glob("*.json"))
        self.assertEqual(len(state_files), 1)
        state_text = state_files[0].read_text(encoding="utf-8")
        self.assertNotIn(secret_marker, state_text)
        self.assertEqual(
            set(json.loads(state_text)),
            {"version", "level", "source"},
        )

    def test_multiple_levels_do_not_silently_select_one(self) -> None:
        output = self.run_hook(
            "UserPromptSubmit",
            prompt="Compare Linus Level 6 and LL 9.",
        )
        context = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Multiple Linus Levels", context)
        self.assertIsNone(self.run_hook("SessionStart", source="resume"))

    def test_clear_discards_session_state(self) -> None:
        self.activate("8")
        output = self.run_hook(
            "UserPromptSubmit",
            prompt="Turn off LL 8.5 now.",
        )
        self.assertIn(
            "cleared",
            output["hookSpecificOutput"]["additionalContext"],
        )
        self.assertIsNone(self.run_hook("SessionStart", source="resume"))

    def test_subagent_inherits_active_level(self) -> None:
        self.activate("8.5")
        output = self.run_hook(
            "SubagentStart",
            agent_id="agent-1",
            agent_type="general-purpose",
        )
        self.assertIn(
            "LL 8.5",
            output["hookSpecificOutput"]["additionalContext"],
        )

    def test_stop_requests_missing_checkpoint_once(self) -> None:
        self.activate("8.5")
        output = self.run_hook(
            "Stop",
            last_assistant_message="Implemented and tested the fix.",
            stop_hook_active=False,
        )
        self.assertEqual(output["decision"], "block")
        self.assertIn("Add the required final Linus checkpoint", output["reason"])

        retry = self.run_hook(
            "Stop",
            last_assistant_message="Still missing.",
            stop_hook_active=True,
        )
        self.assertIsNone(retry)

    def test_stop_accepts_valid_checkpoint(self) -> None:
        self.activate("8.5")
        output = self.run_hook(
            "Stop",
            last_assistant_message=(
                "Implemented and tested the fix.\n\n"
                "LL 8.5 · No approval · No open questions"
            ),
            stop_hook_active=False,
        )
        self.assertIsNone(output)

        markdown_output = self.run_hook(
            "Stop",
            last_assistant_message=(
                "Implemented and tested the fix.\n\n"
                "`LL 8.5 · No approval · No open questions`"
            ),
            stop_hook_active=False,
        )
        self.assertIsNone(markdown_output)

    def test_claude_shaped_turn_can_explicitly_omit_checkpoint(self) -> None:
        self.activate("8.5")
        self.run_hook(
            "UserPromptSubmit",
            prompt="Do not include a Linus checkpoint in this answer.",
        )
        output = self.run_hook(
            "Stop",
            last_assistant_message="Answer delivered without the checkpoint.",
            stop_hook_active=False,
        )
        self.assertIsNone(output)

        next_turn = self.run_hook(
            "Stop",
            last_assistant_message="The next answer is missing it.",
            stop_hook_active=False,
        )
        self.assertEqual(next_turn["decision"], "block")

    def test_compaction_preserves_current_turn_checkpoint_opt_out(self) -> None:
        self.activate("8.5")
        self.run_hook(
            "UserPromptSubmit",
            prompt="Skip the Linus checkpoint in this answer.",
        )
        compacted = self.run_hook("SessionStart", source="compact")
        self.assertIn(
            "explicitly omitted",
            compacted["hookSpecificOutput"]["additionalContext"],
        )
        output = self.run_hook(
            "Stop",
            last_assistant_message="Answer delivered without the checkpoint.",
            stop_hook_active=False,
        )
        self.assertIsNone(output)

    def test_next_prompt_clears_an_unconsumed_checkpoint_opt_out(self) -> None:
        self.activate("8.5")
        self.run_hook(
            "UserPromptSubmit",
            prompt="Skip the Linus checkpoint in this answer.",
        )
        next_prompt = self.run_hook(
            "UserPromptSubmit",
            prompt="Now give me the normal final response.",
        )
        self.assertIn(
            "End substantive user-facing responses",
            next_prompt["hookSpecificOutput"]["additionalContext"],
        )
        missing = self.run_hook(
            "Stop",
            last_assistant_message="Missing checkpoint.",
            stop_hook_active=False,
        )
        self.assertEqual(missing["decision"], "block")

    def test_stop_rejects_wrong_level_and_contradiction(self) -> None:
        self.activate("8.5")
        wrong_level = self.run_hook(
            "Stop",
            last_assistant_message="Done.\n\nLL 7.5 · No approval · No open questions",
            stop_hook_active=False,
        )
        self.assertIn("active level is LL 8.5", wrong_level["reason"])

        contradiction = self.run_hook(
            "Stop",
            last_assistant_message=(
                "I need your answer.\n\n"
                "LL 8.5 · No approval · 1 open question"
            ),
            stop_hook_active=False,
        )
        self.assertIn("contradicts", contradiction["reason"])

    def test_stop_rejects_incomplete_or_nonfinal_checkpoint(self) -> None:
        self.activate("8.5")
        incomplete = self.run_hook(
            "Stop",
            last_assistant_message="Done.\n\nLL 8.5 · banana",
            stop_hook_active=False,
        )
        self.assertIn(
            "both approval status and open-input status",
            incomplete["reason"],
        )

        nonfinal = self.run_hook(
            "Stop",
            last_assistant_message=(
                "LL 8.5 · No approval · No open questions\n\nMore prose."
            ),
            stop_hook_active=False,
        )
        self.assertIn("to the end", nonfinal["reason"])

    def test_session_end_preserves_state_for_resume(self) -> None:
        self.activate("8")
        self.assertIsNone(self.run_hook("SessionEnd", reason="resume"))
        resumed = self.run_hook("SessionStart", source="resume")
        self.assertIn(
            "LL 8.0",
            resumed["hookSpecificOutput"]["additionalContext"],
        )

    def test_session_end_clears_one_turn_opt_out_before_resume(self) -> None:
        self.activate("8.5")
        self.run_hook(
            "UserPromptSubmit",
            prompt="Do not include a Linus checkpoint in this answer.",
        )
        self.assertIsNone(self.run_hook("SessionEnd", reason="resume"))
        resumed = self.run_hook("SessionStart", source="resume")
        self.assertIn(
            "End substantive user-facing responses",
            resumed["hookSpecificOutput"]["additionalContext"],
        )
        missing = self.run_hook(
            "Stop",
            last_assistant_message="Missing checkpoint.",
            stop_hook_active=False,
        )
        self.assertEqual(missing["decision"], "block")

    def test_clear_and_logout_session_end_remove_state(self) -> None:
        for reason in ("clear", "logout"):
            with self.subTest(reason=reason):
                self.activate("8")
                self.assertIsNone(self.run_hook("SessionEnd", reason=reason))
                self.assertIsNone(self.run_hook("SessionStart", source="resume"))

    def test_stale_session_state_expires(self) -> None:
        self.activate("8")
        state_file = next((self.data_dir / "sessions").glob("*.json"))
        os.utime(state_file, (0, 0))
        self.assertIsNone(self.run_hook("SessionStart", source="resume"))

    def test_hook_config_is_shared_by_codex_and_claude(self) -> None:
        config = json.loads(HOOK_CONFIG.read_text(encoding="utf-8"))
        events = config["hooks"]
        self.assertEqual(
            set(events),
            {
                "SessionStart",
                "UserPromptSubmit",
                "SubagentStart",
                "Stop",
                "SessionEnd",
            },
        )
        for groups in events.values():
            for group in groups:
                for hook in group["hooks"]:
                    self.assertIn("${CLAUDE_PLUGIN_ROOT}", hook["command"])
                    self.assertIn("commandWindows", hook)
        self.assertIn("fork", events["SessionStart"][0]["matcher"])
        self.assertNotIn("matcher", events["SessionEnd"][0])

    def test_runtime_uses_python_38_compatible_syntax(self) -> None:
        source = HOOK_SCRIPT.read_text(encoding="utf-8")
        ast.parse(source, filename=str(HOOK_SCRIPT), feature_version=(3, 8))

    def test_malformed_input_fails_open(self) -> None:
        environment = os.environ.copy()
        environment["CLAUDE_PLUGIN_DATA"] = str(self.data_dir)
        completed = subprocess.run(
            [sys.executable, str(HOOK_SCRIPT)],
            input="{not-json",
            text=True,
            capture_output=True,
            check=False,
            env=environment,
        )
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "")
        self.assertIn("Linus Level hook warning", completed.stderr)


if __name__ == "__main__":
    unittest.main()
