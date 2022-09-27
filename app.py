#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email.policy import strict
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
import sys
from datetime import datetime, date

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

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
    
    genres = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    looking_for_talent = db.Column(db.String)
    seeking_description = db.Column(db.String(500))

    shows = db.relationship('Show', backref='venue', lazy=True, cascade = 'all, delete-orphan')

    def __repr__(self):
      return f'<Venue {self.id} {self.name} {self.city} {self.state}>'


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

    website_link = db.Column(db.String(120))
    looking_for_venues = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500))

    shows = db.relationship('Show', backref='artist', lazy=True, cascade = 'all, delete-orphan')

    def __repr__(self):
      return f'<Artist {self.id} {self.name} {self.city} {self.state}>'


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
      return f'<Show {self.id} {self.artist_id} {self.venue_id} {self.start_time}>'
    

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
  
  data=[]

  venues = db.session.query(Venue)

  for venue in venues:
      
    show_venue = db.session.query(Venue.id, Venue.name).filter(Venue.city == venue.city and Venue.state == venue.state)
      
    data.append({
      "city": venue.city,
      "state": venue.state,
      "venues": show_venue
    })
    
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  
  response=[]
  data=[]
  
  search_term=request.form.get('search_term', '')
  
  venues = db.session.query(Venue).filter(Venue.name.ilike('%' + search_term + '%')).all()
 

  for venue in venues:
    data.append ({
      "id": venue.id,
      "name": venue.name,
      "state": venue.state,
      "city": venue.city,
    })
  
  response = ({
    "count": len(venues),
    "data": data
  })

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  
  data=[]
  upcoming_shows=[]
  past_shows=[]
  
  current_time = datetime.now()

  venue = db.session.query(Venue).get(venue_id)
  shows = db.session.query(Show).filter(Show.venue_id == venue_id)

  for show in shows:
    artist = db.session.query(Artist).get(show.artist_id)

    artist_details = {
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.strftime("%Y/%m/%d %H:%M:%S")
    }

    if (show.start_time > current_time):
      upcoming_shows.append(artist_details)
    else:
      past_shows.append(artist_details)

  data = ({
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.looking_for_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.website_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  })
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  
  error = False

  try:
    new_venue = Venue(
      name = request.form.get('name'),
      city = request.form.get('city'),
      state = request.form.get('state'),
      address = request.form.get('address'),
      phone = request.form.get('phone'),
      image_link = request.form.get('image_link'),
      facebook_link = request.form.get('facebook_link'),
      genres = request.form.get('genres'),
      website_link = request.form.get('website_link'),
      looking_for_talent = request.form.get('looking_for_talent'),
      seeking_description = request.form.get('seeking_description')
    )

    db.session.add(new_venue)
    db.session.commit()
  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  
  
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    print(sys.exc_info())
  
  finally:
    db.session.close()
  
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['GET']) 
def delete_venue(venue_id):

  error = False

  try:
    #Note to self: recheck this
    venue = db.session.query(Venue).get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + ' ' + ' was successfully deleted!')
  
  except:
    error = True
    db.session.rollback()
    flash('Venue ' + venue['name'] + ' could not be deleted!')
  
  finally:
    db.session.close()

  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  
  data=[]

  artists = db.session.query(Artist.id, Artist.name).all()

  for artist in artists:
    data.append({
      "id": artist[0],
      "name": artist[1]
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  
  response=[]
  data=[]
  
  search_term=request.form.get('search_term', '')
  
  artists = db.session.query(Artist).filter(Artist.name.ilike('%' + search_term + '%')).all()

  for artist in artists:
    data.append ({
      "id": artist.id,
      "name": artist.name,
      "state": artist.state,
      "city": artist.city,
      #"num_upcoming_shows": num_upcoming_shows
    })
  
  response = ({
    "count": len(artists),
    "data": data
  })

  #response={
  #  "count": 1,
  #  "data": [{
  #    "id": 4,
  #    "name": "Guns N Petals",
  #    "num_upcoming_shows": 0,
  #  }]
  #}
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  
  data=[]
  upcoming_shows=[]
  past_shows=[]

  current_time = datetime.now()
  
  artist = db.session.query(Artist).get(artist_id)
  shows = db.session.query(Show).filter(Show.artist_id == artist_id)

  for show in shows:
    venue = db.session.query(Venue).get(show.venue_id)

    venue_details = {
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "venue_image_link": venue.image_link,
      "start_time": show.start_time.strftime("%Y/%m/%d %H:%M:%S")
    }  
    #Referenced link below for date formating
    #https://stackoverflow.com/questions/63269150/typeerror-parser-must-be-a-string-or-character-stream-not-datetime

    if (show.start_time > current_time):
      upcoming_shows.append(venue_details)
    else:
      past_shows.append(venue_details)

  data = ({
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.looking_for_venues,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  })
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  artist = db.session.query(Artist).get(artist_id)

  #
  #artist={
  #  "id": artist.id,
  #  "name": artist.name,
  #  "genres": artist.genres,
  #  "city": artist.city,
  #  "state": artist.state,
  #  "phone": artist.phone,
  #  "website": artist.website_link,
  #  "facebook_link": artist.facebook_link,
  #  "seeking_venue": artist.looking_for_venues,
  #  "seeking_description": artist.seeking_description,
  #  "image_link": artist.image_link
  #}
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  
  artist = db.session.query(Artist)

  error = False

  try:
    artist = db.session.query(Artist).get(artist_id)

    artist.name = request.form.get('name'),
    artist.city = request.form.get('city'),
    artist.state = request.form.get('state'),
    artist.phone = request.form.get('phone'),
    artist.genres = request.form.get('genres'),
    artist.image_link = request.form.get('image_link'),
    artist.facebook_link = request.form.get('facebook_link'),
    artist.website_link = request.form.get('website_link'),
    artist.looking_for_venues = request.form.get('looking_for_venues'),
    artist.seeking_description = request.form.get('seeking_description')

    db.session.add(artist)
    db.session.commit()
  # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  
  
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
    print(sys.exc_info())
  
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  venue = db.session.query(Venue).get(venue_id)

  #venue={
  #  "id": venue.id,
  #  "name": venue.name,
  #  "genres": venue.genres,
  #  "address": venue.address,
  #  "city": venue.city,
  #  "state": venue.state,
  #  "phone": venue.phone,
  #  "website": venue.website_link,
  #  "facebook_link": venue.facebook_link,
  #  "seeking_talent": venue.looking_for_talent,
  #  "seeking_description": venue.seeking_description,
  #  "image_link": venue.website_link
  #}

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  
  venue = db.session.query(Venue)

  error = False

  try:
    venue = db.session.query(Venue).get(venue_id)

    venue.name = request.form.get('name'),
    venue.city = request.form.get('city'),
    venue.state = request.form.get('state'),
    venue.address = request.form.get('address'),
    venue.phone = request.form.get('phone'),
    venue.image_link = request.form.get('image_link'),
    venue.facebook_link = request.form.get('facebook_link'),
    venue.genres = request.form.get('genres'),
    venue.website_link = request.form.get('website_link'),
    venue.looking_for_talent = request.form.get('looking_for_talent'),
    venue.seeking_description = request.form.get('seeking_description')

    db.session.add(venue)
    db.session.commit()
  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  
  
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
    print(sys.exc_info())
  
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

  error = False

  try:
    new_artist = Artist(
      name = request.form.get('name'),
      city = request.form.get('city'),
      state = request.form.get('state'),
      phone = request.form.get('phone'),
      genres = request.form.get('genres'),
      image_link = request.form.get('image_link'),
      facebook_link = request.form.get('facebook_link'),
      website_link = request.form.get('website_link'),
      looking_for_venues = request.form.get('looking_for_venues'),
      seeking_description = request.form.get('seeking_description')
    )

    db.session.add(new_artist)
    db.session.commit()
  # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    print(sys.exc_info())
  
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  
  data=[]
  
  shows = db.session.query(Show)

  for show in shows:
    data.append ({
    "venue_id": show.venue_id,
    "venue_name": show.venue.name,
    "artist_id": show.artist_id,
    "artist_name": show.artist.name,
    "artist_image_link": show.artist.image_link,
    "start_time": str(show.start_time)
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  
  error = False

  try:
    new_show = Show(
      artist_id = request.form.get('artist_id'),
      venue_id = request.form.get('venue_id'),
      start_time = request.form.get('start_time')
    )

    db.session.add(new_show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
    print(sys.exc_info())
  
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