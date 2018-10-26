import json
from io import BytesIO

from django.test import TestCase, override_settings
from rest_framework.exceptions import ParseError

from rest_framework_json_api.parsers import JSONParser


class TestJSONParser(TestCase):

    def setUp(self):
        class MockRequest(object):

            def __init__(self):
                self.method = 'GET'

        request = MockRequest()

        self.parser_context = {'request': request, 'kwargs': {}, 'view': 'BlogViewSet'}

        data = {
            'data': {
                'id': 123,
                'type': 'Blog',
                'attributes': {
                    'json-value': {'JsonKey': 'JsonValue'}
                },
            },
            'meta': {
                'random_key': 'random_value'
            }
        }

        self.string = json.dumps(data)

    @override_settings(JSON_API_FORMAT_KEYS='camelize')
    def test_parse_include_metadata_format_keys(self):
        parser = JSONParser()

        stream = BytesIO(self.string.encode('utf-8'))
        data = parser.parse(stream, None, self.parser_context)

        self.assertEqual(data['_meta'], {'random_key': 'random_value'})
        self.assertEqual(data['json_value'], {'json_key': 'JsonValue'})

    @override_settings(JSON_API_FORMAT_FIELD_NAMES='dasherize')
    def test_parse_include_metadata_format_field_names(self):
        parser = JSONParser()

        stream = BytesIO(self.string.encode('utf-8'))
        data = parser.parse(stream, None, self.parser_context)

        self.assertEqual(data['_meta'], {'random_key': 'random_value'})
        self.assertEqual(data['json_value'], {'JsonKey': 'JsonValue'})

    def test_parse_invalid_data(self):
        parser = JSONParser()

        string = json.dumps([])
        stream = BytesIO(string.encode('utf-8'))

        with self.assertRaises(ParseError):
            parser.parse(stream, None, self.parser_context)

    def test_parse_with_included(self):
        """ test parsing of incoming JSON which includes referenced entities """
        class ViewMock(object):
            resource_name = 'author-bios'

        parser = JSONParser()
        request_data = {
            "data": {
                "type": "author-bios",
                "id": "author-bio-1",
                "attributes": {
                    "body": "This author is cool",
                },
                "relationships": {
                    "author": {
                        "data": {
                            "type": "authors",
                            "id": "author-1"
                        }
                    },
                }
            },
            "included": [{
                "type": "authors",
                "id": "author-1",
                "attributes": {
                    "name": "Homer Simpson",
                    "email": "homer@simpson.com"
                },
            }]
        }

        stream = BytesIO(json.dumps(request_data).encode('utf-8'))
        result_data = parser.parse(stream, parser_context={'view': ViewMock(), 
                                                           'request': self.parser_context['request']})

        expected_data = {
            'id': 'author-bio-1',
            'body': 'This author is cool',
            'author': {
                'type': 'authors',
                'id': 'author-1'
            },
            '_included': {
                'authors': [{
                    'id': 'author-1',
                    'name': 'Homer Simpson',
                    'email': 'homer@simpson.com',
                }]
            },
        }
        self.assertEqual(result_data, expected_data)