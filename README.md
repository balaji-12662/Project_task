content = """# Employee Review System

A Django REST Framework (DRF) application for managing **employee performance reviews**.  
It supports review cycles, multiple reviewers, score criteria, bulk CSV/JSON import, and secure API authentication.

---

## 🚀 Features
- Manage Employees, Review Cycles, Reviews, and Scores
- Role-based permissions (Admin, Reviewer, Employee)
- Token-based authentication (DRF)
- Bulk Import Reviews (CSV / JSON)
- Prevent duplicate reviews with `get_or_create`
- Criteria-based scoring (`technical`, `communication`, `leadership`, `goals`)
- Extensible for future integrations

---

## 🛠️ Tech Stack
- **Python 3.9+**
- **Django 4+**
- **Django REST Framework**
- **SQLite / PostgreSQL** (configurable)
- **JWT / Token Authentication**

---

## ⚙️ Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/employee-review-system.git
cd employee-review-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # on Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver
