"""مديول -1 permission catalog.

Registered into the central permission registry via ``apps.ready()``.
"""

PERMISSIONS = [
    {"code": "module_1_view", "label": "عرض مديول -1", "group": "module_1"},
    {
        "code": "module_1_manage",
        "label": "إدارة مديول -1 (إضافة/تعديل/حذف)",
        "group": "module_1",
    },
    {"code": "nav_module_1", "label": "قائمة مديول -1", "group": "nav"},
]

GROUPS = [
    {"key": "module_1", "label": "مديول -1", "icon": "fa-cubes"},
]
