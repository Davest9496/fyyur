"""
Module description:
This module contains functions for loading sample data into the database.
It includes methods to create artists, venues, and shows.
"""

from datetime import datetime
from app import app, db
from models import Artist, Show, Venue
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


def load_artists_and_shows():
    """
    Load sample artists and shows into the database.
    """
    with app.app_context():
        try:
            # First, clear existing artists and shows to avoid conflicts
            db.session.query(Show).delete()
            db.session.query(Artist).delete()
            db.session.commit()

            # Get existing venues
            venues = Venue.query.all()
            if not venues:
                print("No venues found in database. Please load venues first.")
                return

            print(f"Found {len(venues)} venues in database.")
            for venue in venues:
                print(f"Venue ID: {venue.id}, Name: {venue.name}")

            # Create artists
            artist1 = Artist(
                name="Guns N Petals",
                genres=["Rock n Roll"],
                city="San Francisco",
                state="CA",
                phone="326-123-5000",
                website_link="https://www.gunsnpetalsband.com",
                facebook_link="https://www.facebook.com/GunsNPetals",
                seeking_venue=True,
                seeking_description="Looking for shows to perform at in the San Francisco Bay Area!",
                image_link="https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
            )

            artist2 = Artist(
                name="Matt Quevedo",
                genres=["Jazz"],
                city="New York",
                state="NY",
                phone="300-400-5000",
                facebook_link="https://www.facebook.com/mattquevedo923251523",
                seeking_venue=False,
                image_link="https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80"
            )

            artist3 = Artist(
                name="The Wild Sax Band",
                genres=["Jazz", "Classical"],
                city="San Francisco",
                state="CA",
                phone="432-325-5432",
                seeking_venue=False,
                image_link="https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80"
            )

            # Add and commit artists
            db.session.add(artist1)
            db.session.add(artist2)
            db.session.add(artist3)
            db.session.commit()

            print(
                f"Artists created. IDs: {artist1.id}, {artist2.id}, {artist3.id}")

            # Use the first venue for Musical Hop, third for Park Square
            # (assuming they were loaded in the original order)
            venue_musical_hop = venues[0] if len(venues) > 0 else None
            venue_park_square = venues[2] if len(venues) > 2 else None

            if not venue_musical_hop or not venue_park_square:
                print(
                    "Required venues not found. Make sure venues are loaded in the correct order.")
                return

            print(
                f"Using venues: {venue_musical_hop.name} (ID: {venue_musical_hop.id}) and {venue_park_square.name} (ID: {venue_park_square.id})")

            # Examine the Show model
            print(
                f"Show model attributes: {[column.name for column in Show.__table__.columns]}")

            try:
                # Create shows manually without specifying id
                show1 = Show(
                    artist_id=artist1.id,
                    venue_id=venue_musical_hop.id,
                    start_time=datetime.fromisoformat("2019-05-21T21:30:00")
                )

                db.session.add(show1)
                db.session.commit()
                print(f"First show added successfully with id: {show1.id}")

                # Continue with the rest of the shows
                show2 = Show(
                    artist_id=artist2.id,
                    venue_id=venue_park_square.id,
                    start_time=datetime.fromisoformat("2019-06-15T23:00:00")
                )
                db.session.add(show2)

                show3 = Show(
                    artist_id=artist3.id,
                    venue_id=venue_park_square.id,
                    start_time=datetime.fromisoformat("2035-04-01T20:00:00")
                )
                db.session.add(show3)

                show4 = Show(
                    artist_id=artist3.id,
                    venue_id=venue_park_square.id,
                    start_time=datetime.fromisoformat("2035-04-08T20:00:00")
                )
                db.session.add(show4)

                show5 = Show(
                    artist_id=artist3.id,
                    venue_id=venue_park_square.id,
                    start_time=datetime.fromisoformat("2035-04-15T20:00:00")
                )
                db.session.add(show5)

                db.session.commit()
                print("All shows added successfully!")

            except (SQLAlchemyError, IntegrityError) as e:
                db.session.rollback()
                print(f"Error creating shows: {str(e)}")
                print("Show schema may require manual ID assignment.")

                # Try with explicit ID assignment
                print("Attempting with explicit ID assignment...")
                show1 = Show(
                    id=1,  # Explicitly set ID
                    artist_id=artist1.id,
                    venue_id=venue_musical_hop.id,
                    start_time=datetime.fromisoformat("2019-05-21T21:30:00")
                )
                db.session.add(show1)
                db.session.commit()
                print("Show added with explicit ID assignment.")

            print("Sample artists and shows loaded successfully!")

        except (SQLAlchemyError, IntegrityError) as e:
            db.session.rollback()
            print(f"Error loading sample data: {str(e)}")

        finally:
            db.session.close()


if __name__ == "__main__":
    load_artists_and_shows()
