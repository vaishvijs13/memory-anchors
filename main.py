from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Memory Anchors API")

# Enable CORS for local React dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MemoryAnchor(BaseModel):
    object_label: str
    title: str
    memory_text: str
    audio_url: Optional[str] = None


# In-memory store with seed data
memory_store: dict[str, MemoryAnchor] = {
    "chair": MemoryAnchor(
        object_label="chair",
        title="Reading Spot",
        memory_text="Every evening, after the world quieted down, Grandpa would sink into this worn leather chair by the window. The lamp cast a warm glow as he'd read aloud—his voice steady and kind. I'd sit at his feet, lost in stories of faraway lands. That chair held more than books; it held our unspoken bond.",
    ),
    "book": MemoryAnchor(
        object_label="book",
        title="Favorite Stories",
        memory_text="Mom's copy of 'The Velveteen Rabbit' was falling apart, pages soft from years of bedtime readings. She'd trace the illustrations with her finger, and I'd watch her eyes shimmer when the rabbit became real. That tattered book taught me love makes things real—even now, holding it brings her voice back to me.",
    ),
    "tv": MemoryAnchor(
        object_label="tv",
        title="Family Nights",
        memory_text="Sunday nights meant the whole family piled onto the couch—knees bumping, blankets shared. Dad controlled the remote like a sacred artifact. We'd laugh at the same jokes, groan at the same cliffhangers. Those glowing evenings weren't about what we watched; they were the last time we were all together, simply happy.",
    ),
    "laptop": MemoryAnchor(
        object_label="laptop",
        title="Letters & Photos",
        memory_text="After she moved overseas, this laptop became our bridge. Late-night video calls where we'd both pretend the distance didn't ache. She'd email photos of her tiny apartment, and I'd send back pictures of the dog she missed. Every notification was a small proof: miles couldn't break what we built.",
    ),
}


@app.get("/health")
def health_check():
    return {"ok": True}


@app.get("/memory", response_model=list[MemoryAnchor])
def list_memories():
    return list(memory_store.values())


@app.get("/memory/{object_label}", response_model=MemoryAnchor)
def get_memory(object_label: str):
    label = object_label.lower().strip()
    if label not in memory_store:
        raise HTTPException(status_code=404, detail=f"No memory found for '{object_label}'")
    return memory_store[label]


@app.post("/memory", response_model=MemoryAnchor)
def create_or_update_memory(anchor: MemoryAnchor):
    label = anchor.object_label.lower().strip()
    anchor.object_label = label
    memory_store[label] = anchor
    return anchor
