# MovieDB

NB: This tool works, but requires some manual steps, and has no tests. A complete rework is under way at [movie-db2](https://github.com/tmcadam/movie-db2)

A Python2 script that reads the contents of a folder containing movies, searches IMDB & Rotten Tomatoes for info on that movie, then creates a searchable/sortable single webpage using the [Datatables](https://datatables.net/
) jQuery plugin. Makes your movie collection super easy to search.

The generated page can be set to run locally on your machine or you can sync it to a server somewhere to share it. The script currently finishes with an SCP command to push the finished page to simple web server.

## Installation
  * Clone the repo
      ```
      git clone https://github.com/tmcadam/movie-db.git
      ```
  * Change directory to the repo

  * Run the build script
      ```
      bash build.sh
      ```
  * Create 3 settings files (no file extension) in the same directory as file ```moviedb.py```
    * ```MOVIE_DIR``` - Contains the directory of movies to catalogue
    * ```API_KEY``` - Get an API key from http://www.omdbapi.com/ and put it here
    * ```REMOTE_LOCATION``` - A path for the SCP command to use to upload the HTML file

## Usage
  * Change directory to the repo
  * Make sure the 3 settings files are configured (see Installation)
  * ```python moviedb.py```
