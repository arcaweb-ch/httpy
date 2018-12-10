# httpy
Simple python http server with python interpreter.

# Info

I made this as a simple web application development environment with Python interpreter and MySQL support. The first idea was to combine a python webserver and cefpython (https://github.com/cztomczak/cefpython) to be able to develop standalone multiplatform software with the power of modern HTML5, CSS and JS scripting techniques for easy interface development, server sessions for network user authentication, database support for more complex applications, as well as python high level libraries for almost anything else. I decided to share the web server code with the hope that someone will find it useful or will help improving it. 

# Requirements
- Python 3.6 or later (https://www.python.org/downloads/release/python-360/)

# Features

- Mulththreaded HTTP server
- Tested on Win, Mac, LINUX.
- GET/POST/OPTIONS request are supported
- Server session management
- URL rewriting support
- MySQL support (requires Python MySQLdb module)
- Python scripting output to browser
- Header manipulation
- GET and POST parameter management (see core/http.py)
- Logging

# Install

0. Extract files to any folder
1. Edit aws.conf file to match your needs
2. Execute httpd.py (accepts alternate config files as argument)

# Contributing

Feel free to report any problem, ask for help, or improve it
