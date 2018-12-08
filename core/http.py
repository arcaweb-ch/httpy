import sys
import os
import contextlib
import re
import pickle
import uuid
import base64
import cgi

class Http:

    env = None 
    custom_headers = {}
    httperror = 0

    def __init__(self, env):

        self.env = env

    def generate_uuid(self):
        return str(uuid.uuid1())

    def session_create(self, obj):

        newid = self.generate_uuid()
        self.header('X-Arc-Set-Session', newid)
        self.set_env('session', obj)
        self.set_env('session_id', newid)
        self.session_save()

    def session_destroy(self):

        sessionid = self.header('X-Arc-Sessionid')

        if sessionid:
            sessionfile = self.get_env('session_path') + '/' + sessionid
            if os.path.exists(sessionfile):
                try:
                    os.remove(sessionfile)
                    return True
                except:
                    pass

        self.header('X-Arc-Set-Session', '0')

    def session_load(self):

        sessionid = self.header('X-Arc-Sessionid')
        if sessionid:
            sessionfile = self.get_env('session_path') + '/' + sessionid
            if os.path.exists(sessionfile):
                with open(sessionfile, 'rb') as f:
                    obj = pickle.load(f)
                    self.set_env('session', obj)
                    self.set_env('session_id', sessionid)
                    return obj
        return False

    def get_auth(self):

        if self.header('X-Arc-Auth'):
            userpass = base64.b64decode(self.header('X-Arc-Auth')).decode('utf-8')
            userpass = re.sub(r'[<>\"\'\\\/]+', '', userpass).split('-')
            u = userpass[0].strip()
            p = userpass[1].strip()
            return (u, p)
        return ('', '')

    def session_save(self):

        if self.get_env('session_id') and self.get_env('session'):
            sessionfile = self.get_env('session_path') + '/' + self.get_env('session_id')
            with open(sessionfile, 'wb') as f:
                pickle.dump(self.get_env('session'), f, pickle.HIGHEST_PROTOCOL)
                f.close()

    def session(self, key = "", obj = ""):

        s = self.get_env('session')

        if s:
            if key:
                if obj:
                    s[key] = obj
                    self.set_env('session', s)
                    self.session_save()
                else:
                    if key in s:
                        return s[key]
            return s
        return {}

    def get_env(self, key=None):

        if key is None:
            return self.env
        try:
            return self.env[key]
        except:
            return ''

    def set_env(self, key, val):

        self.env[key] = val

    def get(self, key=""):

        if key:
            if key in self.env['request_get_params']:
                return self.env['request_get_params'][key]
            else:
                return False
        else:
            return self.env['request_get_params']

    def post(self, key=""):

        # POSTPROCESSOR

        import json

        for k in self.env['request_post_params']:
            if k.endswith('[]'):

                lst = str(self.env['request_post_params'][k]).strip('[]').split(',')
                for i, l in enumerate(lst):

                    
                    l = str(l).replace('\\\"', '"').replace('\\\\', '\\')
                    l = l[1:-1] if l.startswith('"') and l.endswith('"') else l
                    lst[i] = l

                self.env['request_post_params'][k] = lst

            else:

                l = self.env['request_post_params'][k]
                
                l = l[1:-1] if l.startswith('"') and l.endswith('"') else l
                self.env['request_post_params'][k] = str(l).replace('\\\"', '"').replace('\\\\', '\\')

                
        if key:
            if key in self.env['request_post_params']:
                return self.env['request_post_params'][key]
            else:
                return False
        else:
            return self.env['request_post_params']


    def header(self, k, v = None):

        if v is not None:   
            self.custom_headers[k] = v
        else:
            if k in self.env['request_headers']:
                return self.env['request_headers'][k]
            return ''
    def httperror(self, err = 0):

        self.httperror = err


    def pprint(self, obj):

        pp = pprint.PrettyPrinter(indent=4)
        return pp.pformat(obj)

