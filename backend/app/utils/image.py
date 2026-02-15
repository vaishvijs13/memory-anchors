import base64
import io


def decode_base64_image(data: str) -> bytes:
    """Decode a base64-encoded image string, stripping any data URI prefix."""
    if "," in data:
        data = data.split(",", 1)[1]
    return base64.b64decode(data)


def encode_base64_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    """Encode bytes to a data URI string."""
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{b64}"
