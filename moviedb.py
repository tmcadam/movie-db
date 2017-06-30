import os
import json
from jinja2 import Template
from movie import Movie

# Some constants which could/should be passed in as arguments
with open("MOVIE_DIR") as f:
    MOVIE_DIR = f.read()
TEMPLATE_FILE = 'template.html'
CACHE_FILE = 'cache/imdbCache.json'
DATE_FILE = 'cache/dateAdded.json'
HTML_OUT = 'output/index.html'
with open("API_KEY") as f:
    API_KEY = f.read()
CACHED_DAYS = 90

# Generate a list of file names in the specified folder.
files = os.listdir(MOVIE_DIR)

# Read the IMDB data cache. If it doesn't exist create a blank file and an empty dictionary to use.
try:
    with open(CACHE_FILE) as f: imdb_cache = json.load(f)
except: 
    with open(CACHE_FILE, 'w') as f: f.write('{}')
    imdb_cache = {}
    
# Read the Date Added cache. If it doesn't exist create a blank file and an empty dictionary to use.
try: 
    with open(DATE_FILE) as f: date_cache = json.load(f)
except: 
    with open(DATE_FILE, 'w') as f: f.write('{}')
    date_cache = {}

counter = {'main':0, 'from_cache':0, 'error':0, 'updated_cache':0, 'by_search':0, 'by_id':0, 'no_imdb':0}
movies = [] # this will be the list of movie object that gets sent to the template.
print '\nReading directory contents....\n'
for file in files:
    movie = Movie(file, MOVIE_DIR, CACHED_DAYS, CACHE_FILE, DATE_FILE, API_KEY, imdb_cache, date_cache)
    if movie.status[0] in [1,2,3,4,5]:
        movies.append( movie )
        counter['main'] += 1
        if movie.status[0] == 1:
            counter['by_search'] += 1
            print movie.status[1]
        elif movie.status[0] == 2:
            counter['from_cache'] += 1
        elif movie.status[0] == 3:
            counter['updated_cache'] += 1
        elif movie.status[0] == 4:
            counter['by_id'] += 1
        elif movie.status[0] == 5: 
            counter['no_imdb'] += 1
    else:
        print movie.status[1]
        counter['error'] += 1

print '\nTotal Files in Folder: %s' % len(files)
print '\n%s Errors' % counter['error'] 
print '%s Successfully Added' % counter['main']
print '----------------------------------------------------------'
print '%s From Cache' % counter['from_cache']
print '%s Updated Cache' % counter['updated_cache'] 
print '%s By Search' % counter['by_search']  
print '%s By ID' % counter['by_id']  
print '%s No IMDB' % counter['no_imdb']
        
with open( TEMPLATE_FILE ) as file_template:
    template = Template( file_template.read() )
    html = template.render( counter = counter['main'], movies = movies )
    with open(HTML_OUT, 'w') as file_out:
        file_out.write(html.encode('utf8'))
        print '\nHTML output successful'    
 