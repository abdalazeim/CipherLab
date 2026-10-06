# Django Enterprise Starter Template

قالب Django احترافي قابلة لإعادة الاستخدام لنظم الأعمال. يتبع معمارية Modular Monolith مع فصل كامل بين Core والوحداتBusiness، ويدعم التطوير المحلي و Docker و الإنتاج (Render / Neon / Linux).

## البنية

```
project/
├── config/                    # إعدادات Django (base/development/test/production/desktop)
│   ├── settings/
│   │   ├── base.py           # إعدادات مشتركة
│   │   ├── development.py    # تطوير محلي
│   │   ├── test.py           # اختبارات سريعة (SQLite في الذاكرة)
│   │   ├── production.py     # إنتاج (SSL/HSTS/secure cookies)
│   │   └── desktop.py        # PyInstaller Desktop
│   ├── urls.py               # URLs رئيسية
│   └── api_urls.py           # جدول توجيه API موحد
│
├── apps/
│   ├── core/                  # نواة مستقلة عن مجال العمل
│   │   ├── models/           # BaseModel, AuditLog, SystemSetting, LookupCategory
│   │   ├── services/         # Audit, Backup, Security, System Settings
│   │   ├── middleware/       # Security, Rate Limit, Language Switch
│   │   ├── repositories/     # Base Repository Pattern
│   │   ├── utils/            # HTTP helpers, Exceptions, Decorators, Validators
│   │   ├── constants/        # Permission codes, Audit actions
│   │   ├── management/       # أوامر (startmodule، seed_data، backup_db)
│   │   ├── views/            # Dashboard, Health, Backup, Settings
│   │   └── tests/            # Unit tests for core
│   │
│   ├── accounts/              # مستقل - Authentication & Authorization
│   │   ├── models/           # User, UserGroup, SystemRole, UserProfile
│   │   ├── services/         # Permission resolution
│   │   ├── views/            # Auth, Users, Groups, Roles
│   │   ├── permissions/      # Permission catalog
│   │   └── urls.py
│   │
│   └── modules/               # Units modules (قابلة للإضافة والحذف)
│       └── example/           # وحدة مثال - مرجع لإنشاء وحدات جديدة
│           ├── models/
│           ├── services/
│           ├── repositories/
│           ├── views/
│           ├── serializers/
│           ├── forms/
│           ├── permissions.py
│           ├── urls.py
│           ├── admin.py
│           └── tests/
│
├── templates/
│   ├── base/
│   ├── layouts/              # app_layout, auth_layout
│   ├── pages/                # index, login, example_page
│   ├── components/           # table, modal, card, form, alert, breadcrumb
│   ├── partials/             # sidebar, navbar, footer
│   ├── forms/
│   ├── errors/
│   └── pdf/
│
├── static/
│   ├── css/
│   ├── js/
│   ├── fonts/
│   ├── images/
│   └── vendor/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── api/
│   └── e2e/
│
├── scripts/
│   ├── seed_data.py
│   ├── health_check.py
│   ├── verify_api.py
│   └── check_static_refs.py
│
├── deployment/
│   ├── docker/
│   │   ├── Dockerfile
│   │   └── docker-compose.yml
│   ├── nginx/
│   │   └── nginx.conf
│   └── gunicorn/
│       └── gunicorn.conf.py
│
├── docs/
│   ├── architecture/
│   ├── development/
│   ├── deployment/
│   ├── api/
│   ├── database/
│   └── security/
│
├── manage.py
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
└── README.md
```

## المتطلبات

- Python 3.11+
- PostgreSQL 16+ (إنتاج) أو SQLite (تطوير)
- venv مفعّل

## التثبيت السريع

```bash
# 1. نسخ المتغيرات
copy .env.example .env

# 2. تثبيت الاعتمادات
pip install -r requirements.txt

# 3. تشغيل الهجرات
python manage.py makemigrations
python manage.py migrate

# 4. إنشاء مشرف (اختياري - أو استخدم create_admin)
python manage.py createsuperuser

# 5. تشغيل الخادم
python manage.py runserver
```

## الاختبارات

```bash
# اختبارات سريعة (SQLite في الذاكرة)
python manage.py test --settings=config.settings.test

# فحص النظام
python manage.py check

# فحص الهجرات
python manage.py makemigrations --check

# تحقق API
python scripts\verify_api.py
```

## البيئات

| البيئة | الإعدادات | ملاحظات |
|--------|-----------|---------|
| تطوير | `config.settings.development` | DEBUG=True, SQLite |
| اختبار | `config.settings.test` | SQLite في الذاكرة |
| إنتاج | `config.settings.production` | DEBUG=False, SSL/HSTS |
| سطح مكتب | `config.settings.desktop` | PyInstaller |

## API Versioning

- `/api/` — legacy/default
- `/api/v1/` — explicit versioned namespace
- Unified response envelope: `{success, message, data, errors}`

