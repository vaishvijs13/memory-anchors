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
        "title": "Reading Spot",
        "narrative_text": (
            "Every evening, after the world quieted down, Grandpa would sink into "
            "this worn leather chair by the window. The lamp cast a warm glow as "
            "he'd read aloud\u2014his voice steady and kind. I'd sit at his feet, "
            "lost in stories of faraway lands. That chair held more than books; "
            "it held our unspoken bond."
        ),
    },
    "book": {
        "title": "Favorite Stories",
        "narrative_text": (
            "Mom's copy of 'The Velveteen Rabbit' was falling apart, pages soft "
            "from years of bedtime readings. She'd trace the illustrations with "
            "her finger, and I'd watch her eyes shimmer when the rabbit became "
            "real. That tattered book taught me love makes things real\u2014even now, "
            "holding it brings her voice back to me."
        ),
    },
    "tv": {
        "title": "Family Nights",
        "narrative_text": (
            "Sunday nights meant the whole family piled onto the couch\u2014knees "
            "bumping, blankets shared. Dad controlled the remote like a sacred "
            "artifact. We'd laugh at the same jokes, groan at the same "
            "cliffhangers. Those glowing evenings weren't about what we watched; "
            "they were the last time we were all together, simply happy."
        ),
    },
    "laptop": {
        "title": "Letters & Photos",
        "narrative_text": (
            "After she moved overseas, this laptop became our bridge. Late-night "
            "video calls where we'd both pretend the distance didn't ache. She'd "
            "email photos of her tiny apartment, and I'd send back pictures of the "
            "dog she missed. Every notification was a small proof: miles couldn't "
            "break what we built."
        ),
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
