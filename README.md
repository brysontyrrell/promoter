# promoter

A Python module for migrating objects between two JSSs (*JAMF Software Server*) via the REST API.

`promoter` was first shown during a remote presentation for [Macbrained.org](http://macbrained.org/recap-may-quantcast/) 

## So, really important here...

I am commiting the current **WORK-IN-PROGRESS** code for the promoter module. This is in no way ready to use as a part of any production workflow. To stress that again:

**DO NOT USE THIS IN PRODUCTION!!!**

In the module's current form it is capable of cleaning out a JSS via the REST API and then migrating objects over to replicate a source (as much as is possible via the REST API). There are a number of features that are not yet complete including:

* Better error handling (JAMF Cloud has been throwing 504 GATEWAY_TIMEOUT errors at me for the sheer number of HTTP requests I could be making)
* Actual encoding handling (right now in my example main.py script I have a hack to reload the Python environment's default encoding as UTF-8 - this really should be handled by the JSS class)
* `dependencies` as a part of the object manifests (see below for how the manifests fit in)
* `jsslib.py` does not cover every endpoint in the JSS REST API
* `jsslib.py` needs to be version aware (API endpoints have made numerous changes in every update since 9.0 was released)
* Fixes to some of the functions in `promoter.py` (insert_override_element() needs to be split up, additional functions to support single object promotion and the inclusion of `dependencies` in the manifests)
* Allowing the user to pass a custom manifest object that will be used in place of the default included manifest (which should be treated more as a 'default' state and not modified)
* Multi-threading API operations for speed
* Lots of other things I'm not remmebering...

As you can see from this short list there is a lot that is not done yet. So, again, please do not use this in any production workflow at this time.

## What does promoter do?

There are a lot of solutions out there for migrating objects between two JSSs and are usually either restores of a MySQL database (if you have access) or using the API. I've seen a lot of great examples of both types. In my case, my JSS environment is entirely hosted (on JAMF Cloud) and any type of replication or copying of objects would have to be via the REST API as I don't have access to the database.

`promoter` was written to allow me to replicate - as much as possible - my production JSS to another hosted JSS to perform testing or QA work.

In addition to being able to replicate these objects through the API I also wanted to be able to selectively manipulate the data I was moving. There are elements in the data I would want to remove, others change and some I would want to insert. Having to manually modify items in the interface to complete my replicated enviroment, but point to test resources, was a cumbersome prospect. My goal was to effectively be able to push a button that would replicate my produciton JSS to any other JSS I pointed to and have it be ready to go using test accounts (like for LDAP) and distribution servers.

### Manifests

Automating the manipulation of the API's XML data as it comes down is handled in promoter through the use of `manifests`. A manifest is a mapping of element paths for a JSS object and dictates the actions that are performed on those elements when promoter is running.

For example, here are the `computers` and `ldap_servers` manifests:

```
manifests = {
    ...
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
    ...
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
    ...
```

A manifest is a Python dictionary that contains five keys:

##### dependencies

**This is not yet written into promoter**

The `dependencies` will be a list of element paths where promoter will look for linked JSS objects (like `categories`), see if they exist on the destination and promote those objects if not. This is a requirement for getting single object promotion working.

##### exclude

These are elements (or as show above paths to elements) that should be removed from the XML as it is being processed by promoter. This is useful for preventing conflicts and/or removing choice data so that it does not appear in a non-production environment.

##### override

These are pre-existing elements that have their values replaced with new values. In the `ldap_servers` manifest the existing value for the `distinguished_username` it being replaced with one for a test account.

In this example the same LDAP server is being used but a different account for accessing it than production.

##### inject

These are new elements to insert into the XML data. Again, for `ldap_servers` an element containing the password for the account that replaced the production username is being injected so the connection is live immediately after the data is POSTed.

##### collections

These are groups within the XML that point to other JSS objects. promoter will remove the `id` tags for each item in the group so when the data is POSTed the JSS will handle linking to the correction object based on name matching.

### API account permissions

While there is a `read_only=True` flag that can be set in `jsslib.py` it would be much safer to setup your API user in your source (usually production) JSS as an *Auditor* which gives full read access but no permissions for creating, updating or deleting.

The target JSS account should be a full admin to avoid issues with creating new objects.

At this time `promoter` does not check the permissions of the account used to authenticate, but that is something that is planned.

## Why post promoter now?

Mostly to prove it isn't vaporware. The `main.py` file is an example script using the current version of the `promoter` module to clean out a target JSS and then begin replicating objects via the API. This example migrates all objects in a specific order to satify dependencies.

The next big step for `promoter` is going to be building in the dependency pieces which will allow individual objects to be moved without having to manually satisfy the requirements of other objects they are linked to or strip out tons of additional data to make it work.

If you're curious about what the project does, how it works in its current form and want to provide some feedback on the direction it's going please do so with a copy of this source. You can reach out to me here, on Slack or Twitter.
