"""A simple wrapper for the JSS REST API"""
import logging
import requests
import xml.etree.ElementTree as etree

__author__ = 'brysontyrrell'
__version__ = '1.0'


class JSS(object):
    """
    An object for interacting with the JSS REST API

    set 'read_only' to True to only allow GET requests with the API
        calls to POST, PUT and DELETE will return a None value

    set 'return_json' to True to have GET requests return JSON instead of XML
        the JSS API can only accept XML for POST and PUT requests

    The HTTP method is inferred by the values passed to the resource

        GET: provide no value for 'id_name' or pass an integer (id) or string (name)
        POST: provide 'data' in string format or an ElementTree.Element object
        PUT: provide a value for 'id_name" and 'data' in string format or an ElementTree.Element object
        DELETE: provide a value for 'id_name' and pass 'delete=True'

    TODO:
    _update_only_object()
        Objects that only support GET, PUT requests
        /activationcode
        /byoprofiles
        /computercheckin
        /gsxconenction
        /smtpserver

    _invitation_object()
        Invitations support GET, POST, DELETE requests
        /computerinvitations
        /mobiledeviceinvitations

    _file_upload()
        Need to design use of this endpoint - add-on to existing methods that support fileupload?
        /fileupload

    _subset_object()
        Build subset support for objects that support it

    Add objects that are not implemented

    Add exceptions
    """
    def __init__(self, url, username, password, read_only=False, return_json=False):
        """Initialize the JSS class"""
        self._session = requests.Session()
        self._session.auth = (username, password)
        self._url = '{}/JSSResource'.format(url)
        self._read_only = read_only
        self.version = self._get_version()
        self._content_header = {"Content-Type": "text/xml"}
        self._accept_header = {"Accept": "application/xml"} if not return_json else {"Accept": "application/json"}

    def _get_version(self):
        """Returns the version of the JSS (uses deprecated API)"""
        resp = self._session.get('{}/jssuser'.format(self._url))
        resp.raise_for_status()
        return etree.fromstring(resp.text).findtext('version')

    @staticmethod
    def _is_int(value):
        """Tests a value to determine if it should be treated as an integer or string"""
        try:
            int(value)
        except ValueError:
            return False
        except TypeError:
            raise Exception
        else:
            return True

    @staticmethod
    def _return_list(xml, list_value):
        """Returns a list of ids for a collection"""
        id_list = [int(i.findtext('id')) for i in etree.fromstring(xml).findall(list_value)]
        id_list.sort()
        return id_list

    @staticmethod
    def _return_group_list_filtered(xml, list_value, group_filter):
        """Returns a list of ids for a group collection with an optional filter for only 'smart' and 'static'"""
        id_list = list()
        # It can be assumed that the only other possible value is 'static' - see _get()
        match = 'true' if group_filter == 'smart' else 'false'
        for i in etree.fromstring(xml).findall(list_value):
            if i.findtext('is_smart') == match:
                id_list.append(int(i.findtext('id')))

        id_list.sort()
        return id_list

    @staticmethod
    def _element_check(data):
        """Checks if a value is an xml.etree.ElementTree.Element object and returns a string"""
        if isinstance(data, etree.Element):
            logging.debug("attempting to convert to xml string")
            return etree.tostring(data)
        else:
            return data

    def _append_id_name(self, url, value):
        """Appends '/id/value' or '/name/value' to a url"""
        return '{}/id/{}'.format(url, value) if self._is_int(value) else '{}/name/{}'.format(url, value)

    def _get(self, url, list_value=None, group_filter=None):
        """REST API GET request
            returns a list of ids (as integers) for a collection
            returns a string (xml text) for single objects"""
        logging.debug('GET: {}'.format(url))
        resp = self._session.get(url, headers=self._accept_header)
        resp.raise_for_status()
        if list_value and group_filter is None:
            logging.debug("returning id list for collection")
            return self._return_list(resp.text, list_value)
        elif list_value and group_filter:
            logging.debug("returning filtered list of ids for group collection")
            return self._return_group_list_filtered(resp.text, list_value, group_filter)
        else:
            return resp.text

    def _post(self, url, xml):
        """REST API POST request
            returns the id of the created resource
            returns None if 'read_only' is True"""
        data = self._element_check(xml)
        logging.debug('POST: {}'.format(url))
        logging.debug('DATA: {}'.format(data))
        if self._read_only:
            logging.info("api read_only is enabled")
            return None

        url += '/id/0'
        resp = self._session.post(url, data, headers=self._content_header)
        resp.raise_for_status()
        return etree.fromstring(resp.text).findtext('id')

    def _put(self, url, xml):
        """REST API PUT request
            returns the id of the updated resource
            returns None if 'read_only' is True"""
        data = self._element_check(xml)
        logging.debug('PUT: {}'.format(url))
        logging.debug('DATA: {}'.format(data))
        if self._read_only:
            logging.info("api read_only is enabled")
            return None

        resp = self._session.put(url, data, headers=self._content_header)
        resp.raise_for_status()
        return etree.fromstring(resp.text).findtext('id')

    def _delete(self, url):
        """REST API DELETE request
            returns the id of the deleted resource
            returns None if 'read_only' is True"""
        logging.debug('DELETE: {}'.format(url))
        if self._read_only:
            logging.info("api read_only is enabled")
            return None

        resp = self._session.delete(url)
        resp.raise_for_status()
        return etree.fromstring(resp.text).findtext('id')

    def _standard_object(self, **kwargs):
        """Method for interacting with most objects"""
        id_name = kwargs.pop('id_name')
        data = kwargs.pop('data')
        delete = kwargs.pop('delete')
        path = kwargs.pop('path')
        list_value = kwargs.pop('list_value')
        obj_url = '{}/{}'.format(self._url, path)
        if not (id_name or data or delete):
            return self._get(obj_url, list_value)
        elif data and not (id_name or delete):
            return self._post(obj_url, data)
        else:
            obj_url = self._append_id_name(obj_url, id_name)
            if id_name and not (data or delete):
                return self._get(obj_url)
            elif id_name and data and not delete:
                return self._put(obj_url, data)
            elif id_name and delete and not data:
                return self._delete(obj_url)
            else:
                raise Exception

    def _group_object(self, **kwargs):
        """Method for interacting with group objects"""
        id_name = kwargs.pop('id_name')
        data = kwargs.pop('data')
        delete = kwargs.pop('delete')
        path = kwargs.pop('path')
        list_value = kwargs.pop('list_value')
        obj_url = '{}/{}'.format(self._url, path)
        if not (id_name or data or delete):
            group_filter = kwargs.pop('group_filter')
            if group_filter not in ('smart', 'static', None):
                logging.debug("invalid filter: must be 'smart', 'static' or None")
                raise Exception

            return self._get(obj_url, list_value, group_filter)
        elif data and not (id_name or delete):
            return self._post(obj_url, data)
        else:
            obj_url = self._append_id_name(obj_url, id_name)
            if id_name and not (data or delete):
                return self._get(obj_url)
            elif id_name and data and not delete:
                return self._put(obj_url, data)
            elif id_name and delete and not data:
                return self._delete(obj_url)
            else:
                raise Exception

    def buildings(self, id_name=None, data=None, delete=False):
        """/JSSResource/buildings"""
        return self._standard_object(id_name=id_name, data=data, delete=delete, path='buildings', list_value='building')

    def categories(self, id_name=None, data=None, delete=False):
        """/JSSResource/categories"""
        return self._standard_object(id_name=id_name, data=data, delete=delete, path='categories',
                                     list_value='category')

    def computers(self, id_name=None, data=None, delete=False):
        """/JSSResource/computers"""
        return self._standard_object(id_name=id_name, data=data, delete=delete, path='computers', list_value='computer')

    def computer_extension_attributes(self, id_name=None, data=None, delete=False):
        """/JSSResource/computerextensionattributes"""
        return self._standard_object(id_name=id_name, data=data, delete=delete, path='computerextensionattributes',
                                     list_value='computer_extension_attribute')

    def computer_groups(self, id_name=None, data=None, delete=False, group_filter=None):
        """
        /JSSResource/computergroups
            group_filter: 'smart', 'static' or None
        """
        return self._group_object(id_name=id_name, data=data, delete=delete, path='computergroups',
                                  list_value='computer_group', group_filter=group_filter)

    def departments(self, id_name=None, data=None, delete=False):
        """/JSSResource/departments"""
        return self._standard_object(id_name=id_name, data=data, delete=delete, path='departments',
                                     list_value='department')

    def ebooks(self, id_name=None, data=None, delete=False):
        """/JSSResource/ebooks"""
        return self._standard_object(id_name=id_name, data=data, delete=delete, path='ebooks', list_value='ebook')

    def ibeacons(self, id_name=None, data=None, delete=False):
        """/JSSResource/ibeacons"""
        return self._standard_object(id_name=id_name, data=data, delete=delete, path='ibeacons', list_value='ibeacon')

    def ldap_servers(self, id_name=None, data=None, delete=False):
        """/JSSResource/ldapservers"""
        return self._standard_object(id_name=id_name, data=data, delete=delete, path='ldapservers',
                                     list_value='ldap_server')

    def mac_applications(self, id_name=None, data=None, delete=False):
        """/JSSResource/macapplications"""
        return self._standard_object(id_name=id_name, data=data, delete=delete, path='macapplications',
                                     list_value='mac_application')

    def mobile_device_applications(self, id_name=None, data=None, delete=False):
        """/JSSResource/mobiledeviceapplications"""
        return self._standard_object(id_name=id_name, data=data, delete=delete, path='mobiledeviceapplications',
                                     list_value='mobile_device_application')

    def mobile_device_configuration_profiles(self, id_name=None, data=None, delete=False):
        """/JSSResource/mobiledeviceconfigurationprofiles"""
        return self._standard_object(id_name=id_name, data=data, delete=delete,
                                     path='mobiledeviceconfigurationprofiles', list_value='configuration_profile')

    def mobile_device_extension_attributes(self, id_name=None, data=None, delete=False):
        """/JSSResource/mobiledeviceextensionattributes"""
        return self._standard_object(id_name=id_name, data=data, delete=delete, path='mobiledeviceextensionattributes',
                                     list_value='mobile_device_extension_attribute')

    def mobile_device_groups(self, id_name=None, data=None, delete=False, group_filter=None):
        """
        /JSSResource/mobiledevicegroups
            group_filter: 'smart', 'static' or None
        """
        return self._group_object(id_name=id_name, data=data, delete=delete, path='mobiledevicegroups',
                                  list_value='mobile_device_group', group_filter=group_filter)

    def mobile_devices(self, id_name=None, data=None, delete=False):
        """/JSSResource/mobiledevices"""
        return self._standard_object(id_name=id_name, data=data, delete=delete, path='mobiledevices',
                                     list_value='mobile_device')

    def network_segments(self, id_name=None, data=None, delete=False):
        """/JSSResource/networksegments"""
        return self._standard_object(id_name=id_name, data=data, delete=delete, path='networksegments',
                                     list_value='network_segment')

    def os_x_configuration_profiles(self, id_name=None, data=None, delete=False):
        """/JSSResource/osxconfigurationprofiles"""
        return self._standard_object(id_name=id_name, data=data, delete=delete, path='osxconfigurationprofiles',
                                     list_value='os_x_configuration_profile')

    def packages(self, id_name=None, data=None, delete=False):
        """/JSSResource/packages"""
        return self._standard_object(id_name=id_name, data=data, delete=delete, path='packages', list_value='package')

    def peripherals(self, id_name=None, data=None, delete=False):
        """/JSSResource/buildings"""
        return self._standard_object(id_name=id_name, data=data, delete=delete, path='peripherals',
                                     list_value='peripheral')

    def peripheral_types(self, id_name=None, data=None, delete=False):
        """/JSSResource/peripheraltypes"""
        return self._standard_object(id_name=id_name, data=data, delete=delete, path='peripheraltypes',
                                     list_value='peripheral_type')

    def policies(self, id_name=None, data=None, delete=False):
        """/JSSResource/policies"""
        return self._standard_object(id_name=id_name, data=data, delete=delete, path='policies', list_value='policy')

    def printers(self, id_name=None, data=None, delete=False):
        """/JSSResource/printers"""
        return self._standard_object(id_name=id_name, data=data, delete=delete, path='printers', list_value='printer')

    def scripts(self, id_name=None, data=None, delete=False):
        """/JSSResource/scripts"""
        return self._standard_object(id_name=id_name, data=data, delete=delete, path='scripts', list_value='script')

    def user_extension_attributes(self, id_name=None, data=None, delete=False):
        """/JSSResource/userextensionattributes"""
        return self._standard_object(id_name=id_name, data=data, delete=delete, path='userextensionattributes',
                                     list_value='user_extension_attribute')

    def user_groups(self, id_name=None, data=None, delete=False, group_filter=None):
        """
        /JSSResource/usergroups
            group_filter: 'smart', 'static' or None
        """
        return self._group_object(id_name=id_name, data=data, delete=delete, path='usergroups',
                                  list_value='user_group', group_filter=group_filter)

    def users(self, id_name=None, data=None, delete=False):
        """/JSSResource/users"""
        return self._standard_object(id_name=id_name, data=data, delete=delete, path='users', list_value='user')

