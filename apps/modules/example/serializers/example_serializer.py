"""Example module serializers.

Plain dict serializers (framework-agnostic). If the project adopts DRF,
replace these with ``rest_framework.serializers.ModelSerializer`` subclasses
while keeping the same field names.
"""


def serialize_example_item(item):
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


def serialize_example_item_list(items):
    return [serialize_example_item(item) for item in items]
