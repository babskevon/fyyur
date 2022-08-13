#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from sqlalchemy import func,cast, DATETIME
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app,db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    shows = db.relationship('Show',backref='showed', lazy='joined')

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    seeking_venues = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    shows = db.relationship('Show',backref='show', lazy='joined')

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  venue = db.Column(db.Integer,db.ForeignKey('Venue.id'), nullable=False)
  artist = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  datetime = db.Column(db.DateTime)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(str(value))
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
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  cities = Venue.query.with_entities(Venue.city, Venue.state).distinct()
  data = Venue.query.all()
  return render_template('pages/venues.html',
      data=data,
      cities=cities
  )

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term=request.form.get('search_term', '')
  data = Venue.query.filter(Venue.name.like("%{}%".format(search_term))).all()
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  today = datetime.datetime.now()
  venue = Venue.query.get(venue_id)
  artists = Artist.query.filter(Artist.shows.any(venue=venue_id))
  #.filter(Artist.shows.any(func.DATETIME(datetime)==today))#func.DATETIME(datetime)

  past_shows = []
  upcoming_shows = []

  for artist in artists:
    for show in artist.shows:
      if(show.datetime < today and show.artist == artist.id and show.venue==venue_id):
        data = {
          "artist_id": show.artist,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": str(show.datetime)
        }
        past_shows.append(data)
      if(show.datetime > today and show.artist == artist.id and show.venue==venue_id):
        data = {
          "artist_id": show.artist,
          "artist_name": artist.name,
          "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
          "start_time": str(show.datetime)
        }
        upcoming_shows.append(data)
  shows = {
    "past_shows":past_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
    "upcoming_shows":upcoming_shows,
    "genres":venue.genres.split(',')
  }
  return render_template('pages/show_venue.html', venue=venue, shows=shows)

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
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  address = request.form['address']
  phone = request.form['phone']
  image_link = request.form['image_link']
  genres = request.form.getlist('genres')
  genres = ' '.join(genres).replace(" ", ",")
  facebook_link = request.form['facebook_link']
  website_link = request.form['website_link']
  seeking_talent = request.form['seeking_talent']
  seeking_description = request.form['seeking_description']
  

  try:
    venue = Venue(
      name=name,
      city=city,
      state=state,
      address=address,
      phone=phone,
      image_link=image_link,
      genres=genres,
      facebook_link=facebook_link,
      website_link=website_link,
      seeking_talent=True if seeking_talent=='y' else False,
      seeking_description=seeking_description
    )
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + data.name + ' could not be listed.')
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
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.order_by('id').all()
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  data = Artist.query.filter(Artist.name.like("%{}%".format(search_term))).all()
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  venues = Venue.query.all()
  today = datetime.datetime.now()
  past_shows = []
  upcoming_shows = []
  for venue in venues:
    for show in artist.shows:
      if(show.datetime < today and show.venue==venue.id):
        data = {
          "venue_id": show.venue,
          "venue_name": venue.name,
          "venue_image_link": venue.image_link,
          "start_time": show.datetime
        }
        past_shows.append(data)
      if(show.datetime >= today and show.venue==venue.id):
        data = {
          "venue_id": show.venue,
          "venue_name": venue.name,
          "venue_image_link": venue.image_link,
          "start_time": show.datetime
        }
        upcoming_shows.append(data)
  shows = {
    "past_shows":past_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
    "upcoming_shows":upcoming_shows,
    "genres":artist.genres.split()
  }
  return render_template('pages/show_artist.html', artist=artist,shows=shows)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist=Artist.query.get(artist_id)
  form = ArtistForm(
    name=artist.name,
    city=artist.city,
    state=artist.state,
    phone=artist.phone,
    genres=artist.genres.split(','),
    facebook_link=artist.facebook_link,
    image_link=artist.image_link,
    seeking_venue=artist.seeking_venues,
    seeking_description=artist.seeking_description,
    website_link=artist.website_link
  )
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  # genres = request.form['genres']
  genres = request.form.getlist('genres')
  genres = ' '.join(genres).replace(" ", ",")
  website_link = request.form['website_link']
  facebook_link = request.form['facebook_link']
  seeking_venue = request.form['seeking_venue']
  seeking_description = request.form['seeking_description']
  try:
    artist = Artist.query.get(artist_id)
    artist.name = name
    artist.city = city
    artist.state = state
    artist.phone = phone
    artist.genres = genres
    artist.website_link = website_link
    artist.seeking_venues = True if seeking_venue=='y' else False
    artist.seeking_description = seeking_description
    artist.facebook_link = facebook_link
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  form = VenueForm(
    name=venue.name,
    city=venue.city,
    state=venue.state,
    address=venue.address,
    phone=venue.phone,
    genres=venue.genres.split(','),
    facebook_link=venue.facebook_link,
    website_link=venue.website_link,
    image_link=venue.image_link,
    seeking_talent=venue.seeking_talent,
    seeking_description=venue.seeking_description
  )
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  address = request.form['address']
  phone = request.form['phone']
  image_link = request.form['image_link']
  genres = request.form.getlist('genres')
  genres = ' '.join(genres).replace(" ", ",")
  facebook_link = request.form['facebook_link']
  website_link = request.form['website_link']
  seeking_talent = request.form['seeking_talent']
  seeking_description = request.form['seeking_description']
  try:
    venue = Venue.query.get(venue_id)
    venue.name = name
    venue.city = city
    venue.state=state
    venue.address = address
    venue.phone = phone
    venue.image_link = image_link
    venue.genres = genres
    venue.facebook_link = facebook_link
    venue.website_link = website_link
    venue.seeking_talent = True if seeking_talent=='y' else False
    venue.seeking_description = seeking_description
    db.session.commit()
  except:
    db.session.rollback()
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
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  # genres = request.form['genres']
  genres = request.form.getlist('genres')
  genres = ' '.join(genres).replace(" ", ",")
  website_link = request.form['website_link']
  facebook_link = request.form['facebook_link']
  seeking_venue = request.form['seeking_venue']
  seeking_description = request.form['seeking_description']
  
  try:
    artist = Artist(
      name=name,
      city=city,
      state=state,
      phone=phone,
      genres=genres,
      website_link=website_link,
      facebook_link=facebook_link,
      seeking_venues=True if seeking_venue=='y' else False,
      seeking_description=seeking_description
    )
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    # on failed db insert, flash success
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  venues = Venue.query.all()
  artists = Artist.query.all()
  return render_template('pages/shows.html', artists=artists, venues=venues)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  artist_id = request.form['artist_id']
  venue_id = request.form['venue_id']
  start_time = request.form['start_time']
  try:
    show = Show(
      venue=venue_id,
      artist=artist_id,
      datetime=start_time
    )
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')

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
