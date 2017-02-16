import json

from django.core.urlresolvers import reverse
from django.conf import settings

from example.tests import TestBase
from example.tests.utils import dump_json, redump_json


class GenericViewSet(TestBase):
    """
    Test expected responses coming from a Generic ViewSet
    """

    def setUp(self):
        super(GenericViewSet, self).setUp()

        setattr(settings, 'JSON_API_FORMAT_KEYS', 'dasherize')

    def tearDown(self):

        setattr(settings, 'JSON_API_FORMAT_KEYS', 'camelize')

    def test_default_rest_framework_behavior(self):
        """
        This is more of an example really, showing default behavior
        """
        url = reverse('user-default', kwargs={'pk': self.miles.pk})

        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

        expected = {
            'id': 2,
            'first_name': 'Miles',
            'last_name': 'Davis',
            'email': 'miles@example.com'
        }

        content_dump = redump_json(response.content)
        expected_dump = dump_json(expected)

        assert expected_dump == content_dump


    def test_ember_expected_renderer(self):
        """
        The :class:`UserEmber` ViewSet has the ``resource_name`` of 'data'
        so that should be the key in the JSON response.
        """
        url = reverse('user-manual-resource-name', kwargs={'pk': self.miles.pk})

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        expected = {
            'data': {
                'type': 'data',
                'id': '2',
                'attributes': {
                    'first-name': 'Miles',
                    'last-name': 'Davis',
                    'email': 'miles@example.com'
                }
            }
        }

        content_dump = redump_json(response.content)
        expected_dump = dump_json(expected)

        assert expected_dump == content_dump

    def test_default_validation_exceptions(self):
        """
        Default validation exceptions should conform to json api spec
        """
        expected = {
            'errors': [
                {
                    'status': '400',
                    'source': {
                        'pointer': '/data/attributes/email',
                    },
                    'detail': 'Enter a valid email address.',
                },
                {
                    'status': '400',
                    'source': {
                        'pointer': '/data/attributes/first-name',
                    },
                    'detail': 'There\'s a problem with first name',
                }
            ]
        }
        response = self.client.post('/identities', {
            'email': 'bar', 'first_name': 'alajflajaljalajlfjafljalj'})

        content_dump = redump_json(response.content)
        expected_dump = dump_json(expected)

        assert expected_dump == content_dump

    def test_validation_exceptions_with_included(self):
        """
        Exceptions should be able to be formatted manually
        """
        expected_error = {
            'status': '400',
            'meta': {
                'source': '/included/authors/1/bio',
            },
            'detail': 'This field is required.',
        }
        response = self.client.post('/entries', dump_json({
            'data': {
                'type': 'posts',
                'id': 1,
                'attributes': {
                    'headline': 'A headline',
                    'body_text': 'A body text',
                },
                'relationships': {
                    'blog': {
                        'data': {
                            'type': 'blogs',
                            'id': 1,
                        },
                    },
                    'authors': {
                        'data': [{
                            'type': 'authors',
                            'id': 1,
                        }]
                    }
                },
            },
            'included': [
                {
                    'type': 'blogs',
                    'id': 1,
                    'attributes': {
                        'name': 'A blog name',
                        'tagline': 'A blog tagline',
                    },
                },
                {
                    'type': 'authors',
                    'id': 1,
                    'attributes': {
                        'name': 'Author name',
                        'email': 'author@example.org',
                    },
                },
            ]
        }), content_type='application/vnd.api+json')

        assert expected_error in json.loads(response.content)['errors']
