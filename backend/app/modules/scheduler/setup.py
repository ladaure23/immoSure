from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import settings
from app.modules.scheduler.jobs import job_paiements_du_jour, job_rappels_echeances


def create_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=settings.scheduler_timezone)

    trigger = CronTrigger(
        hour=settings.notification_hour,
        minute=settings.notification_minute,
        timezone=settings.scheduler_timezone,
    )

    scheduler.add_job(
        job_paiements_du_jour,
        trigger=trigger,
        id="paiements_du_jour",
        replace_existing=True,
    )
    scheduler.add_job(
        job_rappels_echeances,
        trigger=trigger,
        id="rappels_echeances",
        replace_existing=True,
    )

    return scheduler
