import logging
import os
import sys
from urllib.parse import parse_qs

import sprockets_dynamodb as dynamodb
import tornado.ioloop
import tornado.web
import tornado_aws


logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)1.1s %(name)s: %(message)s')

LOGGER = logging.getLogger('create-database')
dynamo = dynamodb.Client()
TABLE_DEF = {
    'TableName': 'Responses',
    'AttributeDefinitions': [
        {'AttributeName': 'Form', 'AttributeType': 'S'},
    ],
    'KeySchema': [
        {'AttributeName': 'Form', 'KeyType': 'HASH'},
    ],
    'ProvisionedThroughput': {
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5,
    }
}

class MainHandler(tornado.web.RequestHandler):
    def post(self):
        body_as_unicode = self.decode_argument(self.request.body)
        items = parse_qs(body_as_unicode, keep_blank_values=True)
        dynamo.put_item('Responses', {"Form": items["form"][0], "data":{"what", "butt"}})
        self.write(items)

def make_app():

    settings = {
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
    }

    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/(form\.html)", tornado.web.StaticFileHandler,
            dict(path=settings['static_path']))
    ], **settings)

def on_table_described(describe_response):

    def on_created(create_response):
        try:
            result = create_response.result()
            LOGGER.info('table created - %r', result)
        except Exception:
            LOGGER.exception('failed to create table')
            sys.exit(-1)

    try:
        result = describe_response.result()
        LOGGER.info('future %s', result)
        LOGGER.info('found table %s, created %s',
                    result['TableName'],
                    result['CreationDateTime'])
    except dynamodb.exceptions.ResourceNotFound as error:
        LOGGER.warning('table not found, attempting to create: %s', error)
        next_future = dynamo.create_table(TABLE_DEF)
        tornado.ioloop.IOLoop.current().add_future(next_future, on_created)

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    iol = tornado.ioloop.IOLoop.current()
    iol.add_future(dynamo.describe_table(
            TABLE_DEF['TableName']),
            on_table_described)
    iol.start()
