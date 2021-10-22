#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

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
from datetime import date
from sqlalchemy.exc import SQLAlchemyError

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:4928wuzi@localhost:5432/fyyur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
    #genre = db.Column(db.String(500))
    genres = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(1000))
    shows = db.relationship('Show', backref='venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String(1000))
    shows = db.relationship('Show', backref='artist', lazy=True)

class Show(db.Model): 
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime(), nullable=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  ven = Venue.query.all()
  return render_template('pages/venues.html', areas=ven, venue=ven);


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  result = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))
  print ('And the result is . . .')
  print(result)
  response={
    "count": result.count(),
    "data": result
  }
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venu = Venue.query.get(venue_id)
  #data = list(filter(lambda d: d['id'] == venue_id, venu))[0]
  return render_template('pages/show_venue.html', venue=venu)

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

    #form = VenueForm(request.form, meta={'csrf': False})
    form = VenueForm(request.form)
    #if form.validate():
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
            website_link=form.website_link.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data,
        )
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + form.name.data + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue '+ request.form['name'] + ' could not be listed')
    finally:
        db.session.close()
    return render_template('pages/home.html')

  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  #return render_template('pages/home.html')

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
  art = Artist.query.all()
  return render_template('pages/artists.html', artists=art)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  result = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))
  print ('And the result is . . .')
  print(result)
  response={
    "count": result.count(),
    "data": result
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  dat = Artist.query.get(artist_id)
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=dat)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  artist_inf={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist_inf)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    form = ArtistForm(request.form)
    artist = Artist.query.get(artist_id)

    artist.name = form.name.data
    artist.phone = form.phone.data
    artist.state = form.state.data
    artist.city = form.city.data
    artist.genres = form.genres.data
    artist.image_link = form.image_link.data
    artist.facebook_link = form.facebook_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    
    db.session.commit()
    flash('The Artist ' + request.form['name'] + ' has been successfully updated!')
  except:
    db.session.rollback()
    flash('An Error has occured, Update is not applied')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  venue={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website_link": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    form = VenueForm(request.form)
    venue = Venue.query.get(venue_id)

    venue.name = form.name.data
    venue.genres = form.genres.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.facebook_link = form.facebook_link.data
    venue.website_link = form.website_link.data
    venue.image_link = form.image_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data

    db.session.commit()
    #Succesice update
    flash('Venue ' + request.form['name'] + 'has been updated')
  except:
    #Failure of updating
    db.session.rollback()
    flash('An error occured while trying to update Venue')
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

    #form = VenueForm(request.form, meta={'csrf': False})
    form = ArtistForm(request.form)
    #if form.validate():
    try:
        artist = Artist(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            #address=form.address.data,
            phone=form.phone.data,
            genres=form.genres.data,
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
            website=form.website_link.data,
            seeking_venue=form.seeking_venue.data,
            seeking_description=form.seeking_description.data,
        )
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + form.name.data + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Artist '+ request.form['name'] + ' could not be listed')
    finally:
        db.session.close()
    return render_template('pages/home.html')

  # on successful db insert, flash success
#  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
#  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  now= datetime.utcnow()
  show = db.session.query(
    Show.venue_id,
    Show.id.label("show_id"),
    #Show.id,
    Show.start_time.label("start_time"),
    Venue.name.label("venue_name"),
    Artist.id.label("artist_id"),
    Artist.name.label("artist_name"),
    Artist.image_link
  ).join(
    Venue
  ).join(
    Artist
  ).filter(
    Show.start_time>now
  ).order_by(
    'start_time'
  ).all()

  past_show = db.session.query(
    Show.venue_id,
    Show.id.label("show_id"),
    #Show.id,
    Show.start_time.label("start_time"),
    Venue.name.label("venue_name"),
    Artist.id.label("artist_id"),
    Artist.name.label("artist_name"),
    Artist.image_link
  ).join(
    Venue
  ).join(
    Artist
  ).filter(
    Show.start_time<now
  ).order_by(
    'start_time'
  ).all()
  return render_template('pages/shows.html', shows=show, past=past_show)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  try:
    show = Show(
       artist_id = form['artist_id'].data,
       venue_id = form['venue_id'].data,
       start_time= form['start_time'].data
    )
    db.session.add(show)
    db.session.commit()
  # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occured. show could not be listed')
  finally:
    db.session.close()

  return render_template('pages/home.html')
  # on successful db insert, flash success
 # flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
 # return render_template('pages/home.html')

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
