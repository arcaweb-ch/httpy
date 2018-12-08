# httpy
Simple python http server with python interpreter.

# Info

I made this as a simple web application development environment with Python interpreter and MySQL support. The first idea was to combine a python webserver and cefpython (https://github.com/cztomczak/cefpython) to be able to develop standalone multiplatform software with the power of modern HTML5, CSS and JS scripting techniques for easy interface development, server sessions for network user authentication, database support for more complex applications, as well as python high level libraries for almost anything else. I decided to share the web server code with the hope that someone will find it useful or will help improving it. 

# Features

- Mulththreaded HTTP server
- Easy to deploy:
  1. Edit webroot directories in aws.conf file under "conf" folder to match your paths
  2. Execute httpd.py (optional config file path as argument)
- Works on Windows, Linux, and Mac os.
- GET/POST/OPTIONS request are supported
- Server session management
- URL rewriting support
- MySQL support (requires Python MySQLdb module)
- Python scripting output to browser
- Header manipulation
- GET and POST parameter management (see core/http.py)

# Contributing

Feel free to have fun and improve it.
