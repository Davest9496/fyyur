"""
Module containing SQLAlchemy models for the Fyyur project.

This module defines the database models for venues, artists, and shows.
It uses SQLAlchemy for object-relational mapping and Flask-Migrate for database migrations.
"""

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    """
Represents a venue in the Fyyur database.

Attributes:
    id (int): Unique identifier for the venue.
    name (str): Name of the venue.
    city (str): City where the venue is located.
    state (str): State where the venue is located.
    address (str): Address of the venue.
    phone (str): Phone number of the venue.
    genres (list): List of genres the venue supports.
    image_link (str): URL of the venue's image.
    facebook_link (str): Facebook link of the venue.
    website_link (str): Website link of the venue.
    seeking_talent (bool): Whether the venue is currently looking for talent.
    seeking_description (str): Description of what kind of talent the venue is seeking.
    created_at (datetime): Timestamp when the venue was created.
"""
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    shows = db.relationship('Show', backref='venue', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'


class Artist(db.Model):
    """
    Represents an artist in the Fyyur database.

    Attributes:
        id (int): Unique identifier for the artist.
        name (str): Name of the artist.
        city (str): City where the artist is located.
        state (str): State where the artist is located.
        phone (str): Phone number of the artist.
        genres (list): List of genres the artist supports.
        image_link (str): URL of the artist's image.
        facebook_link (str): Facebook link of the artist.
        website_link (str): Website link of the artist.
        seeking_venue (bool): Whether the artist is currently looking for venues.
        seeking_description (str): Description of what kind of venues the artist is seeking.
        created_at (datetime): Timestamp when the artist was created.
    """
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    shows = db.relationship('Show', backref='artist',
                            lazy=True, cascade="all, delete-orphan")
    availabilities = db.relationship(
        'Availability', backref='artist', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'

class Show(db.Model):
    """
    Represents a show in the Fyyur database.

    Attributes:
        id (int): Unique identifier for the show.
        artist_id (int): Foreign key referencing the Artist model.
        venue_id (int): Foreign key referencing the Venue model.
        start_time (DateTime): Start time of the show.
    """
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Show {self.id}, Artist {self.artist_id}, Venue {self.venue_id}>'


class Availability(db.Model):
    """
    Represents availability information for an artist in the Fyyur database.

    Attributes:
        id (int): Unique identifier for the availability entry.
        artist_id (int): Foreign key referencing the Artist model.
        day_of_week (int): Day of the week (0=Monday, 6=Sunday).
        start_time (Time): Start time of the availability period.
        end_time (Time): End time of the availability period.
    """
    __tablename__ = 'availability'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artists.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    
    def __repr__(self):
        return f'<Availability {self.id}, Artist: {self.artist_id}, Day: {self.day_of_week}>'
