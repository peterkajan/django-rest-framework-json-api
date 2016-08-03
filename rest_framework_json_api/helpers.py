from __future__ import unicode_literals

from rest_framework_json_api.utils import format_value, inner_key_in_dict


class ResourceIdentifier(object):
    """ Object representing pointer to a resource in JSON document """
    class NotFound(Exception):
        pass

    def __init__(self, type_, id_):
        self.resource_type = type_
        self.resource_id = id_

    def __unicode__(self):
        return 'Resource: id - {}, type - {}'.format(self.resource_id, self.resource_type)

    def get_resource(self, resource_map):
        """ Returns data of the resource where this class points to

        Args:
            resource_map: map containing all the resources mapped by type and id

        Returns:
            data dictionary containing resource data
        """
        try:
            return resource_map[format_value(self.resource_type, 'underscore')][self.resource_id]
        except KeyError:
            raise self.NotFound('{} not found'.format(self))

    def check_resource(self, resource_map):
        """ Raise exception if resource does not exist

        Args:
            resource_map: map containing all the resources mapped by type and id
        """
        if not inner_key_in_dict(resource_map, format_value(self.resource_type, 'underscore'), self.resource_id):
            raise self.NotFound('{} not found'.format(self))