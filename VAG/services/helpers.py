from VAG.models import Service
import secrets

def get_previous_next_lesson(lesson):
    previous_lesson = Service.query.filter(
        Service.service_id == lesson.service_id,
        Service.id < lesson.id
    ).order_by(Service.id.desc()).first()

    next_lesson = Service.query.filter(
        Service.service_id == lesson.service_id,
        Service.id > lesson.id
    ).order_by(Service.id.asc()).first()

    return previous_lesson, next_lesson

def slugify(text: str) -> str:
    """
    Simple, dependency-free slugify:
    - lower, keep alnum and hyphens
    - spaces/underscores -> hyphens
    - collapse multiple hyphens
    """
    import re
    text = (text or "").strip().lower()
    text = re.sub(r'[ _]+', '-', text)
    text = re.sub(r'[^a-z0-9\-]', '', text)
    text = re.sub(r'-{2,}', '-', text).strip('-')
    return text or secrets.token_hex(4)
