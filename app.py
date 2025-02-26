"""
Fyyur: Musical Venue and Artist Booking Site

This module contains the main Flask application for Fyyur,
which facilitates bookings between local performing artists and venues.
"""

import logging
import sys
from datetime import datetime, time
from logging import FileHandler, Formatter

import babel
import dateutil.parser
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_migrate import Migrate
from flask_moment import Moment
from sqlalchemy.exc import SQLAlchemyError

from forms import ArtistForm, AvailabilityForm, ShowForm, VenueForm
from models import Artist, Availability, Show, Venue, db
from cli import register_commands

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# Import models after app is created

db.init_app(app)
migrate = Migrate(app, db)
register_commands(app)

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, fmt='medium'):
    """
      Format a datetime string according to the specified format.

      Args:
          value (str): The input datetime string.
          fmt (str): The desired output format. Can be 'full' or 'medium'.

      Returns:
          str: The formatted datetime string.
      """
    date = dateutil.parser.parse(value)
    if fmt == 'full':
        fmt = "EEEE MMMM, d, y 'at' h:mma"
    elif fmt == 'medium':
        fmt = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, fmt, locale='en')

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    """
    Render the home page template.

    Returns:
        str: The rendered 'home.html' template.
    """
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    """
    Query venues grouped by city and state.

    Returns:
        dict: A dictionary containing venues grouped by location.
    """
    venues_by_location = {}
    all_venues = Venue.query.all()
    for venue in all_venues:
        location = (venue.city, venue.state)
        if location not in venues_by_location:
            venues_by_location[location] = {
                "city": venue.city,
                "state": venue.state,
                "venues": []
            }

        # Count upcoming shows
        upcoming_shows = db.session.query(Show).filter(
            Show.venue_id == venue.id,
            Show.start_time > datetime.now()
        ).count()

        venues_by_location[location]["venues"].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": upcoming_shows
        })

    # Convert to list for template
    data = list(venues_by_location.values())
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    """
    Handle POST requests for venue search.

    Searches for venues based on the search term provided in the request form.
    Returns a JSON response with count of venues found and the list of venues.

    Args:
        None

    Returns:
        dict: A dictionary containing the count of venues and the list of venues.
    """
    search_term = request.form.get('search_term', '')
    search_results = Venue.query.filter(
        Venue.name.ilike(f'%{search_term}%')).all()

    response = {
        "count": len(venues),
        "data": []
    }

    for venue in search_results:
        upcoming_shows = db.session.query(Show).filter(
            Show.venue_id == venue.id,
            Show.start_time > datetime.now()
        ).count()

        response["data"].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": upcoming_shows
        })

    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    """
    Display detailed information about a specific venue.

    Args:
        venue_id (int): The ID of the venue to display.

    Returns:
        dict: A dictionary containing venue information and past/upcoming shows.
    """
    # Get venue by ID
    venue = Venue.query.get_or_404(venue_id)

    # Get past shows
    past_shows_query = db.session.query(Show).join(Artist).filter(
        Show.venue_id == venue_id,
        Show.start_time < datetime.now()
    ).all()

    past_shows = []
    for show in past_shows_query:
        past_shows.append({
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        })

    # Get upcoming shows
    upcoming_shows_query = db.session.query(Show).join(Artist).filter(
        Show.venue_id == venue_id,
        Show.start_time >= datetime.now()
    ).all()

    upcoming_shows = []
    for show in upcoming_shows_query:
        upcoming_shows.append({
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        })

    # Format data for template
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    """
    Renders the form for creating a new venue.

    Returns:
        str: The rendered 'forms/new_venue.html' template with the VenueForm instance.
    """
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    """
    Handles the submission of a new venue creation form.

    Processes the form data, creates a new venue record, and handles potential errors.

    Args:
        None

    Returns:
        str: The rendered 'pages/home.html' template with a success or error message.

    Raises:
        Exception: If there's an error during venue creation.
    """
    error = False
    form = VenueForm(request.form)

    try:
        venue = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            genres=form.genres.data,
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
            website=form.website_link.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data
        )

        db.session.add(venue)
        db.session.commit()
    except SQLAlchemyError:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
    else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    """
    Deletes a venue by its ID.

    Args:
        venue_id (int): The ID of the venue to be deleted.

    Returns:
        None

    Raises:
        Exception: If there's an error during deletion.
    """
    error = False
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except SQLAlchemyError as e:
        error = True
        db.session.rollback()
        print(e)
    finally:
        db.session.close()

    if error:
        flash('An error occurred. Venue ' +
              str(venue_id) + ' could not be deleted.')
    else:
        flash('Venue ' + str(venue_id) + ' was successfully deleted.')

    return redirect(url_for('venues'))

