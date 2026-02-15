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
        title="Grandpa's Chair",
        memory_text="Grandpa always sat in this chair after dinner. He'd read to me while I sat on the floor next to him. I remember the way his voice got all soft during the sad parts. The leather's cracked now but it still smells like his pipe tobacco if you lean in close.",
    ),
    "book": MemoryAnchor(
        object_label="book",
        title="Mom's Bedtime Book",
        memory_text="Mom read this to me so many times the spine fell apart. She had to hold the pages together. I used to ask her to do the rabbit's voice over and over. She never got tired of it, or at least she never let on if she did.",
    ),
    "tv": MemoryAnchor(
        object_label="tv",
        title="Sunday Movies",
        memory_text="We'd all cram onto the couch on Sunday nights. Dad would make popcorn with too much butter, the way we liked it. Nobody was allowed to talk during the movie but we'd all look at each other during the funny parts. I miss that.",
    ),
    "laptop": MemoryAnchor(
        object_label="laptop",
        title="Video Calls with Sarah",
        memory_text="When Sarah moved away, we started doing video calls every week on this laptop. Sometimes we'd just sit there not saying much. She'd show me her apartment, I'd show her the dog. It helped, knowing she was right there on the screen even though she was so far away.",
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
