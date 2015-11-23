"""
Manifests are used by promoter to detail which sub-elements of an object's XML are to be included in a new XML
document.

Here is the default layout for a manifest:
{
    objectName: {
        'exclude': [
            Element/Path1,
            Element/Path2
        ],
        'override': {
            Element/Path1: NewValue,
            Element/Path2: NewValue
        },
        'inject': {
            NewElement/Path1: Value,
            NewElement/Path2: Value
        },
        'collections': [
            Element/Path1,
            Element/Path2,
        ]
    }
}

Elements in the 'exclude' list will be omitted.
Elements in the 'override' dictionary must not be in the 'exclude' list or they will be skipped.
New elements can be injected into the output XML by passing the path and value in the 'inject' dictionary
    (e.g. can be used to pass a password with the XML when POSTing to a resource)
Objects that contain collections referencing other objects can be listed in the 'collections' list
    These collections will have all 'id' elements removed

If there is no manifest in this dictionary the object would be copies as-is.

The three global_ variables are applied to all objects.
    For example: including 'id' and 'site' in the global_exclusions list will remove those elements from
    all ElementTree.Element objects that are processed
"""
__author__ = 'brysontyrrell'

global_exclusions = [
    'general/id',
    'general/site',
    'general/category/id',
    'id',
    'site'
]

global_overrides = {
    'location/phone': '612-605-6625',
    'location/building': 'Minneapolis',
    'location/room': '301 4th Ave S'
}

global_injections = {}

global_collections = {}