#  Artists
#  ----------------------------------------------------------------


def artists():
    """
    Retrieve and format a list of all artists.

    Returns:
        list: A list of dictionaries containing artist information.
    """
    all_artists = Artist.query.order_by('name').all()
    data = []

    for artist in all_artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    """
    Handle POST requests for artist search.

    Searches for artists based on the search term provided in the request form.
    Returns a JSON response with count of artists found and the list of artists.

    Args:
        None

    Returns:
        dict: A dictionary containing the count of artists and the list of artists.

    """
    search_term = request.form.get('search_term', '')
    search_results = Artist.query.filter(
        Artist.name.ilike(f'%{search_term}%')).all()

    response = {
        "count": len(search_results),
        "data": []
    }

    for artist in search_results:
        upcoming_shows = db.session.query(Show).filter(
            Show.artist_id == artist.id,
            Show.start_time > datetime.now()
        ).count()

        response["data"].append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": upcoming_shows
        })

    return render_template('pages/search_artists.html', results=response, search_term=search_term)


def show_artist(artist_id):
    """
    Display detailed information about a specific artist.

    Args:
        artist_id (int): The ID of the artist to display.

    Returns:
        dict: A dictionary containing artist information and past/upcoming shows.
    """
    # Get artist by ID
    artist = Artist.query.get_or_404(artist_id)

    # Get past shows
    past_shows_query = db.session.query(Show).join(Venue).filter(
        Show.artist_id == artist_id,
        Show.start_time < datetime.now()
    ).all()

    past_shows = []
    for show in past_shows_query:
        past_shows.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        })

    # Get upcoming shows
    upcoming_shows_query = db.session.query(Show).join(Venue).filter(
        Show.artist_id == artist_id,
        Show.start_time >= datetime.now()
    ).all()

    upcoming_shows = []
    for show in upcoming_shows_query:
        upcoming_shows.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        })

    # Format data for template
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    """
    Render the form to edit an artist with the given artist_id.

    Args:
        artist_id (int): The ID of the artist to be edited.

    Returns:
        render_template: The rendered 'forms/edit_artist.html' template with the 
        ArtistForm instance and the artist data.
    """
    form = ArtistForm()
    artist = Artist.query.get_or_404(artist_id)

    # Pre-fill form with existing data
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    """
    Handles the submission of edits for an artist with the given artist_id.

    Updates the artist's information in the database based on the form data.

    Args:
        artist_id (int): The ID of the artist to be edited.

    Returns:
        redirect: Redirects to the artist's detail page after successful update.

    Raises:
        SQLAlchemyError: If there's an error during the update process.
    """
    error = False
    artist = Artist.query.get_or_404(artist_id)
    form = ArtistForm(request.form)

    try:
        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.genres = form.genres.data
        artist.facebook_link = form.facebook_link.data
        artist.image_link = form.image_link.data
        artist.website = form.website_link.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data

        db.session.commit()
    except SQLAlchemyError:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash('An error occurred. Artist could not be updated.')
    else:
        flash('Artist was successfully updated!')

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    """
    Render the form to edit a venue with the given venue_id.

    Args:
        venue_id (int): The ID of the venue to be edited.

    Returns:
        render_template: The rendered 'forms/edit_venue.html' template with the 
        VenueForm instance and the venue data.
    """
    form = VenueForm()
    venue = Venue.query.get_or_404(venue_id)

    # Pre-fill form with existing data
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website_link.data = venue.website
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    """
    Handles the submission of edits for a venue with the given venue_id.

    Updates the venue's information in the database based on the form data.

    Args:
        venue_id (int): The ID of the venue to be edited.

    Returns:
        redirect: Redirects to the venue's detail page after successful update.

    Raises:
        Exception: If there's an error during the update process.
    """
    error = False
    venue = Venue.query.get_or_404(venue_id)
    form = VenueForm(request.form)

    try:
        venue.name = form.name.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.address = form.address.data
        venue.phone = form.phone.data
        venue.genres = form.genres.data
        venue.facebook_link = form.facebook_link.data
        venue.image_link = form.image_link.data
        venue.website = form.website_link.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data

        db.session.commit()
    except SQLAlchemyError:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash('An error occurred. Venue could not be updated.')
    else:
        flash('Venue was successfully updated!')

    return redirect(url_for('show_venue', venue_id=venue_id))


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    """
    Renders the form for creating a new artist.

    Returns:
        str: The rendered 'forms/new_artist.html' template with the ArtistForm instance.
    """
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    """
    Handles the submission of a new artist creation form.
    Processes the form data, creates a new artist record, and handles potential errors.

    Args:
        None

    Returns:
        str: The rendered 'pages/home.html' template with a success or error message.

    Raises:
        Exception: If there's an error during artist creation.
    """
    error = False
    form = ArtistForm(request.form)

    try:
        artist = Artist(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            genres=form.genres.data,
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
            website=form.website_link.data,
            seeking_venue=form.seeking_venue.data,
            seeking_description=form.seeking_description.data
        )

        db.session.add(artist)
        db.session.commit()
    except SQLAlchemyError:
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    if error:
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')
    else:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    """
    Retrieves and formats a list of all shows.

    Returns:
        list: A list of dictionaries containing show information.

    This function queries the database for all shows, joins with venue and artist data,
    and formats it into a list of dictionaries for easy rendering in the template.
    """
    all_shows = Show.query.join(Venue).join(Artist).all()
    data = []

    for show in all_shows:
        data.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        })

    return render_template('pages/shows.html', shows=data)


