import importlib.util
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "repair_codex_sessions.py"
SPEC = importlib.util.spec_from_file_location("repair_codex_sessions", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class RepairCodexSessionsTest(unittest.TestCase):
    def test_provider_sync_and_sidebar_repair(self):
        with tempfile.TemporaryDirectory() as temp:
            user_home = Path(temp)
            codex_home = user_home / ".codex"
            cwd = user_home / "Documents" / "Codex" / "task"
            rollout = codex_home / "sessions" / "rollout.jsonl"
            rollout.parent.mkdir(parents=True)
            cwd.mkdir(parents=True)
            rollout.write_text("{}\n", encoding="utf-8")
            (codex_home / "config.toml").write_text('model_provider = "custom"\n', encoding="utf-8")
            (codex_home / ".codex-global-state.json").write_text("{}\n", encoding="utf-8")

            db_path = codex_home / "state_5.sqlite"
            with closing(sqlite3.connect(db_path)) as db:
                db.execute(
                    """
                    CREATE TABLE threads (
                        id TEXT PRIMARY KEY,
                        rollout_path TEXT NOT NULL,
                        source TEXT NOT NULL,
                        model_provider TEXT NOT NULL,
                        cwd TEXT NOT NULL,
                        archived INTEGER NOT NULL,
                        thread_source TEXT
                    )
                    """
                )
                db.executemany(
                    "INSERT INTO threads VALUES (?, ?, ?, ?, ?, ?, ?)",
                    [
                        ("restore-me", str(rollout), "vscode", "openai", str(cwd), 0, "user"),
                        ("missing", str(rollout.with_name("missing.jsonl")), "vscode", "openai", str(cwd), 0, "user"),
                        ("subagent", str(rollout), "vscode", "openai", str(cwd), 0, "subagent"),
                    ],
                )
                db.commit()

            self.assertEqual(MODULE.read_current_provider(codex_home), "custom")
            touched, missing, backup = MODULE.sync_thread_provider(codex_home, "custom", False)
            self.assertEqual(touched, 1)
            self.assertEqual(missing, ["missing"])
            self.assertTrue(backup and backup.exists())

            sidebar_touched, state_backup = MODULE.repair(codex_home, user_home, False)
            self.assertEqual(sidebar_touched, 3)
            self.assertTrue(state_backup and state_backup.exists())

            with closing(sqlite3.connect(db_path)) as db:
                providers = dict(db.execute("SELECT id, model_provider FROM threads"))
            self.assertEqual(providers["restore-me"], "custom")
            self.assertEqual(providers["missing"], "openai")
            self.assertEqual(providers["subagent"], "openai")

            state = json.loads((codex_home / ".codex-global-state.json").read_text(encoding="utf-8"))
            self.assertIn("restore-me", state["projectless-thread-ids"])


if __name__ == "__main__":
    unittest.main()


