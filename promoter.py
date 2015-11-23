import logging
from manifests import manifests, global_exclusions, global_overrides, global_injections, global_collections
from requests.exceptions import HTTPError
import os
import xml.etree.ElementTree as etree

__author__ = 'brysontyrrell'


def clean_jss(jss):
    """Iterates over all resources and deletes their objects through the API"""
    order_of_operations = [
        # Objects that have scope
        'ebooks',
        'mac_applications',
        'mobile_device_applications',
        'mobile_device_configuration_profiles',
        'network_segments',
        'os_x_configuration_profiles',
        'peripherals',
        'policies',
        # Device and user records
        'computers',
        'mobile_devices',
        'users',
        # Objects that point to other objects
        'ldap_servers',
        'packages',
        'scripts',
        # Groups
        'computer_groups',
        'mobile_device_groups',
        'user_groups',
        # Stand-alone objects
        'buildings',
        'categories',
        'computer_extension_attributes',
        'departments',
        'ibeacons',
        'mobile_device_extension_attributes',
        'peripheral_types',
        'printers',
        'user_extension_attributes'
    ]
    for resource in order_of_operations:
        logging.info("removing all objects from /{}".format(resource))
        for i in getattr(jss, resource)():
            getattr(jss, resource)(i, delete=True)


def remove_element(root, path):
    """Removes an element from an ElementTree.Element object"""
    parent, child = os.path.split(path)
    try:
        root.remove(root.find(child)) if not parent else root.find(parent).remove(root.find(path))
    except (AttributeError, ValueError):
        logging.info("the element '{}' was not found".format(child))
    else:
        logging.info("the element '{}' was removed".format(child))


def insert_override_element(root, path, value):
    """
    Inserts an element into an ElementTree.Element object or changes the value of an existing element
        Child elements will be created for the passed path
    """
    children = path.split('/')
    if root.find(children[0]) is None:
        logging.info("creating element '{}'".format(children[0]))
        etree.SubElement(root, children[0])

    for p in range(1, len(children)):
        parent_path = '/'.join([children[x] for x in range(p)])
        child_path = '/'.join([children[x] for x in range(p + 1)])
        if root.find(child_path) is None:
            logging.info("creating element '{}'".format(children[p]))
            etree.SubElement(root.find(parent_path), children[p])

    root.find(path).text = value


def remove_element_from_collection(root, path, element='id'):
    """Takes an ElementTree.Element and searches a path for all instances of an element and removes them"""
    collection = root.find(path)
    if collection is not None:
        logging.info("removing '{}' elements from collection: {}".format(element, path))
        for i in collection.getchildren():
            try:
                i.remove(i.find(element))
            except ValueError:
                logging.info("the element '{}' was not found".format(element))

    else:
        logging.info("the collection '{}' was not found".format(path))


def process_xml(data, obj_type):
    """
    Takes an XML string and returns an ElementTree.Element object that has had a manifest applied
        If no manifest exists for the object type it returned the ElementTree.Element object
    """
    src_root = etree.fromstring(data)
    try:
        manifest = manifests[obj_type]
    except KeyError:
        logging.info("there is no manifest for the object: {}".format(obj_type))
        manifest = None

    for element in global_exclusions:
        remove_element(src_root, element)

    for element, value in global_overrides.iteritems():
        insert_override_element(src_root, element, value)

    for element, value in global_injections.iteritems():
        insert_override_element(src_root, element, value)

    for element in global_collections:
        remove_element_from_collection(src_root, element)

    if manifest:
        for element in manifest['exclude']:
            remove_element(src_root, element)

        for element, value in manifest['override'].iteritems():
            insert_override_element(src_root, element, value)

        for element, value in manifest['inject'].iteritems():
            insert_override_element(src_root, element, value)

        for element in manifest['collections']:
            remove_element_from_collection(src_root, element)

    return src_root


def promote_jss(src_jss, trg_jss):
    order_of_operations = [
        # Stand-alone objects
        'buildings',
        'categories',
        'computer_extension_attributes',
        'departments',
        'ibeacons',
        'mobile_device_extension_attributes',
        'peripheral_types',
        'printers',
        'user_extension_attributes',
        # Objects that point to other objects
        'ldap_servers',
        'packages',
        'scripts',
        # Device and user records
        'users',
        'computers',
        'mobile_devices',
        # Groups
        'computer_groups',
        'mobile_device_groups',
        'user_groups',
        # Objects that have scope
        'ebooks',
        'mac_applications',
        'mobile_device_applications',
        'mobile_device_configuration_profiles',
        'network_segments',
        'os_x_configuration_profiles',
        'peripherals',
        'policies'
    ]
    for resource in order_of_operations:
        logging.info("promoting resource: {}".format(resource))
        for i in getattr(src_jss, resource)():
            xml = getattr(src_jss, resource)(i)
            new_object = process_xml(xml, resource)
            try:
                getattr(trg_jss, resource)(data=new_object)
            except HTTPError as e:
                if e.response.status_code == 409:
                    logging.warning(e.message)
                    logging.debug('response error message: {}'.format(e.response.text))
                    logging.warning("the object '{} {}' has not been promoted".format(resource, i))
