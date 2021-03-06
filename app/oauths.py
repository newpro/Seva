"""
Oauth abstraction classes
Based on: https://blog.miguelgrinberg.com/post/oauth-authentication-with-flask
"""
from rauth import OAuth1Service, OAuth2Service
from . import loader
from flask import current_app, url_for, request, redirect, session

class OAuthBase(object):
    """
    Oauth base class
    
    Allow flexible and quick expansion of social platform support 
    """
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        self.store_user = False # flag for user storeage
        if loader.enabled('mongo'):
            self.store_user = True
            self.mongo = current_app.mongo
        credentials = loader.get_oauth(provider_name)
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    def authorize(self):
        raise NotImplementedError()

    def callback(self):
        raise NotImplementedError()

    def get_callback_url(self):
        return url_for('oauth_callback', provider=self.provider_name,
                       _external=True)

    @classmethod
    def get_provider(self, provider_name):
        if not loader.enabled(provider_name):
            raise Exception('Oauth provide not enabled: {}'.format(provider_name))
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]

class FacebookSignIn(OAuthBase):
    def __init__(self):
        super(FacebookSignIn, self).__init__('facebook')
        self.service = OAuth2Service(
            name='facebook',
            client_id=current_app.config['FACEBOOK_KEY'],
            client_secret=current_app.config['FACEBOOK_SECRET'],
            authorize_url='https://graph.facebook.com/oauth/authorize',           
            access_token_url='https://graph.facebook.com/oauth/access_token',
            base_url='https://graph.facebook.com/'
        )

    def authorize(self):
        return redirect(
            self.service.get_authorize_url(
                scope='email',
                response_type='code',
                redirect_uri=self.get_callback_url()
            )
        )

    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()}
        )
        me = oauth_session.get('me?fields=id,email').json()
        if self.store_user and (not self.mongo['facebook'].find_one({"id": me['id']})):
            self.mongo['facebook'].insert_one(me)
        return (
            'facebook$' + me['id'],
            me.get('email').split('@')[0],  # Facebook does not provide username
            me.get('email')
        )

class TwitterSignIn(OAuthBase):
    def __init__(self):
        super(TwitterSignIn, self).__init__('twitter')
        self.service = OAuth1Service(
            name='twitter',
            consumer_key=current_app.config['TWITTER_KEY'],
            consumer_secret=current_app.config['TWITTER_SECRET'],
            request_token_url='https://api.twitter.com/oauth/request_token',
            authorize_url='https://api.twitter.com/oauth/authorize',
            access_token_url='https://api.twitter.com/oauth/access_token',
            base_url='https://api.twitter.com/1.1/'
        )

    def authorize(self):
        request_token = self.service.get_request_token(
            params={'oauth_callback': self.get_callback_url()}
        )
        session['request_token'] = request_token
        return redirect(self.service.get_authorize_url(request_token[0]))

    def callback(self):
        request_token = session.pop('request_token')
        if 'oauth_verifier' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            request_token[0],
            request_token[1],
            data={'oauth_verifier': request.args['oauth_verifier']}
        )
        me = oauth_session.get('account/verify_credentials.json').json()
        if self.store_user and (not self.mongo['twitter'].find_one({"id": me.get('id')})):
            self.mongo['twitter'].insert_one(me)
        social_id = 'twitter$' + str(me.get('id'))
        username = me.get('screen_name')
        return social_id, username, None   # Twitter does not provide email
