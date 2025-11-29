import asyncio
from app.database import engine, AsyncSessionLocal
from app.models import Task, Base
from sqlalchemy.future import select

async def init_data():
    async with AsyncSessionLocal() as db:
        created = 0

        # Seed: Complete Survey (idempotent)
        res1 = await db.execute(
            select(Task).where(
                Task.name == "Complete Survey",
                Task.cpa_network_id == "cpabuild_123"
            )
        )
        if not res1.scalars().first():
            task = Task(
                name="Complete Survey",
                description="Answer 5 questions to verify you are human.",
                cpa_network_id="cpabuild_123",
                reward_spins=2
            )
            db.add(task)
            created += 1

        # Seed: Download App (idempotent)
        res2 = await db.execute(
            select(Task).where(
                Task.name == "Download App",
                Task.cpa_network_id == "ogads_456"
            )
        )
        if not res2.scalars().first():
            task2 = Task(
                name="Download App",
                description="Install and open the app for 30 seconds.",
                cpa_network_id="ogads_456",
                reward_spins=5
            )
            db.add(task2)
            created += 1

        if created:
            await db.commit()
            print(f"Tasks created: {created}")
        else:
            print("Tasks already present; no changes.")

async def main():
    # Create tables if main.py didn't run, but main.py startup event usually handles it.
    # We'll assume tables exist or just trigger creation here too just in case
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    await init_data()

if __name__ == "__main__":
    asyncio.run(main())
