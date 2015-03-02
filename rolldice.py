from dice import parse_expression
from flask import Flask, render_template, request
app = Flask( __name__ )

@app.route("/")
@app.route("/roll")
def index() :
  expr    = ""
  diceset = None
  if request.method == "GET" and request.args.has_key( "expr" ) :
    expr    = request.args.get( "expr" )
    diceset = parse_expression( expr )

  return render_template( 'mainpage.html', diceset = diceset, expr = expr )

if __name__ == "__main__" :
  app.run( host = "127.0.0.1", debug = True )