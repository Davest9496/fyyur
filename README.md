# Fyyur: Artist and Venue Booking Platform

## Overview
Fyyur is a musical venue and artist booking platform that facilitates the discovery and booking of performances between local performing artists and venues. The site enables artists to list themselves, venues to list their spaces, and users to discover and book shows.

## Key Features
- **Venue Management**: Create, search, view, and edit venue listings with details including location, genres, contact information, and talent requirements
- **Artist Management**: Register artists, browse profiles, and manage artist information including genres, contact details, and venue seeking status
- **Show Booking**: Create and view upcoming and past shows connecting artists with venues
- **Advanced Search**: Search artists and venues by name, city, and state
- **Artist Availability**: Artists can set and manage their availability by day of week and time slots
- **Data Visualization**: View shows by venue or artist with clear distinctions between past and upcoming events

## Tech Stack

### Backend
- **Python 3** and **Flask** framework for server-side operations
- **SQLAlchemy ORM** for database interaction
- **PostgreSQL** as the relational database
- **Flask-Migrate** for database schema migrations
- **Flask-WTF** for form handling and validation

### Frontend
- **HTML/CSS/JavaScript** for user interface
- **Bootstrap 3** for responsive design
- **Font Awesome** for icons
- **Moment.js** for date/time manipulation

## Setup Instructions

### Prerequisites
- Python 3.9 or lower
- PostgreSQL installed and running
- Node.js and npm for frontend dependencies

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone <your-repository-url>
   cd fyyur
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m virtualenv env
   
   # On macOS/Linux
   source env/bin/activate
   
   # On Windows
   source env/Scripts/activate
   ```

3. **Install backend dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install frontend dependencies**:
   ```bash
   npm init -y
   npm install bootstrap@3
   ```

5. **Configure the database**:
   - Create a PostgreSQL database:
     ```bash
     createdb fyyur
     ```
   - Update `config.py` with your database URI if needed:
     ```python
     SQLALCHEMY_DATABASE_URI = 'postgresql://postgres@localhost:5432/fyyur'
     ```

6. **Run database migrations**:
   ```bash
   flask db upgrade
   ```

7. **Start the application**:
   ```bash
   export FLASK_APP=app.py
   export FLASK_ENV=development
   flask run
   ```

8. **Access the application** in your browser at [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

## Project Structure

```
fyyur/
│
├── app.py                  # Main application file with routes and controllers
├── models.py               # Database models
├── forms.py                # Form definitions
├── config.py               # Configuration settings
├── cli.py                  # CLI commands
│
├── migrations/             # Database migration files
│   ├── versions/           # Migration version files
│   └── ...
│
├── static/                 # Static assets
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript files
│   ├── fonts/              # Font files
│   └── img/                # Image files
│
├── templates/              # HTML templates
│   ├── errors/             # Error pages
│   ├── forms/              # Form templates
│   ├── layouts/            # Layout templates
│   └── pages/              # Page templates
│
└── requirements.txt        # Python dependencies
```

## Data Models

### Venue
Represents a physical location where shows can be held:
- Basic info (name, city, state, address, phone)
- Genre classification
- External links (website, Facebook)
- Talent seeking status
- Image link
- Associated shows

### Artist
Represents a performing artist:
- Basic info (name, city, state, phone)
- Genre classification
- External links (website, Facebook)
- Venue seeking status
- Image link
- Availability schedule
- Associated shows

### Show
Represents a booking event connecting artists with venues:
- References to venue and artist
- Start time
- Automatically classified as past or upcoming

### Availability
Represents time slots when an artist is available for bookings:
- Day of week
- Time range (start and end)
- Associated artist

## Advanced Features

### Advanced Search
The application supports searching for venues and artists by:
- Name
- City
- State
- Combined formats like "Name, City, State"

### Artist Availability Management
Artists can:
- Set available time slots by day of week
- Specify time ranges when they're available for bookings
- Delete availability slots
- View their availability schedule in an organized format

## Troubleshooting

If you encounter dependency errors:
- Ensure you're using Python 3.9 or lower
- Try updating specific packages:
  ```bash
  pip install --upgrade flask-moment
  pip install Werkzeug==2.0.0
  pip uninstall Flask && pip install flask==2.0.3
  ```

## Future Enhancements
- Implement user authentication and roles
- Add a booking request system
- Create a notification system for new shows
- Add ratings and reviews for venues and artists
- Implement a recommendation engine

## License
This project is licensed under the MIT License - see the LICENSE file for details.
