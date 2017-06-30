import os
import re
import json
import urllib2
from datetime import date, datetime

class Movie:
    """
    A class that essentially takes a file name of a movie and does it's best to return 
    some IMDB and Rotten Tomato information about that movie. It has functions to clean 
    the file name and do some searching based on that.
    """

    def __init__(self, filename, MOVIES_DIR, CACHED_DAYS, CACHE_FILE, DATE_FILE, API_KEY, imdb_cache, date_cache):
        self.status = None
        self.message = None
        # Set the class variables and constants using the init arguments.
        self.filename = filename
        self.MOVIES_DIR = MOVIES_DIR
        self.CACHED_DAYS = CACHED_DAYS
        self.CACHE_FILE = CACHE_FILE
        self.API_KEY = API_KEY
        self.DATE_FILE = DATE_FILE
        self.imdb_cache = imdb_cache
        self.date_cache = date_cache
        # Set some class variables based on the file name and then test if successful.
        self.prepare_name()
        # Attempt to load data from cache or internet.
        if self.is_valid_name:
            self.load_data()
            if self.data:
                self.add_imdb_cache()
                self.add_date_cache()

    def load_data(self):
        '''
            Based on the status of the imdb_id, attempts to find data on the movie
            either from the stored cache, by id or by searching with title and year.
            Adds some blank data if the {no_imdb} tag appears in the file name.
            Returns: Nothing
        '''
        self.data = None
        if self.no_imdb == False:
            if self.imdb_id:
                self.data_by_id()
            else:
                self.data_by_search()
        else:
            self.data = {
                'Title' : self.name,
                'Year' : self.year,
                'Runtime' : '',
                'imdbRating' : '',
                'tomatoRating' : '',
                'Genre' : 'N/A',
                'imdbID' : '',
                'Plot' : '',
                'Poster' : 'N/A'
            }
            self.message = 'NO IMDB: %s' % self.filename
            self.status =(5, self.message)
            
    def add_imdb_cache(self):
        """
            Adds (or updates) an item in the imdb_cache file if a new item has been 
            added or the item in the cache is older than the value set in CACHED_DAYS.
            Returns: Nothing
        """        
        if self.status[0] in [3,4]:
            with open(self.CACHE_FILE, 'r+') as f:
                self.data['cached_date'] = date.today().strftime('%d/%m/%y')
                self.imdb_cache[self.data['imdbID']] = self.data
                f.seek(0)
                json.dump(self.imdb_cache, f, indent=4)

    def add_date_cache(self):
        """
            Tests if a date exists for this file name in the cache, if not it adds todays
            date to the cache.
            Returns: Nothing
        """
        if self.filename in self.date_cache:
            self.date = self.date_cache[self.filename]
        else:
            with open(self.DATE_FILE, 'r+') as f:
                self.date = date.today().strftime('%d/%m/%y')
                #self.date = datetime.fromtimestamp(os.path.getmtime(os.path.join(self.MOVIES_DIR,self.filename))).strftime('%d/%m/%y')
                self.date_cache[self.filename] = self.date
                f.seek(0)
                json.dump(self.date_cache, f, indent=4)        
                
    def pretty_filename(self):
        """
            Builds a standardised file name from the class properties.
            Returns: String
        """
        filename = u'%s (%s)' % (self.name, self.year)
        if self.imdb_id:
            filename += ' {%s}' % self.imdb_id
        filename += self.ext
        return filename

    def clean_filename(self, path):
        """
            Replaces the current file name with the standardised version. Can
            have trouble if the movie has been added twice, so returns a bool 
            to flag this.
            Returns: Bool
        """
        new_path = os.path.join(path, self.pretty_filename())
        old_path = os.path.join(path, self.filename)
        try:
            os.rename(old_path, new_path)
            return True
        except:
            return False

    def data_by_id(self):
        """
            If the imdb_id is known (from the file name), it will test the cache to see if this data
            has already been downloaded. If not it will download it and set the data property.
            Returns: Nothing
        """
        try:
            self.status = (4, 'NEW: From API (by ID) - %s' % self.filename )
            # Test if item exists in cache.
            if self.imdb_id in self.imdb_cache:
                self.data = self.imdb_cache[self.imdb_id]
                self.status = (2, 'EXISTING: From CACHE - %s' % self.filename )
                # Test for cache being older than CACHED_DAYS.
                cached_date = datetime.strptime( self.data['cached_date'], "%d/%m/%y").date()
                if (date.today() - cached_date).days > self.CACHED_DAYS:
                    self.status = (3, 'EXISTING: From CACHE (updated) - %s' % self.filename)
            # Get new data if not in cache or older than CACHED_DAYS.
            if self.status[0] in [3,4]:
                url = 'http://www.omdbapi.com/?apikey=%s&i=%s&plot=full&r=json&tomatoes=true' % (self.API_KEY, self.imdb_id)
                self.data = json.load(urllib2.urlopen(url, timeout=30))
        except:
            self.data = None
            self.message = 'ERROR: Could not read online data - %s' % self.filename
            self.status = (0, self.message)
            
    def data_by_search(self):
        """
            If the imdb_id is unknown (new files generally) this will attempt to find the data and the 
            imdb_id by using the search api. Sets the data if successful.
            Returns: Nothing
        """
        try:
            urls = self.build_search_urls()
            for url in urls:
                data = json.load(urllib2.urlopen(url[1], timeout=60))
                if data['Response'] == 'True':
                    self.data = data
                    self.imdb_id = self.data['imdbID']
                    if self.clean_filename(self.MOVIES_DIR):
                        self.message = 'NEW: From API (by SEARCH) %s (%s)= %s (%s) - %s' % (self.name,
                                self.year,
                                self.data['Title'],
                                self.data['Year'],
                                self.data['imdbID']
                            )
                        self.status = (1, self.message)    
                        break
                    else:
                        self.message = 'ERROR: Duplicate File - %s' % self.filename
                        self.data = None
                        self.status = (0, self.message)
                        break
        except:
            self.data = None
            self.message = 'ERROR: Could not read online data - %s' % self.filename
            self.status = (0, self.message)

    def build_search_urls(self):
        """
            Constructs a few search urls from the file name and year.
            Returns: List of Strings
        """
        urls = []
        year_str = 'y=%s' % self.year
        title_str = 't=%s' % self.name.replace(' ', '+')
        api_str = 'apikey=%s' % self.API_KEY
        urls.append((1, 'http://www.omdbapi.com/?%s&%s&%s&plot=full&r=json&tomatoes=true' % (api_str, title_str, year_str)))
        urls.append((2, 'http://www.omdbapi.com/?%s&%s&plot=full&r=json&tomatoes=true' % (api_str, title_str)))
        if '-' in self.name:
            names = self.name.split('-')
            title = self.name.replace(names[0] + '-', '').strip()
            title_str = 't=%s' % title.replace(' ', '+')
            urls.append((3, 'http://www.omdbapi.com/?%s&%s&%s&plot=full&r=json&tomatoes=true' % (api_str, title_str, year_str)))
            urls.append((4, 'http://www.omdbapi.com/?%s&%s&plot=full&r=json&tomatoes=true' % (api_str, title_str)))
        return urls

    def short_plot(self):
        """
            Currently used in the template to display a teaser of the plot.
            Returns: String
        """
        return self.data['Plot'][:300]
    
    def prepare_name(self):
        '''
            Runs a group of functions to extract details from the file name.
            Returns: Nothing
        '''
        self.set_ext()
        self.test_dotted()
        self.set_year()
        self.set_name()
        self.set_imdb_id()
        self.valid()
        
    def valid(self):
        """
            Tests if the init was able to produce a valid name and year from the file name.
            Returns: True or False
        """
        self.is_valid_name = False
        self.status = (0 , self.message)
        if self.year and self.name and self.ext:
            self.is_valid_name = True
            self.message = None
        
    def set_name(self):
        """
            Strips the movie name and cleans it. Has conditional to test if a dotted file
            name is being used.
            Returns: Nothing
        """
        self.name = None
        if self.year:
            self.message = 'ERROR: Unable to set name - %s' % self.filename
            if self.dotted == False:
                m = re.split('\\(%s\\)' % self.year, self.filename)
                if len(m) == 2:
                    self.name = m[0].strip()
            else:
                m = re.split('\\.%s\\.' % self.year, self.filename)
                if len(m) == 2:
                    self.name = m[0].strip().replace('.', ' ')

    def set_ext(self):
        """
            Splits the extension from the file name. Used to rebuild a standard/clean 
            file name.
            Returns: Nothing
        """
        self.ext = os.path.splitext(self.filename)[1]
        if self.ext not in ('.avi', '.mp4', '.mkv', '.divx','.mpg','.flv', '.m4v'):
            self.ext = None
            self.message = 'ERROR: Invalid file type - %s' % self.filename

    def test_dotted(self):
        """
            Determines if the filename uses the common protocol of splitting words in 
            the title and the year, with dots rather than spaces.
        """
        if self.filename.count('.') > 3 and len(re.findall('\\(\\d{4}\\)', self.filename)) == 0:
            self.dotted = True
        else:
            self.dotted = False

    def set_year(self):
        """
            Trys to find a year in the given file name. If it finds one surrounded by dots
            it sets the dotted property of the class.
            Returns: Nothing
        """
        self.year = None
        if self.ext:
            self.message = 'ERROR: No year found - %s' % self.filename
            if self.dotted == True:
                re_string = '\\.\\d{4}\\.'
            else:
                re_string = '\\(\\d{4}\\)'
            m = re.findall(re_string, self.filename)
            if len(m) > 0:
                for item in m:
                    year = int(re.search('\\d{4}', item).group())
                    if year != 1080 and year >= 1900 and year <= date.today().year:
                        self.year = year

    def set_imdb_id(self):
        """
            Strips the IMDB id out of the file name and sets the imdb_id class property.
            Returns: Nothing
        """
        self.no_imdb = False
        self.imdb_id = None
        if '{no_imdb}' in self.filename:
            self.no_imdb = True
            return
        m = re.findall('\\{tt\\d{7}\\}', self.filename)
        if len(m) > 0:
            self.imdb_id = re.search('tt\\d+', m[-1]).group()        

    def __str__(self):
        return u'%s - %s' % (self.name, self.year)