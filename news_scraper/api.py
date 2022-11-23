import psycopg2
import psycopg2.extras  # We'll need this to convert SQL responses into dictionaries
from flask import Flask, current_app, jsonify, request
import json

app = Flask(__name__)

# if __name__ == '__main__':
#   app.run(debug=True, host='0.0.0.0', port=5000)
  
def get_db_connection(): # sets up a connection to my social_news database in postgres
  try:
    conn = psycopg2.connect("dbname=social_news user=postgres password=Snowshill1 host=news-scraper-db-will3.c1i5dspnearp.eu-west-2.rds.amazonaws.com")
    return conn
  except:
    print("Error connecting to database.")

conn = get_db_connection() # connection made to database

@app.route("/", methods=["GET"]) #retrieves the news site page
def index():
    return current_app.send_static_file("index.html")

@app.route("/stories", methods=["GET"]) #provides a list of the news stories sorted by score high to low.
def stories():
    try:  
      cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
      cur.execute("""SELECT id, title, url, created_at, updated_at, story_id, CASE 
      WHEN score IS NULL THEN 0
      WHEN score < 0 THEN 0
      ELSE score
      END score
      FROM stories LEFT JOIN stories_with_scores ON stories.id = stories_with_scores.story_id 
      ORDER BY score DESC;
      """)
      fetch = cur.fetchall()
      data = {'stories': fetch, 'success': True, 'total_stories': len(fetch)}
      if data['total_stories'] == 0:
        return 'No stories found', 404
      conn.commit()
      cur.close()
      return jsonify(data), 200
    except:
      return 'Server error or Unknown error fetching stories.', 500

def db_select(query, parameters):
    if conn != None:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            try:
                cur.execute(query, parameters)
                conn.commit()
                return 200
            except:
                return "Error executing query.", 500
    else:
        return "No connection"

def db_fetch(query, parameters=()): #this function fetches data using a parameterised query.
    if conn != None:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            try:
                cur.execute(query, parameters)
                fetch = cur.fetchall()
                return fetch
            except:
                return "Error executing query."
    else:
        return "No connection"

@app.route("/stories/<int:id>/votes", methods=['POST']) # casts a vote for a story.
def send_vote(id):
    try:
      if request.method == 'POST':
        data = json.loads(request.data)
        params = (data['direction'], id)
        query = """
        INSERT INTO votes(direction, created_at, updated_at, story_id)
        VALUES (%s, current_timestamp, current_timestamp, %s);
        """
        db_select(query, params)
        return ('Vote cast', 200,)
    except:
      return 'Server error', 500

@app.route("/search") # Query parameter search by tags or title
def get_stories_query(): #tags is a query param.
  search_result = '<h1> No stories found :( </h1>'
  try:
    tags = request.args.get('tags').split(',')
    title = request.args.get('title')
    title_for_query = f'%{title}%'
  except:
    return search_result
  query = """
  SELECT DISTINCT stories.title, stories.url, tags.description 
  FROM stories
  JOIN metadata ON stories.id = metadata.story_id 
  JOIN tags ON metadata.tag_id = tags.id
  WHERE tags.description = ANY(%s) OR stories.title LIKE %s;
  """ # query that returns the title, url, and tag, for any stories with their tag in the search, or their title containing a searched substring. 
  fetch = db_fetch(query, (tags, title_for_query))
  search_result = [[element['title'], element['url'], element['description']] for element in fetch]
  return search_result