def create_shows():
    """
    Renders the form for creating a new show.

    Returns:
        render_template: The rendered 'forms/new_show.html' template with the ShowForm instance.
    """
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    """
    Handles the submission of a new show creation form.
    Processes the form data, creates a new show record, and handles potential errors.

    Args:
        None

    Returns:
        str: The rendered 'pages/home.html' template with a success or error message.

    Raises:
        Exception: If there's an error during show creation.
    """
    error = False
    form = ShowForm(request.form)

    try:
        show = Show(
            artist_id=form.artist_id.data,
            venue_id=form.venue_id.data,
            start_time=form.start_time.data
        )

        db.session.add(show)
        db.session.commit()
    except SQLAlchemyError:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash('An error occurred. Show could not be listed.')
    else:
        flash('Show was successfully listed!')

    return render_template('pages/home.html')


@app.route('/venues/advanced-search', methods=['POST'])
def advanced_search_venues():
    """
    Search venues by name, city, and state.
    Format: "Name, City, State" - each part is optional
    Examples: 
        - "Musical, San Francisco, CA"
        - "San Francisco, CA"
        - "Music"
    """
    search_term = request.form.get('search_term', '')
    parts = [part.strip() for part in search_term.split(',')]

    # Initialize the query
    query = Venue.query

    # Apply filters based on parts provided
    if len(parts) == 1:
        # Just name
        query = query.filter(Venue.name.ilike(f'%{parts[0]}%'))
    elif len(parts) == 2:
        # City and State, or Name and City
        query = query.filter(
            (Venue.name.ilike(f'%{parts[0]}%') & Venue.city.ilike(f'%{parts[1]}%')) |
            (Venue.city.ilike(f'%{parts[0]}%') &
             Venue.state.ilike(f'%{parts[1]}%'))
        )
    elif len(parts) >= 3:
        # Name, City, and State
        query = query.filter(
            Venue.name.ilike(f'%{parts[0]}%') &
            Venue.city.ilike(f'%{parts[1]}%') &
            Venue.state.ilike(f'%{parts[2]}%')
        )

    search_results = query.all()

    response = {
        "count": len(search_results),
        "data": []
    }

    for venue in search_results:
        upcoming_shows = db.session.query(Show).filter(
            Show.venue_id == venue.id,
            Show.start_time > datetime.now()
        ).count()

        response["data"].append({
            "id": venue.id,
            "name": venue.name,
            "city": venue.city,
            "state": venue.state,
            "num_upcoming_shows": upcoming_shows
        })

    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/artists/advanced-search', methods=['POST'])
