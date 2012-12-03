from __future__ import with_statement

import base64
import contextlib
from distutils.core import Command
from distutils.errors import DistutilsOptionError
import getpass
try:
    import simplejson as json
except ImportError:
    import json
import mimetools
import mimetypes
import os.path
import re
import urllib2


__url__ = 'https://github.com/dahlia/github-distutils'
__author__ = 'Hong Minhee'
__email__ = 'minhee' '@' 'dahlia.kr'
__copyright__ = 'Copyright 2012, Hong Minhee'
__license__ = 'Public Domain'
__version__ = '0.1.1'


class GitHubRequest(urllib2.Request):
    """GitHub API request."""

    def __init__(self, token, url, data=None, headers={}, method=None):
        if isinstance(data, dict):
            data = json.dumps(data)
        headers = dict(headers)
        for key in headers:
            if key.lower() == 'authorization':
                break
        else:
            headers['Authorization'] = 'token ' + token
        urllib2.Request.__init__(self, url, data, headers)
        self.method = method

    def get_method(self):
        if self.method:
            return self.method
        return urllib2.Request.get_method(self)


def make_multipart_formdata(values):
    boundary = mimetools.choose_boundary()
    content_type = 'multipart/form-data; boundary=' + boundary
    def parts():
        for field, value in values:
            field = str(field)
            yield '--' + boundary
            if isinstance(value, basestring):
                yield 'Content-Disposition: form-data; name="' + field + '"'
                yield ''
                yield str(value)
            else:
                filename, mimetype, file_ = value
                yield ('Content-Disposition: form-data; name="' + field +
                       '"; filename="' + str(filename) + '"')
                yield 'Content-Type: ' + str(mimetype)
                yield ''
                while 1:
                    chunk = file_.read(4096)
                    if chunk:
                        yield chunk
                    else:
                        break
        yield '--' + boundary + '--'
        yield ''
    return content_type, '\r\n'.join(parts())


class GitHubClient(object):
    """Minimal GitHub client that signs in and uploads files."""

    def __init__(self, username, password, repository):
        self.username = username
        self.password = password
        self.repository = repository

    @contextlib.contextmanager
    def signin(self, username=None, password=None):
        username = username or self.username
        password = password or self.password
        url = 'https://api.github.com/authorizations'
        auth = 'Basic ' + base64.standard_b64encode(username + ':' + password)
        headers = {'Authorization': auth,
                   'Content-Type': 'application/json'}
        data = {'scopes': ['repo'],
                'note': __name__.replace('_', '-'),
                'note_url': __url__}
        request = urllib2.Request(url, headers=headers, data=json.dumps(data))
        response = urllib2.urlopen(request)
        auth = json.load(response)
        assert isinstance(auth, dict)
        assert 'token' in auth
        def send_request(*args, **kwargs):
            req = GitHubRequest(auth['token'], *args, **kwargs)
            return urllib2.urlopen(req)
        yield send_request
        request = GitHubRequest(auth['token'], auth['url'],
                                headers=headers,
                                method='DELETE')
        response = urllib2.urlopen(request)
        assert response.code == 204

    def upload(self, filename):
        url = 'https://api.github.com/repos/' + self.repository + '/downloads'
        data = {'name': os.path.basename(filename),
                'size': os.path.getsize(filename),
                'content_type': mimetypes.guess_type(filename)[0]}
        with self.signin() as request:
            response = request(url, data=data)
            result = json.load(response)
            with open(filename) as file_:
                s3_values = [
                    ('key', result['path']),
                    ('acl', result['acl']),
                    ('success_action_status', '201'),
                    ('Filename', result['name']),
                    ('AWSAccessKeyId', result['accesskeyid']),
                    ('Policy', result['policy']),
                    ('Signature', result['signature']),
                    ('Content-Type', result['mime_type']),
                    ('file', (result['name'], result['mime_type'], file_))
                ]
                s3_mimetype, s3_body = make_multipart_formdata(s3_values)
            s3_request = urllib2.Request(str(result['s3_url']),
                                         headers={'Content-Type': s3_mimetype},
                                         data=s3_body)
            response = urllib2.urlopen(s3_request)
            response.read()
            assert response.code == 201
        return result['html_url']

    def _find_field(self, form_string, name):
        pattern = (r'<input\s[^<>]*name=[\'"]' + re.escape(name) +
                   r'[\'"]\s[^>]*>')
        tag = re.search(pattern, form_string)
        token = re.search(r'value=[\'"]([^\'"]+)[\'"]', tag.group(0))
        return token.group(1)


class github_upload(Command):
    """Upload package to GitHub."""

    description = __doc__
    user_options = [
        ('repository=', 'R', 'GitHub repository name e.g. user/reponame'),
        ('username=', 'u', 'GitHub username'),
        ('password=', 'p', 'GitHub password')
    ]
    USERNAME_RE = re.compile(r'^[-_.a-zA-Z0-9]+/[-_.a-zA-Z0-9]+$')

    def initialize_options(self):
        self.repository = ''
        self.username = ''
        self.password = ''

    def finalize_options(self):
        if not self.USERNAME_RE.match(self.repository):
            raise DistutilsOptionError('-R/--repository option is incorrect')
        if not self.username:
            self.username = raw_input('GitHub username: ')
        if not self.password:
            self.password = getpass.getpass('GitHub password: ')

    def run(self):
        if not self.distribution.dist_files:
            raise DistutilsOptionError(
                'No dist file created in earlier command'
            )
        gh = GitHubClient(self.username, self.password, self.repository)
        sdist_url = None
        for command, pyversion, filename in self.distribution.dist_files:
            url = gh.upload(filename)
            if command == 'sdist':
                sdist_url = url
        if sdist_url:
            url = sdist_url
        self.distribution.metadata.download_url = url


commands = {'github_upload': github_upload}

