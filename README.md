
# Gallery Backend

This is the backend of the Gallery project, built with Django. It provides the API and logic to manage gallery-related operations.

## Prerequisites

- Python 3.8+
- Ubuntu or any Linux-based system (or equivalent)
- Git

## Setup Instructions

# 1. Create Project Directory
```bash
mkdir Gallery-Backend
cd Gallery-Backend
```

# 2. Create and Activate a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

# 3. Clone the Repository
```bash
git clone https://github.com/FadyM66/GalleryBackend.git
cd GalleryBackend
```
# 4. Update and Upgrade the System
```bash
sudo apt update
sudo apt upgrade -y
```
# 5. Install Python
```bash
sudo apt install python3 python3-pip python3-venv -y

# 6. Install Django
pip install django
```
# 7. Install Project Dependencies
```bash
pip install -r requirements.txt
```
# 8. Run Database Migrations
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```
# 9. Run the Development Server
```bash
python3 manage.py runserver
```
# PROJECT STRUCTURE
```bash
Gallery-Backend/
├── venv/                    # Virtual environment directory
├── gallery/                  # Main Django app folder
│   ├── authentication/       # Handles user authentication
│   ├── gallery/              # Manages gallery-related functionality
│   ├── image/                # Manages image-related functionality
├── manage.py                 # Django project management script
├── requirements.txt          # Python dependencies required for the project
├── .env                      # Environment variables file (for sensitive data like SECRET_KEY)
```
