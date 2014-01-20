from urlparse import parse_qsl

import psycopg2
import psycopg2.extras

import json

db = psycopg2.connect("dbname='squilla' user='nick' password='hunter12'")

def application(environ, start_response):

    # Get the HTTP parameters

    name = environ['PATH_INFO'][1:]
    assert(name.isalnum())
    query = parse_qsl(environ['QUERY_STRING'], keep_blank_values=True)

    # Turn them into an SQL Query accessing a stored procedure

    sqlquery = (
        'SELECT * FROM public."%s" (' % name +
        ', '.join( '"%s" := %%s' % q[0] for q in query if q[0].isalnum())
    )
    sqlparams = [ str(q[1]) for q in query if q[0].isalnum() ]

    # Turn the response into JSON

    cursor = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cursor.execute(sqlquery, sqlparams)
    response = json.dumps(cursor.fetchall())

    # Return the response in HTTP

    start_response('200 OK', [
        ( 'Content-Type', 'application/json' ),
        ( 'Content-Length', str(len(response)) ),
    ])
    return response

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    make_server('localhost', 8001, application).serve_forever()
