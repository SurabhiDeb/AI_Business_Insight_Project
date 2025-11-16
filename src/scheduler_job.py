import schedule
import time
import subprocess
import os

# --- Path Setup ---
# Get the absolute path of the directory containing this script (src/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute paths to the scripts to be run
ETL_SCRIPT_PATH = os.path.join(SCRIPT_DIR, "etl_pipeline.py")
AI_SCRIPT_PATH = os.path.join(SCRIPT_DIR, "ai_insight_generator.py")


def job():
    """Executes the ETL and AI insight generation scripts."""
    print(f"--- Running ETL + AI Job at {time.ctime()} ---")

    # Run ETL Pipeline using the absolute path
    print(f"Starting ETL: {ETL_SCRIPT_PATH}")
    etl_result = subprocess.run(
        ["python3", ETL_SCRIPT_PATH],
        capture_output=True,
        text=True
    )
    print("ETL Output:\n", etl_result.stdout)
    if etl_result.stderr:
        print("ETL ERROR:\n", etl_result.stderr)

    # Run AI Generator using the absolute path
    print(f"Starting AI Generation: {AI_SCRIPT_PATH}")
    ai_result = subprocess.run(
        ["python3", AI_SCRIPT_PATH],
        capture_output=True,
        text=True
    )
    print("AI Output:\n", ai_result.stdout)
    if ai_result.stderr:
        print("AI ERROR:\n", ai_result.stderr)

    print("--- Job completed ---")


# schedule every Monday at 09:00 (example)
# schedule.every().monday.at("09:00").do(job)

# For testing run every minute (uncomment for quick tests)
schedule.every(1).minutes.do(job)

print("Scheduler started. Press Ctrl+C to stop.")
while True:
    schedule.run_pending()
    time.sleep(10)
