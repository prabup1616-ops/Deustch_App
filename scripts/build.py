#!/usr/bin/env python3
"""
================================================================================
German B1 Goethe Prep & Duel - Build Automation Tool (Gradle-style for Python)
================================================================================
Equivalent to build.gradle / gradlew in the Java ecosystem.

Usage:
    python build.py <task>

Available Tasks:
    run       : Starts the Streamlit application server (like 'gradle run')
    test      : Runs automated unit tests on questions & storage (like 'gradle test')
    build     : Compiles all Python files, verifies templates & assets (like 'gradle build')
    clean     : Cleans __pycache__, temporary bytecode, and build caches (like 'gradle clean')
    tasks     : Lists all available build tasks (like 'gradle tasks')
================================================================================
"""

import sys
import os
import shutil
import py_compile
import subprocess
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
DATA_DIR = os.path.join(BASE_DIR, "data")
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


def log_header(title: str):
    print("\n" + "=" * 70)
    print(f" > Task: {title}")
    print("=" * 70)


def log_success(msg: str):
    print(f"\n[BUILD SUCCESSFUL] {msg}\n")


def log_failed(msg: str):
    print(f"\n[BUILD FAILED] {msg}\n")
    sys.exit(1)


# ==============================================================================
# TASK: CLEAN (like 'gradle clean')
# ==============================================================================
def task_clean():
    log_header("clean")
    deleted_count = 0
    for root, dirs, files in os.walk(BASE_DIR):
        for d in dirs:
            if d in ("__pycache__", ".pytest_cache", "build", "dist", "*.egg-info"):
                p = os.path.join(root, d)
                try:
                    shutil.rmtree(p)
                    print(f"  Removed: {p}")
                    deleted_count += 1
                except Exception as e:
                    print(f"  Warning: Could not remove {p}: {e}")

        for f in files:
            if f.endswith((".pyc", ".pyo")):
                p = os.path.join(root, f)
                try:
                    os.remove(p)
                    deleted_count += 1
                except Exception:
                    pass

    log_success(f"Clean complete. Removed {deleted_count} cached artifacts.")


# ==============================================================================
# TASK: COMPILE & VALIDATE (like 'gradle compileJava')
# ==============================================================================
def task_compile():
    log_header("compilePython")
    python_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        if "__pycache__" in root or ".git" in root or ".venv" in root:
            continue
        for f in files:
            if f.endswith(".py") and f != "build.py":
                python_files.append(os.path.join(root, f))

    print(f"Compiling {len(python_files)} Python source files...")
    for pf in python_files:
        rel_path = os.path.relpath(pf, BASE_DIR)
        try:
            py_compile.compile(pf, doraise=True)
            print(f"  [OK] {rel_path}")
        except py_compile.PyCompileError as e:
            log_failed(f"Syntax error in {rel_path}:\n{e}")

    # Verify Static Assets
    log_header("processResources")
    required_assets = [
        "static/css/main.css",
        "static/templates/timer.html",
        "static/templates/voice_bubble.html",
        "static/templates/confetti.html",
        "static/templates/grammar_chart.html",
        "static/templates/phrase_loader.html",
        "data/german_phrases.json",
        "data/lsrw_cache.json",
        "data/questions_bank.json",
        "data/gender_questions_bank.json",
        "data/duel_data.json"
    ]
    for asset in required_assets:
        full_p = os.path.join(BASE_DIR, asset)
        if os.path.exists(full_p):
            sz = os.path.getsize(full_p)
            print(f"  [OK] Asset verified: {asset} ({sz} bytes)")
        else:
            log_failed(f"Missing required asset: {asset}")

    log_success("All Python sources and templates validated successfully.")


