""" 

	Python page eyample
	See core/http.py for http helper methods

"""

html = '<h1>It works!</h1>'
html += '<form method="get" action="/"><input name="testvar" value="any text" /><input type="submit" value="Test query string"></form>'

testvar = http.get('testvar')
if testvar:
	html += '<h2>You submitted: '+testvar+'</h2>'

print(html)
