from django import template
from itsdangerous import URLSafeSerializer, BadData

register = template.Library()

@register.filter(name="serialize_id")
def serialize_id(user_id, event_id):
    serial = URLSafeSerializer('some_secret_key',
                                salt='presence')

    data = {'user_id': user_id,
            'event_id': event_id}
    return serial.dumps(data)
