import asyncio,json,logging,os,sys
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from plyer import notification
from typing import List

current_dir=os.path.dirname(os.path.abspath(__file__))
task_file=os.path.join(current_dir,"tasks.json")
log_file=os.path.join(current_dir,"reminder_history.log")

logging.basicConfig(filename=log_file,level=logging.INFO,
    format="%(asctime)s | %(message)s")

@dataclass
class Task:
    id: int
    title: str
    notes: str
    run_at: datetime
    recurring: bool
    interval: int |None=None

    def to_dict(self):
        d = asdict(self)
        d["run_at"] = self.run_at.isoformat()
        return d

    @staticmethod
    def from_dict(d):
        d["run_at"] = datetime.fromisoformat(d["run_at"])
        return Task(**d)

def load_tasks():
    if not os.path.exists(task_file):
        return []
    try:
        with open(task_file) as f:
            return [Task.from_dict(t) for t in json.load(f)]
    except (json.JSONDecodeError, KeyError):
        return []

def save_tasks(tasks:List[Task]):
    with open(task_file,"w") as f:
        json.dump([t.to_dict() for t in tasks], f, indent=4)

def notify(task:Task):
    print(f"\n Notification:{task.title}")
    notification.notify(title=task.title,message=task.notes,timeout=10)
    logging.info(f"Triggered |{task.id}|{task.title}")

async def run_task(task:Task,tasks:List[Task]):
    try:
        while True:
            now=datetime.now()
            delay=(task.run_at-now).total_seconds()

            if delay>0:
                await asyncio.sleep(delay)

            notify(task)
            if not task.recurring or not task.interval:
                tasks[:] = [t for t in tasks if t.id != task.id]
                save_tasks(tasks)
                break

            task.run_at+=timedelta(minutes=task.interval)
            save_tasks(tasks)
            logging.info(f"Rescheduled | {task.id} | {task.run_at}")
    except asyncio.CancelledError:
        pass

async def ainput(prompt: str) -> str:
    return await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)

async def main():
    tasks = load_tasks()
    scheduled = {}

    for t in tasks:
        if t.run_at > datetime.now():
            scheduled[t.id] = asyncio.create_task(run_task(t, tasks))

    while True:
        print("\n[1] Create [2] View [3] Delete [4] Exit")
        print("Choice: ", end="", flush=True)
        choice=(await ainput("")).strip()

        if choice=="1":
            try:
                title=(await ainput("Title: ")).strip()
                notes=(await ainput("Notes: ")).strip()
                time_str=(await ainput("Date & Time (DD-MM-YYYY HH:MM): ")).strip()
                run_at=datetime.strptime(time_str, "%d-%m-%Y %H:%M")

                rec=(await ainput("Recurring? (y/n): ")).strip().lower() == "y"
                interval=int((await ainput("Interval (min): ")).strip()) if rec else None

                task_id=max([t.id for t in tasks],default=0) + 1
                new_task=Task(task_id,title,notes,run_at,rec,interval)
                tasks.append(new_task)
                
                save_tasks(tasks)
                scheduled[new_task.id]=asyncio.create_task(run_task(new_task, tasks))
                print("Task scheduled successfully.")
            
            except ValueError:
                print("Invalid input. Task not created.")

        elif choice=="2":
            if not tasks:
                print("No tasks found.")
            for t in tasks:
                status="Recurring" if t.recurring else "Once"
                print(f"ID: {t.id} | {t.title} | {t.run_at} ({status})")

        elif choice=="3":
            print("Enter ID to delete: ", end="", flush=True)
            try:

                tid=int((await ainput("")).strip())
                if tid in scheduled:
                    scheduled[tid].cancel()
                    del scheduled[tid]

                tasks[:]=[t for t in tasks if t.id != tid]
                save_tasks(tasks)
                print(f"Task {tid} deleted.")
            except ValueError:
                print("Invalid ID.")

        elif choice=="4":
            print("Exiting...")
            for t in scheduled.values():
                t.cancel()
            break

try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
