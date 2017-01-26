# -- Secrets --
local = {
    'secret': '',
    'db': {
        'user': '',
        'password': '',
        'location': '',
        'name': ''
    },
    'realtime': {
        'url': '',
        'cred_path': '',
        'api_key': ''
    },
    'mongo': { # optional
        'host': '',
        'port': 27017
    },
    'stripe': { # optional
        'secret': '',
        'public': ''
    }
}

remote = {
    'secret': '',
    'db': {'url': ''},
    'realtime': {}
}

testing= {}

global_ = {
    'aws': { # optional
        'bucket': '',
        'key': '',
        'secret': '',
        'region': ''
    },
    'oauth': { # optional
        'twitter': {
            'key': '',
            'secret': ''
        },
        'facebook': {
            'key': '',
            'secret': ''
        }
    }
}
