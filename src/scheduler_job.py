# src/scheduler_job.py
import schedule
import time
import subprocess


def job():
    print("Running ETL + AI job...")
    subprocess.run(["python", "src/etl_pipeline.py"])
    subprocess.run(["python", "src/ai_insight_generator.py"])
    print("Job completed.")


# schedule every Monday at 09:00 (example)
schedule.every().monday.at("09:00").do(job)

# For testing run every minute (uncomment for quick tests)
# schedule.every(1).minutes.do(job)

print("Scheduler started. Press Ctrl+C to stop.")
while True:
    schedule.run_pending()
    time.sleep(10)
