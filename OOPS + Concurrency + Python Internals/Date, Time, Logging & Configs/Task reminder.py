import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from plyer import notification

logging.basicConfig(filename="reminder_history.log",level=logging.INFO,format="%(asctime)s | %(levelname)s | %(message)s",)

@dataclass
class Task:
    title: str 
    notes: str
    run_at: datetime
    recurring: bool
    interval_minutes: int|None = None

def send_notification(task:Task):
    notification.notify(title=task.title,message=task.notes,timeout=10)
    logging.info(f"Reminder triggered | Title: {task.title} | Run at {task.run_at}")

async def schedule_task(task:Task):
    while True:
        now=datetime.now()
        wait_time=(task.run_at - now).total_seconds()

        if wait_time > 0:
            await asyncio.sleep(wait_time)

        send_notification(task)
        if not task.recurring:
            logging.info(f"One-time task completed | Title: {task.title}")
            break

        task.run_at+= timedelta(minutes=task.interval_minutes)
        logging.info(f"Recurring task rescheduled | Title: {task.title} | Next run at: {task.run_at}")

def get_user_task() -> Task:
    print("\nCreate New Task")

    title = input("Task Title: ").strip()
    notes = input("Notes: ").strip()
    date_str = input("Date (YYYY-MM-DD): ").strip()
    time_str = input("Time (HH:MM, 24-hr): ").strip()

    run_at = datetime.strptime(f"{date_str} {time_str}","%Y-%m-%d %H:%M")

    recurring_input = input("Recurring task? (yes/no): ").strip().lower()
    recurring = recurring_input == "yes"
    interval = None
    if recurring:
        interval = int(input("Repeat interval (in minutes): ").strip())

    logging.info(f"Task created | Title: {title} | Run at: {run_at} | Recurring: {recurring}")

    return Task(title=title,notes=notes,run_at=run_at,recurring=recurring,interval_minutes=interval)

async def main():
    scheduled_tasks = []

    while True:
        task = get_user_task()
        scheduled_tasks.append(asyncio.create_task(schedule_task(task)))

        more = input("\nAdd another task? (y/n): ").strip().lower()
        if more != "yes":
            break

    if scheduled_tasks:
        await asyncio.gather(*scheduled_tasks)
    else:
        print("No tasks scheduled.")

if __name__ == "__main__":
    print("Task Reminder Application Started")
    asyncio.run(main())