def advanced_search_artists():
    """
    Search artists by name, city, and state.
    Format: "Name, City, State" - each part is optional
    Examples: 
        - "Band, San Francisco, CA"
        - "New York, NY"
        - "Jazz"
    """
    search_term = request.form.get('search_term', '')
    parts = [part.strip() for part in search_term.split(',')]

    # Initialize the query
    query = Artist.query

    # Apply filters based on parts provided
    if len(parts) == 1:
        # Just name
        query = query.filter(Artist.name.ilike(f'%{parts[0]}%'))
    elif len(parts) == 2:
        # City and State, or Name and City
        query = query.filter(
            (Artist.name.ilike(f'%{parts[0]}%') & Artist.city.ilike(f'%{parts[1]}%')) |
            (Artist.city.ilike(f'%{parts[0]}%') &
             Artist.state.ilike(f'%{parts[1]}%'))
        )
    elif len(parts) >= 3:
        # Name, City, and State
        query = query.filter(
            Artist.name.ilike(f'%{parts[0]}%') &
            Artist.city.ilike(f'%{parts[1]}%') &
            Artist.state.ilike(f'%{parts[2]}%')
        )

    search_results = query.all()

    response = {
        "count": len(search_results),
        "data": []
    }

    for artist in search_results:
        upcoming_shows = db.session.query(Show).filter(
            Show.artist_id == artist.id,
            Show.start_time > datetime.now()
        ).count()

        response["data"].append({
            "id": artist.id,
            "name": artist.name,
            "city": artist.city,
            "state": artist.state,
            "num_upcoming_shows": upcoming_shows
        })

    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>/availability')
def artist_availability(artist_id):
    """
    Displays the availability schedule for an artist.

    Args:
        artist_id (int): The ID of the artist whose availability is being displayed.

    Returns:
        render_template: The rendered 'pages/artist_availability.html' template 
        with the artist's availability information.
    """
    # Get artist and their availability slots
    artist = Artist.query.get_or_404(artist_id)
    availabilities = Availability.query.filter_by(
        artist_id=artist_id).order_by('day_of_week', 'start_time').all()

    days = ['Monday', 'Tuesday', 'Wednesday',
            'Thursday', 'Friday', 'Saturday', 'Sunday']

    availability_by_day = {}
    for day_index, day in enumerate(days):
        availability_by_day[day] = [
            a for a in availabilities if a.day_of_week == day_index]

    form = AvailabilityForm()
    form.artist_id.data = artist_id

    return render_template('pages/artist_availability.html', artist=artist,
                           availability_by_day=availability_by_day, form=form)


@app.route('/artists/<int:artist_id>/availability/create', methods=['POST'])
def create_artist_availability(artist_id):
    """
    Creates a new availability entry for an artist.

    Args:
        artist_id (int): The ID of the artist.

    Returns:
        redirect: Redirects to the artist's availability page after successful creation.
    """
    form = AvailabilityForm(request.form)

    # Validate the form
    if form.validate_on_submit():
        try:
            # Parse time strings to time objects
            start_parts = form.start_time.data.split(':')
            end_parts = form.end_time.data.split(':')

            start_time = time(int(start_parts[0]), int(start_parts[1]))
            end_time = time(int(end_parts[0]), int(end_parts[1]))

            # Check if start is before end
            if start_time >= end_time:
                flash('Start time must be before end time.')
                return redirect(url_for('artist_availability', artist_id=artist_id))

            # Create new availability
            availability = Availability(
                artist_id=artist_id,
                day_of_week=int(form.day_of_week.data),
                start_time=start_time,
                end_time=end_time
            )

            db.session.add(availability)
            db.session.commit()
            flash('Availability added successfully.')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}')
    else:
        flash('Please correct the errors in the form.')

    return redirect(url_for('artist_availability', artist_id=artist_id))


@app.route('/artists/<int:artist_id>/availability/<int:availability_id>/delete', methods=['POST'])
def delete_artist_availability(artist_id, availability_id):
    """
    Deletes an availability entry for an artist.

    Args:
        artist_id (int): The ID of the artist.
        availability_id (int): The ID of the availability entry to be deleted.

    Returns:
        redirect: Redirects to the artist's availability page after successful deletion.

    Raises:
        ValueError: If the availability doesn't belong to the specified artist.
    """
    availability = Availability.query.get_or_404(availability_id)

    # Verify availability belongs to the specified artist
    if availability.artist_id != artist_id:
        flash('Invalid operation.')
        return redirect(url_for('artist_availability', artist_id=artist_id))

    try:
        db.session.delete(availability)
        db.session.commit()
        flash('Availability removed successfully.')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}')

    return redirect(url_for('artist_availability', artist_id=artist_id))


@app.errorhandler(404)
def not_found_error():
    """
    Error handler for 404 Not Found errors.

    Args:
        error: The error object passed by Flask.

    Returns:
        tuple: A tuple containing the rendered 404 error page and the 404 status code.
    """
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error():
    """
    Error handler for 500 Internal Server Error.

    Args:
        error: The error object passed by Flask.

    Returns:
        tuple: A tuple containing the rendered 500 error page and the 500 status code.
    """
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()