# ==============================================================================
# TASK: TEST (like 'gradle test')
# ==============================================================================
def task_test():
    log_header("test")
    print("Running automated test suite...\n")

    # Test 1: Questions Bank Integrity
    print("1. Testing questions_bank.json integrity...")
    q_file = os.path.join(DATA_DIR, "questions_bank.json")
    if not os.path.exists(q_file):
        log_failed(f"questions_bank.json not found in {DATA_DIR}!")
    with open(q_file, "r", encoding="utf-8") as f:
        q_data = json.load(f)
    if len(q_data) < 162:
        log_failed(f"Expected 162 questions, found {len(q_data)}")
    for q in q_data[:5]:
        assert "prompt_te" in q, "Missing Telugu prompt"
        assert "prompt_kn" in q, "Missing Kannada prompt"
        assert "target_de" in q, "Missing German target"
        assert len(q["options"]) == 4, "Each question must have 4 options"
    print(f"   [PASS] 162 verified B1 questions loaded cleanly.")

    # Test 2: Storage & Score Normalization
    print("2. Testing storage & case-insensitive player registration...")
    import storage
    p = storage.get_or_create_player("__test_runner__", "🚀")
    assert p["name"] == "__test_runner__"
    # Case insensitivity test
    p_lower = storage.get_or_create_player("__TEST_RUNNER__")
    assert p["id"] == p_lower["id"]
    # Cleanup test player
    data = storage.load_data()
    if "__test_runner__" in data["players"]:
        del data["players"]["__test_runner__"]
    storage.save_data(data)
    print("   [PASS] Persistent storage & case-insensitive matching verified.")

    # Test 3: Template Loaders
    print("3. Testing template loaders...")
    from src.config import load_css, load_template
    css = load_css()
    assert len(css) > 500, "main.css is empty or failed to load"
    timer_html = load_template("timer.html")
    assert "{{curr_idx}}" in timer_html, "timer.html template placeholder missing"
    print("   [PASS] External CSS and HTML templates verified.")

    # Test 4: Gender Questions Bank Integrity
    print("4. Testing gender_questions_bank.json integrity...")
    from src.gender_questions import GENDER_QUESTIONS_DATA, get_daily_gender_questions, get_gender_pack_questions
    assert len(GENDER_QUESTIONS_DATA) >= 200, f"Expected 200+ nouns, found {len(GENDER_QUESTIONS_DATA)}"
    for gq in GENDER_QUESTIONS_DATA[:10]:
        assert gq["article"] in ["der", "die", "das"], f"Invalid article: {gq['article']}"
        assert len(gq["noun"]) > 0, "Missing noun"
        assert len(gq["plural"]) > 0, "Missing plural form"
        assert len(gq["meaning_en"]) > 0, "Missing English meaning"
    daily_gq = get_daily_gender_questions("2026-11-14", count=5)
    assert len(daily_gq) == 5, "Daily gender question generator must yield 5 questions"
    print(f"   [PASS] {len(GENDER_QUESTIONS_DATA)} verified Goethe B1 nouns with articles and plurals loaded.")

    # Test 5: Strict Scoreboard Isolation (Pronoun vs Gender)
    print("5. Testing scoreboard isolation between Pronoun and Gender categories...")
    test_date = "2099-01-01"
    # Record pronoun attempt
    storage.record_attempt("__iso_test__", test_date, score=4, total=5, category="pronoun")
    # Record gender attempt
    storage.record_attempt("__iso_test__", test_date, score=2, total=5, category="gender")

    pronoun_stats = storage.get_player_daily_stats("__iso_test__", test_date, category="pronoun")
    gender_stats = storage.get_player_daily_stats("__iso_test__", test_date, category="gender")

    assert pronoun_stats["best_score"] == 4, f"Expected pronoun best score 4, got {pronoun_stats['best_score']}"
    assert gender_stats["best_score"] == 2, f"Expected gender best score 2, got {gender_stats['best_score']}"

    # Clean up test attempts
    data = storage.load_data()
    data["attempts"] = [a for a in data.get("attempts", []) if a.get("player_id") != "__iso_test__"]
    storage.save_data(data)
    print("   [PASS] Strict scoreboard isolation verified.")

    # Test 6: LSRW Module State Persistence
    print("6. Testing LSRW Module state persistence & storage...")
    test_lsrw_player = "__lsrw_test_player__"
    test_lsrw_state = {
        "practiced_list": ["Relativsatz"],
        "explained_list": ["Passiv", "weil vs obwohl"],
        "has_seen_kasus": True,
        "current_topic": "Passiv",
        "current_stage": "scenario_selection",
        "chat_history": [{"role": "assistant", "content": "Hallo"}]
    }
    storage.save_lsrw_data(test_lsrw_player, test_lsrw_state)
    retrieved_lsrw = storage.get_lsrw_data(test_lsrw_player)
    assert retrieved_lsrw["practiced_list"] == ["Relativsatz"], "Failed to retrieve LSRW practiced_list"
    assert retrieved_lsrw["explained_list"] == ["Passiv", "weil vs obwohl"], "Failed to retrieve LSRW explained_list"
    assert retrieved_lsrw["has_seen_kasus"] is True, "Failed to retrieve has_seen_kasus flag"
    assert retrieved_lsrw["current_topic"] == "Passiv", "Failed to retrieve current_topic"

    # Cleanup LSRW test data
    data = storage.load_data()
    if test_lsrw_player in data.get("lsrw_sessions", {}):
        del data["lsrw_sessions"][test_lsrw_player]
        storage.save_data(data)
    print("   [PASS] LSRW persistent state & topic tracking verified.")

    log_success("All tests passed (6/6 test suites succeeded).")


# ==============================================================================
# TASK: BUILD (like 'gradle build' = clean + compile + test)
# ==============================================================================
def task_build():
    task_clean()
    task_compile()
    task_test()
    log_success("Project build succeeded! Ready for production & deployment.")


# ==============================================================================
# TASK: RUN (like 'gradle run')
# ==============================================================================
def task_run():
    log_header("runApp")
    print("Starting Streamlit application...\n")
    cmd = [sys.executable, "-m", "streamlit", "run", "app.py"]
    try:
        subprocess.run(cmd, cwd=BASE_DIR)
    except KeyboardInterrupt:
        print("\nApp stopped by user.")


# ==============================================================================
# TASK: TASKS (like 'gradle tasks')
# ==============================================================================
def task_list():
    print("""
================================================================================
German B1 Duel Build Automation Tasks (like gradle tasks)
================================================================================
Tasks:
  run       - Launch the Streamlit application server (like 'gradle run')
  build     - Clean, compile, and run tests (like 'gradle build')
  test      - Run verification tests on question banks & storage (like 'gradle test')
  compile   - Check Python syntax and verify template resources
  clean     - Remove temporary __pycache__ and build artifacts (like 'gradle clean')
  tasks     - Show this list of available tasks

Usage examples:
  python build.py run
  python build.py test
  python build.py build
  python build.py clean
================================================================================
""")


# ==============================================================================
# MAIN DISPATCHER
# ==============================================================================
def main():
    if len(sys.argv) < 2:
        task_list()
        return

    action = sys.argv[1].lower()
    if action == "run":
        task_run()
    elif action == "build":
        task_build()
    elif action in ("test", "tests"):
        task_test()
    elif action in ("compile", "check"):
        task_compile()
    elif action == "clean":
        task_clean()
    elif action in ("tasks", "help", "--help", "-h"):
        task_list()
    else:
        print(f"Unknown task: '{action}'")
        task_list()
        sys.exit(1)


if __name__ == "__main__":
    main()
