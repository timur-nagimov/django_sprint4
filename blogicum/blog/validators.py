from datetime import datetime

from django.core.exceptions import ValidationError
from django.utils import timezone


def correct_datetime(value: datetime) -> None:
    # время с учетом часового пояса
    now_aware = timezone.now()

    if value < now_aware:
        raise ValidationError(
            'Дата и время публикации должны быть в будущем.'
        )