manifests = {
    'computer_groups': {
        'exclude': ['computers'],
        'override': {},
        'inject': {},
        'collections': []
    },
    'computers': {
        'exclude': [
            'general/remote_management/management_password_md5',
            'general/remote_management/management_password_sha256',
            'general/distribution_point',
            'general/sus',
            'general/netboot_server',
            'peripherals',
            'groups_accounts/computer_group_memberships',
            'configuration_profiles',
            'purchasing/attachments'
        ],
        'override': {},
        'inject': {'general/remote_management/management_password': 'jamfsoftware'},
        'collections': [
            'extension_attributes',
            'configuration_profiles'
        ]
    },
    'ebooks': {
        'exclude': [
            'general/self_service_icon',
            'self_service/self_service_icon',
            'self_service/self_service_categories',
            'self_service/self_service_icon',
            'vpp_codes'
        ],
        'override': {},
        'inject': {},
        'collections': [
            'scope/computers',
            'scope/computer_groups',
            'scope/buildings',
            'scope/departments',
            'scope/mobile_devices',
            'scope/mobile_device_groups',
            'scope/limitations/user_groups',
            'scope/limitations/network_segments',
            'scope/limitations/ibeacons',
            'scope/exclusions/computers',
            'scope/exclusions/computer_groups',
            'scope/exclusions/buildings',
            'scope/exclusions/departments',
            'scope/exclusions/mobile_devices',
            'scope/exclusions/mobile_device_groups',
            'scope/exclusions/user_groups',
            'scope/exclusions/network_segments',
            'scope/exclusions/ibeacons',
            'self_service/self_service_categories'
        ]
    },
    'ldap_servers': {
        'exclude': [
            'account/password_md5',
            'account/password_sha256'
        ],
        'override': {
            'connection/account/distinguished_username':
                'CN=Captain Kirk,OU=Test Accounts,OU=Staff'
        },
        'inject': {'connection/account/password': 'GoClimbARock'},
        'collections': []
    },
    'mac_applications': {
        'exclude': [
            'self_service/self_service_categories',
            'self_service/self_service_icon',
            'vpp_codes'
        ],
        'override': {},
        'inject': {},
        'collections': [
            'scope/computers',
            'scope/computer_groups',
            'scope/buildings',
            'scope/departments',
            'scope/limitations/user_groups',
            'scope/limitations/network_segments',
            'scope/limitations/ibeacons',
            'scope/exclusions/computers',
            'scope/exclusions/computer_groups',
            'scope/exclusions/buildings',
            'scope/exclusions/departments',
            'scope/exclusions/user_groups',
            'scope/exclusions/network_segments',
            'scope/exclusions/ibeacons'
        ]
    },
    'mobile_device_applications': {
        'exclude': [
            'general/ipa',
            'general/icon',
            'general/provisioning_profile',
            'self_service/self_service_categories',
            'self_service/self_service_icon'
        ],
        'override': {},
        'inject': {},
        'collections': [
            'scope/mobile_devices',
            'scope/mobile_device_groups',
            'scope/buildings',
            'scope/departments',
            'scope/limitations/user_groups',
            'scope/limitations/network_segments',
            'scope/limitations/ibeacons',
            'scope/exclusions/mobile_devices',
            'scope/exclusions/mobile_device_groups',
            'scope/exclusions/buildings',
            'scope/exclusions/departments',
            'scope/exclusions/user_groups',
            'scope/exclusions/network_segments',
            'scope/exclusions/ibeacons'
        ]
    },
    'mobile_device_configuration_profiles': {
        'exclude': ['self_service/self_service_icon'],
        'override': {},
        'inject': {},
        'collections': [
            'scope/mobile_devices',
            'scope/mobile_device_groups',
            'scope/buildings',
            'scope/departments',
            'scope/limitations/user_groups',
            'scope/limitations/network_segments',
            'scope/limitations/ibeacons',
            'scope/exclusions/mobile_devices',
            'scope/exclusions/mobile_device_groups',
            'scope/exclusions/buildings',
            'scope/exclusions/departments',
            'scope/exclusions/user_groups',
            'scope/exclusions/network_segments',
            'scope/exclusions/ibeacons',
            'self_service/self_service_categories'
        ]
    },
    'mobile_device_groups': {
        'exclude': ['mobile_devices'],
        'override': {},
        'inject': {},
        'collections': []
    },
    'mobile_devices': {
        'exclude': [
            'general/computer',
            'general/phone_number'
            'configuration_profiles',
            'provisioning_profiles',
            'mobile_device_groups',
            'purchasing/attachments'
        ],
        'override': {},
        'inject': {},
        'collections': ['extension_attributes']
    },
    'network_segments': {
        'exclude': [],
        'override': {'distribution_server': 'jds.starfleet.corp'},
        'inject': {},
        'collections': []
    },
    'os_x_configuration_profiles': {
        'exclude': ['self_service/self_service_icon'],
        'override': {},
        'inject': {},
        'collections': [
            'scope/computers',
            'scope/computer_groups',
            'scope/buildings',
            'scope/departments',
            'scope/limitations/user_groups',
            'scope/limitations/network_segments',
            'scope/limitations/ibeacons',
            'scope/exclusions/computers',
            'scope/exclusions/computer_groups',
            'scope/exclusions/buildings',
            'scope/exclusions/departments',
            'scope/exclusions/user_groups',
            'scope/exclusions/network_segments',
            'scope/exclusions/ibeacons',
            'self_service/self_service_categories'
        ]
    },
    'peripherals': {
        'exclude': [
            'general/computer_id',
            'location/phone',
            'attachments'
        ],
        'override': {},
        'inject': {},
        'collections': []
    },
    'policies': {
        'exclude': [
            'general/override_default_settings',
            'self_service/self_service_icon',
            'account_maintenance/open_firmware_efi_password',
            'disk_encryption'
        ],
        'override': {},
        'inject': {},
        'collections': [
            'scope/computers',
            'scope/computer_groups',
            'scope/buildings',
            'scope/departments',
            'scope/limitations/user_groups',
            'scope/limitations/network_segments',
            'scope/limitations/ibeacons',
            'scope/exclusions/computers',
            'scope/exclusions/computer_groups',
            'scope/exclusions/buildings',
            'scope/exclusions/departments',
            'scope/exclusions/user_groups',
            'scope/exclusions/network_segments',
            'scope/exclusions/ibeacons',
            'self_service/self_service_categories',
            'package_configuration/packages'
        ]
    },
    'user_groups': {
        'exclude': ['users'],
        'override': {},
        'inject': {},
        'collections': []
    },
    'users': {
        'exclude': [
            'sites',
            'links',
            'ldap_server/id'
        ],
        'override': {'phone_number': '612-605-6625'},
        'inject': {},
        'collections': ['extension_attributes']
    }
}