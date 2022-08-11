#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from crypt import methods
from enum import unique
import json
from unicodedata import name
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from config import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)


app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
  __tablename__ ='show'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer,db.ForeignKey('artist.id'), nullable=False)
  venue_id = db.Column(db.Integer,db.ForeignKey('venue.id'), nullable=False)
  start_date = db.Column(db.DateTime(), nullable=False, unique=True)

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talents = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', cascade='all, delete-orphan', backref='venue', lazy=True)

    
class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_venue_description = db.Column(db.String(500))
    shows = db.relationship('Show', cascade='all, delete-orphan', backref='artist', lazy=True)


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

@app.route('/venues', methods=['GET'])
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  # Algorithm to get it done
  # 1. Get data from the database using SQLAlchemy's Model.query.all()
  # 2. Group data as a list of dictionaries 
  # 3. Use dictionary comprehension to iterate over the keys and convert to {city: value, state: values, venues: [item1, item2 ...]}
  # 4 Feed data to the frontend

  # Step 1
  rows = Venue.query.all()

  #Step 2
  venues_dict = {}
  for row in rows:
    city_state = (row.city, row.state)
    if city_state not in venues_dict.keys():
      venues_dict[city_state] = []
    venues_dict[city_state].append(dict(
      id = row.id,
      name = row.name, 
      upcoming_shows = Show.query.filter(Show.venue_id == row.id, Show.start_date > datetime.today()).count()
    ))

  # Step 3
  data = [ dict(city=k[0], state=k[1], venues=v) for k, v in venues_dict.items() ]
  # Step 4
  return render_template('pages/venues.html', areas = data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # search for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  # Solution Roadmap

  # 1 Get required fields using filter and the ilike('%ed%') matching scheme
  # 2 Count the result set with Model.query.count() 
  # 3 Format and feed to response for frontend

  # Step 1
  search_term=request.form.get('search_term','')
  result_set = Venue.query.filter(Venue.name.ilike('%'+ search_term +'%'))

  # Step 2
  count = result_set.count()

  # step 3
  data =  []
  for venue in result_set.all():
    dic = dict(
      id = venue.id,
      name = venue.name,
      num_of_upcoming_shows = Show.query.filter_by(id=venue.id).count()  
    )
    data.append(dic)
  
  response={
    "count": count,
    "data": data
  }

  return render_template('pages/search_venues.html', results=response)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  ### Code 

  venue = Venue.query.filter_by(id = venue_id).first()
  shows = Show.query.filter(Show.venue_id==venue_id)

  past_shows = [{"artist_id": show.artist.id,
                  "artist_name": show.artist.name,
                  "artist_image_link": show.artist.image_link,
                  "start_time": show.start_date.strftime("%m/%d/%Y, %H:%M:%S")
                  } for show in shows.all() if show.start_date < datetime.today() ]          
  upcoming_shows = [{"artist_id": show.artist.id,
                  "artist_name": show.artist.name,
                  "artist_image_link": show.artist.image_link,
                  "start_time": show.start_date.strftime("%m/%d/%Y, %H:%M:%S")
                  } for show in shows.all() if show.start_date > datetime.today()  ]

  past_shows_count = len(past_shows)
  upcoming_shows_count = len(upcoming_shows)

  data = {
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres.strip('}').strip('{').split(','),
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talents,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": past_shows_count,
      "upcoming_shows_count": upcoming_shows_count,
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  form = VenueForm(request.form)
  venue = Venue(
    name = form.name.data,
    genres = form.genres.data,
    address = form.address.data,
    city = form.city.data,
    state = form.state.data,
    phone = form.phone.data,
    website = form.website_link.data,
    facebook_link = form.facebook_link.data,
    seeking_talents = form.seeking_talent.data,
    seeking_description = form.seeking_description.data,
    image_link = form.image_link.data
  )
  try:
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
    return redirect(url_for('venues'))

@app.route('/venues/delete/<int:venue_id>')
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get_or_404(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash("Venue was successfully deleted!")
    return redirect(url_for('venues'))
  except:
    flash("There was an error deleting venue")
    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()

  data=[ {
    "id": artist.id,
    "name": artist.name,
  } for artist in artists ]

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term=request.form.get('search_term', '')
  search_result = Artist.query.filter(Artist.name.ilike('%' + search_term + '%'))
  count = search_result.count()
  data = [ {
    "id": artist.id,
    "name": artist.name,
    "num_upcoming_shows": len(artist.shows)
    } for artist in search_result.all() ]

  response={
    "count": count,
    "data": data
  }
  return render_template('pages/search_artists.html', results=response)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  artist = Artist.query.get(artist_id)
  shows = Show.query.filter(Show.artist_id==artist_id)

  past_shows = [{"venue_id": show.venue.id,
                  "venue_name": show.venue.name,
                  "venue_image_link": show.venue.image_link,
                  "start_time": show.start_date.strftime("%m/%d/%Y, %H:%M:%S")
                  } for show in shows.all() if show.start_date < datetime.today() ]          
  upcoming_shows = [{"venue_id": show.venue.id,
                  "venue_name": show.venue.name,
                  "venue_image_link": show.venue.image_link,
                  "start_time": show.start_date.strftime("%m/%d/%Y, %H:%M:%S")
                  } for show in shows.all() if show.start_date > datetime.today()  ]

  past_shows_count = len(past_shows)
  upcoming_shows_count = len(upcoming_shows)

  data = {
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres.strip('}').strip('{').split(','),
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_venue_description,
      "image_link": artist.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": past_shows_count,
      "upcoming_shows_count": upcoming_shows_count,
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm(request.form)
  artist = Artist.query.get(artist_id)
  
  form.name.data = artist.name
  form.genres.data = artist.genres
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.website_link.data = artist.website
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_venue_description
  form.image_link.data = artist.image_link

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
 
  form_data = ArtistForm(request.form)
  artist = Artist.query.get(artist_id)
  artist.name = form_data.name.data
  artist.genres = form_data.genres.data
  artist.city = form_data.city.data
  artist.state = form_data.state.data
  artist.phone = form_data.phone.data
  artist.website = form_data.website_link.data
  artist.facebook_link = form_data.facebook_link.data
  artist.image_link = form_data.image_link.data
  artist.seeking_venue = form_data.seeking_venue.data
  artist.seeking_venue_description = form_data.seeking_description.data
  db.session.commit()
  return redirect(url_for('show_artist', artist_id= artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  
  venue = Venue.query.get(venue_id)

  form = VenueForm(request.form)
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.genres.data = venue.genres
  form.address.data = venue.address
  form.website_link.data = venue.website
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link
  form.seeking_talent.data = venue.seeking_talents
  form.seeking_description.data = venue.seeking_description

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  form = VenueForm(request.form)

  venue = Venue.query.get(venue_id)

  venue.name = form.name.data
  venue.genres = form.genres.data
  venue.city = form.city.data
  venue.state = form.state.data
  venue.address = form.address.data
  venue.phone = form.phone.data
  venue.website = form.website_link.data
  venue.facebook_link = form.facebook_link.data
  venue.seeking_talents = form.seeking_talent.data
  venue.seeking_description = form.seeking_description.data
  venue.image_link = form.image_link.data
  db.session.commit()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm(request.form)
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
 
  form  = ArtistForm(request.form)
  artist = Artist(
      name = form.name.data,
      genres = form.genres.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      website = form.website_link.data,
      facebook_link = form.facebook_link.data,
      image_link = form.image_link.data,
      seeking_venue = form.seeking_venue.data,
      seeking_venue_description = form.seeking_description.data
    )
  try:
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return redirect(url_for('artists'))
  except:
    flash(' Error occured while trying to create artist ' + request.form['name']+ '!!')
    return render_template('pages/home.html')
  finally:
    db.session.close()


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
 
  shows = Show.query.all()
  
  data = [ {
    "venue_id": show.venue.id,
    "venue_name": show.venue.name,
    "artist_id": show.artist.id,
    "artist_name": show.artist.name,
    "artist_image_link": show.artist.image_link,
    "start_time": show.start_date.strftime("%m/%d/%Y, %H:%M:%S")
  } for show in shows ]

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
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
