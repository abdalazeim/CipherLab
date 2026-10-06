"""مديول -1 serializers (plain dict serializers)."""


def serialize_module_1_item(item):
    return {
        "id": item.pk,
        "name": item.name,
        "code": item.code,
        "description": item.description,
        "quantity": item.quantity,
        "sort_order": item.sort_order,
        "is_active": item.is_active,
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "updated_at": item.updated_at.isoformat() if item.updated_at else None,
    }


def serialize_module_1_item_list(items):
    return [serialize_module_1_item(item) for item in items]