## النشر

### Docker
```bash
docker compose up -d
```

### Render
- يستخدم `Procfile` و `render.yaml`
- يدعم Neon PostgreSQL

### Linux Server
- Nginx + Gunicorn + PostgreSQL
- انظر `docs/deployment/`

## بناء نظام جديد من القالب

هذا القالب "جهاز جاهز" لبناء أي نظام أعمال — خالٍ تماماً من منطق أي مجال محدد:

1. **التخصيص السريع** — غيّر الاسم والشعار من متغيرات البيئة (`.env`):
   ```env
   SITE_TITLE=نظامي الجديد
   SITE_SUBTITLE=الإصدار الأول
   ```
2. **أنشئ وحداتك** بالأمر الآلي `startmodule` (يولّد النماذج/الخدمات/API/الصفحة/القائمة/الصلاحيات ويُسجّل كل شيء تلقائياً).
3. **عيّن الصلاحيات** — كل وحدة تولّد صلاحياتها الخاصة (`<module>_view` / `<module>_manage` / `nav_<module>`) وتظهر في صفحة إدارة المستخدمين تلقائياً.
4. **كل وحدة مستقلة وقابلة للإزالة** — تحذفها بحذف مجلدها وسطر `INSTALLED_APPS` فقط.

## إضافة وحدة جديدة (Module)

```bash
# أمر واحد يولّد الوحدة كاملة ويسجّلها تلقائياً:
python manage.py startmodule purchase_orders --label "أوامر الشراء"

# ثم طبّق الهجرات
python manage.py migrate
```

ما يفعله الأمر تلقائياً:
- ينشئ `apps/modules/purchase_orders/` بنفس هيكل وحدة `example` (models / services / repositories / serializers / views / urls / permissions / admin / tests / migrations).
- يسجّل التطبيق في `INSTALLED_APPS` (`config/settings/base.py`).
- يركّب الـ API تحت `/api/modules/purchase_orders/` في `config/api_urls.py`.
- يضيف عنصر قائمة + صفحة SPA + سكربت الصفحة + صلاحيات (`purchase_orders_view`، `purchase_orders_manage`، `nav_purchase_orders`).
- يولّد هجرة واختبارات جاهزة (`python manage.py test apps/modules/purchase_orders --settings=config.settings.test`).

> بعد التوليد، عدّل النموذج في `apps/modules/<name>/models/` وأضف حقول مجال عملك، ثم `python manage.py makemigrations <name>` و `migrate`.

لمعاينة مخرجات الأمر، شغّله على أي اسم ثم أنظر إلى المجلد المولّد، أو راجع وحدة `apps/modules/example/` المكتوبة يدوياً كمرجع.

## معمارية وحدات الأعمال

```
apps/modules/<module_name>/
├── models/          # نماذج قاعدة البيانات (ترث BaseModel)
├── services/        # منطق الأعمال + سجل التدقيق (log_audit)
├── repositories/    # طبقة الوصول للبيانات (BaseRepository)
├── serializers/     # تحويل النماذج إلى JSON
├── views/           # واجهات API رفيعة
├── permissions/     # صلاحيات الوحدة (تسجّل تلقائياً)
├── urls.py          # مسارات API الخاصة بالوحدة
├── admin.py         # واجهة Django Admin
├── tests/           # اختبارات الوحدة
└── migrations/
```

كل وحدة مستقلة تماماً: تعتمد على `core` و `accounts` فقط، ولا تؤثر على الوحدات الأخرى. سجل التدقيق العام (`AuditLog`) يجمع كل العمليات من كل الوحدات في لوحة التحكم والتقارير.

## الميزات

- **Core مستقل**: لا يحتوي على أي منطق عمل مجال محدد
- **Accounts مستقل**: مستخدمين، مجموعات، أدوار، صلاحيات
- **Service Layer**: منطق العمل منفصل عن الـ Views
- **Repository Pattern**: تجريد قاعدة البيانات
- **API Versioned**: `/api/v1/` مع دعم الإصدارات المستقبلية
- **Audit Logging**: سجل تدقيق عام لجميع العمليات
- **Security Headers**: HSTS, CSRF, CORS, XSS Protection
- **RTL/LTR**: دعم كامل للعربية والإنجليزية
- **Docker Ready**: docker-compose للتطوير والإنتاج
- **Render Compatible**: نشر تلقائي على Render
- **Neon Compatible**: PostgreSQL سحابي
- **Desktop Support**: PyInstaller للعمل بدون إنترنت

## Architecture Rules

1. **Core لا يعتمد على Modules**
2. **Accounts يعتمد فقط على Core**
3. **Business Modules تعتمد على Core + Accounts**
4. **لا Business Logic في Templates**
5. **لا Hard-coded Configuration**
6. **كل Module مستقل وقابل للإزالة**

## License

MIT
