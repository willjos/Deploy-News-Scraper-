from urllib.request import urlopen
from datetime import datetime   
from bs4 import BeautifulSoup
import psycopg2
import psycopg2.extras

def get_html(url): # retrieves all of the HTML data for a given URL
    page = urlopen(url)
    html_bytes = page.read()
    html = html_bytes.decode("utf_8")
    return html

def get_db_connection(): # connects to our stories database
  try:
    conn = psycopg2.connect("dbname=social_news user=postgres password=SnowshillTrumlet1% host=will-personal-news-scraper-db.cqy5c0k9kldd.eu-west-2.rds.amazonaws.com")
    return conn
  except:
    print("Error connecting to database.")

# import db function
# txt file for comments
# discuss subsets of application, less jumping around

conn = get_db_connection() # connection made to database by calling above function

def db_select(query, parameters=()): # this function executes a parameterised query
    if conn != None:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            try:
                cur.execute(query, parameters)
                conn.commit()
                return "Database updated", 200    
            except:
                return "Error executing query."
    else:
        return "No connection"

def db_fetch(query, parameters=()): #this function fetches data using a parameterised query.
    if conn != None:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            try:
                cur.execute(query, parameters)
                fetch = cur.fetchone()
                return fetch
            except:
                return "Error executing query."
    else:
        return "No connection"

def add_story_tag_metadata_to_database(story): # adds our BBC news stories to the stories database.
    query1 = """
    INSERT INTO stories (title, created_at, updated_at, url)
    VALUES (%s, current_timestamp, current_timestamp, %s);
    """
    params1 = (story['title'], story['url'])
    query2 = """
    INSERT INTO tags (description)
    VALUES (%s)
    ON CONFLICT DO NOTHING;
    """
    params2 = (story['description'],)
    query3 = """
    SELECT id FROM stories WHERE url = %s
    """
    params3 = (story['url'],)
    query4 = """
    SELECT id FROM tags WHERE description = %s
    """
    params4 = (story['description'],)
    query5 = """
    INSERT INTO metadata(story_id, tag_id)
    VALUES (%s, %s);
    """
    db_select(query1, params1)
    db_select(query2, params2)
    story_id = db_fetch(query3, params3)['id']
    tag_id = db_fetch(query4, params4)['id']
    db_select(query5, (story_id, tag_id))
    return 200

if __name__ == "__main__":
    bbc_url = "http://bbc.co.uk"
    bbc_html_doc = get_html(bbc_url)

def parse_stories_with_metadata(html):
    soup = BeautifulSoup(html, "html.parser")
    articles = soup.find_all(type='article')
    def find_title_url_metadata(article):
        metadata = article.find_all('span', class_ = 'ssrcss-1if1g9v-MetadataText')[0].get_text()
        a_tag = article.find_all('a')[0]
        a_tag_title = a_tag.find_all('span')[-1].string
        a_tag_url = "http://bbc.co.uk" + a_tag['href']
        return {'title': a_tag_title, 'url': a_tag_url, 'description': metadata} 
    useful_article_info = []
    for article in articles:
        useful_article_info.append(find_title_url_metadata(article))
    return useful_article_info

def add_info_to_database():
    info = parse_stories_with_metadata(get_html("http://bbc.co.uk"))
    for article in info:
        add_story_tag_metadata_to_database(article)
    return 200


add_info_to_database()
