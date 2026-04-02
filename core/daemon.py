import asyncio
import logging
import signal
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.config import settings, validate_config
from core.logger import db_logger
from agents.orchestrator import run_orchestrator
from datetime import datetime

logger = logging.getLogger(__name__)

class SherlockDaemon:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.run_count = 0
        self.last_run = None
        self.is_running = False

    async def run_task(self):
        """
        The main task that runs every 15 minutes.
        """
        if self.is_running:
            db_logger.log_event("WARNING", "DAEMON", "Previous run still in progress. Skipping...")
            return

        self.is_running = True
        self.run_count += 1
        self.last_run = datetime.now()
        
        db_logger.log_event("INFO", "DAEMON", f"Starting scheduled run #{self.run_count}")
        
        try:
            # Execute the LangGraph orchestrator
            # We wrap it in a timeout to prevent it from hanging forever
            # 14 minutes timeout for a 15-minute interval
            await asyncio.wait_for(run_orchestrator(), timeout=14 * 60)
            db_logger.log_event("INFO", "DAEMON", f"Scheduled run #{self.run_count} completed successfully.")
        except asyncio.TimeoutError:
            db_logger.log_event("ERROR", "DAEMON", f"Run #{self.run_count} timed out.")
        except Exception as e:
            db_logger.log_event("ERROR", "DAEMON", f"Run #{self.run_count} failed with error: {e}")
        finally:
            self.is_running = False

    def start(self):
        """
        Start the APScheduler loop.
        """
        if not validate_config():
            logger.error("Configuration validation failed. Daemon will not start.")
            return

        db_logger.log_event("INFO", "DAEMON", "SHERLOCK DAEMON starting up...")
        
        # Schedule the first run immediately, then every X minutes
        self.scheduler.add_job(self.run_task, 'interval', minutes=settings.DAEMON_INTERVAL_MINUTES, next_run_time=datetime.now())
        self.scheduler.start()
        
        db_logger.log_event("INFO", "DAEMON", f"Scheduler started. Interval: {settings.DAEMON_INTERVAL_MINUTES} minutes.")

    def stop(self):
        """
        Gracefully stop the daemon.
        """
        db_logger.log_event("INFO", "DAEMON", "SHERLOCK DAEMON shutting down...")
        self.scheduler.shutdown()

async def main():
    daemon = SherlockDaemon()
    daemon.start()

    # Handle termination signals
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    try:
        await stop_event.wait()
    finally:
        daemon.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
