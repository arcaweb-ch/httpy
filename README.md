# httpy
Simple python http server with python interpreter.

# Info

I made this as a simple web application development environment with Python interpreter and MySQL support. The first idea was to combine it with cefpython (https://github.com/cztomczak/cefpython) to be able to develop standalone multiplatform software with the power of modern HTML5, CSS and JS scripting techniques, and robust Python support, with less depandancies as possible.

# Requirements
- Python 3.6 or later (https://www.python.org/downloads/release/python-360/)

# Features

- Mulththreaded HTTP server
- Supports Python code with basic error output (see webrooot/index.py)
- Tested on Win, Mac, LINUX.
- GET/POST/OPTIONS request are supported
- Server session file management
- URL rewriting support
- MySQL support (requires Python MySQLdb module)
- Header manipulation
- GET and POST parameter management (see core/http.py)
- Logging

# Install

0. Extract files to any folder
1. Edit aws.conf file to match your needs
2. Execute httpd.py (accepts alternate config files as argument)

# Warning

This code has been shared for learning purposes, it's not meant to be used as public server in production environment.

# Contributing

Feel free to report any problem, ask for help, or improve it!
