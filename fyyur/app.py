#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
from tkinter import EXCEPTION
from wsgiref import validate
import dateutil.parser
import babel
import sys
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy.sql import func
from models import * 
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

#app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
#db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#





#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.

  distinct_venues = Venue.query.distinct(Venue.state, Venue.city).all()
  all_venues = Venue.query.all()

  data = []
  for distinct_venue in distinct_venues:
    venues_in_city = {
      "city": distinct_venue.city,
      "state": distinct_venue.state,
      "venues": []
    }

    for venue in all_venues:
      if (distinct_venue.city == venue.city and distinct_venue.state == venue.state):
        venues_in_city['venues'].append({
          "id": venue.id, 
          "name": venue.name,
          "state": venue.state, 
        })
    data.append(venues_in_city)

  if len(data) == 0:
    flash("Venues haven't been created yet")

  return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  input = request.form['search_term']
  search = '%{}%'.format(input)
  venue_search = Venue.query.filter(Venue.name.ilike(search)).all()
  

  response = {
    'count': len(venue_search),
    'data': []
  }

  for result in venue_search:
    response['data'].append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.now(), result.shows)))
    })
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

  

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  upcoming_shows = []
  past_shows = []
  current_time = datetime.now()
  for show in venue.shows:
    venue_detail = {
      "artist_id": show.artist_id,
      "artist_name": show.artists.name,
      "artist_image_link": show.artists.image_link,
      "start_time": show.start_time.isoformat()
    }

    if (show.start_time >= current_time):
      upcoming_shows.append(venue_detail)
    else:
      past_shows.append(venue_detail)
  data = vars(venue)
  data['upcoming_shows'] = upcoming_shows
  data['upcoming_shows_count'] = len(upcoming_shows)
  data['past_shows'] = past_shows
  data['past_shows_count'] = len(past_shows)

  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  form = VenueForm(request.form)
  print(form.data)
  # Validate Form
  if form.validate():
    name = form.name.data
    city = form.city.data
    state = form.state.data
    address = form.address.data
    phone = form.phone.data
    genres = form.genres.data
    facebook_link = form.facebook_link.data
    image_link = form.image_link.data
    website_link = form.website_link.data
    seeking_talent = form.seeking_talent.data
    seeking_description = form.seeking_description.data

    venue = Venue(name=name, city=city, state=state, address=address,
      phone=phone, genres=genres, facebook_link=facebook_link, 
      image_link=image_link, website_link=website_link, 
      seeking_talent=seeking_talent, seeking_description=seeking_description)
    
    try:
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except Exception as error:
      print(error)
      db.session.rollback()
      flash('An error occurred. ' + request.form['name'] + ' could not be listed!')
    finally:
      db.session.close()

  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()
  data = []
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name
    })

  return render_template('pages/artists.html', artists=data)



@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  input = request.form['search_term']
  search = '%{}%'.format(input)
  artist_search = Artist.query.filter(Artist.name.ilike(search)).all()
  

  response = {
    'count': len(artist_search),
    'data': []
  }

  for result in artist_search:
    response['data'].append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.now(), result.shows)))
    })
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  upcoming_shows = []
  past_shows = []
  current_time = datetime.now()
  for show in artist.shows:
    artist_detail = {
      "venue_id": show.venue_id,
      "venue_name": show.venues.name,
      "venue_image_link": show.venues.image_link,
      "start_time": show.start_time.isoformat()
    }

    if (show.start_time >= current_time):
      upcoming_shows.append(artist_detail)
    else:
      past_shows.append(artist_detail)
  data = vars(artist)
  data['upcoming_shows'] = upcoming_shows
  data['upcoming_shows_count'] = len(upcoming_shows)
  data['past_shows'] = past_shows
  data['past_shows_count'] = len(past_shows)
  return render_template('pages/show_artist.html', artist=artist)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
   # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)

  return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)
  
  artist_form = ArtistForm(request.form)
  if artist_form.validate():
    for key, val in artist_form.data.items():
      setattr(artist, key, val)

    try:
      db.session.commit()
      flash('Artist ' + artist_form.name.data + ' was successfully edited!')
    except:
      flash('Artist ' + request.form['name'] + ' was not successfully edited!')
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))



@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)

  return render_template('forms/edit_venue.html', form=form, venue=venue)



@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  
  venue = Venue.query.get(venue_id)
  
  venue_form = VenueForm(request.form)
  if venue_form.validate():
    print(venue_form.data)
    for key, val in venue_form.data.items():
      setattr(venue, key, val)

    try:
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully edited!')
    except:
      db.session.rollback()
      print(sys.exc_info())
      flash('Venue ' + request.form['name'] + ' was not successfully edited!')
    finally:
      db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  form = ArtistForm(request.form)
  print(form.data)
  if form.validate():
    name = form.name.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data
    facebook_link = form.facebook_link.data
    image_link = form.facebook_link.data
    website_link = form.website_link.data
    seeking_venue = form.seeking_venue.data
    seeking_description =form.seeking_description.data

    artist = Artist(name=name, city=city, state=state,
      phone=phone, facebook_link=facebook_link, 
      image_link=image_link, website_link=website_link, 
      seeking_venue=seeking_venue, seeking_description=seeking_description)

    try:
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' success!')
    except Exception as error:
      print(error)
      db.session.rollback()
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    finally:
      db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  all_shows = db.session.query(Show).outerjoin(Artist).outerjoin(Venue).all()
  print(all_shows)
  data = []
  for show in all_shows: 
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venues.name,
      "artist_id": show.artist_id,
      "artist_name": show.artists.name, 
      "artist_image_link": show.artists.image_link,
      "start_time": show.start_time.isoformat()
    })

  return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  form = ShowForm(request.form)
  print(form.data)
  if form.validate():
    artist_id = form.artist_id.data
    venue_id = form.venue_id.data
    start_time = form.start_time.data

    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)

    try:
      db.session.add(show)
      db.session.commit()
      flash('Show was successfully listed!')
    except:
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occured, show could not be listed, try again!')
    finally:
      db.session.close()

  return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
