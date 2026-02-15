"""Seed the database with the 4 original memories and a default user."""

import asyncio
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session, engine
from app.models import Base, Memory, RegisteredObject, MemoryObject
from app.models.user import User, UserRole

DEFAULT_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

SEED_OBJECTS = [
    {"label": "chair", "display_name": "Grandpa's Chair", "coco_label": "chair"},
    {"label": "book", "display_name": "Mom's Book", "coco_label": "book"},
    {"label": "tv", "display_name": "Family TV", "coco_label": "tv"},
    {"label": "laptop", "display_name": "Our Laptop", "coco_label": "laptop"},
]

SEED_MEMORIES = {
    "chair": {
        "title": "Grandpa's Chair",
        "memory_text": "Grandpa always sat in this chair after dinner. He'd read to me while I sat on the floor next to him. I remember the way his voice got all soft during the sad parts. The leather's cracked now but it still smells like his pipe tobacco if you lean in close.",
    },
    "book": {
        "title": "Mom's Bedtime Book",
        "memory_text": "Mom read this to me so many times the spine fell apart. She had to hold the pages together. I used to ask her to do the rabbit's voice over and over. She never got tired of it, or at least she never let on if she did.",
    },
    "tv": {
        "title": "Sunday Movies",
        "memory_text": "We'd all cram onto the couch on Sunday nights. Dad would make popcorn with too much butter, the way we liked it. Nobody was allowed to talk during the movie but we'd all look at each other during the funny parts. I miss that.",
    },
    "laptop": {
        "title": "Video Calls with Sarah",
        "memory_text": "When Sarah moved away, we started doing video calls every week on this laptop. Sometimes we'd just sit there not saying much. She'd show me her apartment, I'd show her the dog. It helped, knowing she was right there on the screen even though she was so far away.",
    },
}


async def seed():
    async with async_session() as session:
        # Check if already seeded
        existing = await session.execute(select(User).where(User.id == DEFAULT_USER_ID))
        if existing.scalar_one_or_none():
            print("Database already seeded.")
            return

        # Create default user
        user = User(
            id=DEFAULT_USER_ID,
            email="patient@example.com",
            password_hash="$2b$12$placeholder_hash_for_seed_user",
            full_name="Demo Patient",
            role=UserRole.patient,
        )
        session.add(user)
        await session.flush()

        # Create registered objects and memories
        for obj_data in SEED_OBJECTS:
            obj = RegisteredObject(
                user_id=DEFAULT_USER_ID,
                label=obj_data["label"],
                display_name=obj_data["display_name"],
                coco_label=obj_data["coco_label"],
            )
            session.add(obj)
            await session.flush()

            mem_data = SEED_MEMORIES[obj_data["label"]]
            memory = Memory(
                user_id=DEFAULT_USER_ID,
                title=mem_data["title"],
                narrative_text=mem_data["narrative_text"],
                is_ai_generated=False,
            )
            session.add(memory)
            await session.flush()

            link = MemoryObject(
                memory_id=memory.id, object_id=obj.id, is_primary=True
            )
            session.add(link)

        await session.commit()
        print("Seeded 4 memories with registered objects.")


if __name__ == "__main__":
    asyncio.run(seed())
