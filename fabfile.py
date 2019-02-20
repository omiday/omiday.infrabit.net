"""
Fabric configuration file for Pelican
"""

import SocketServer
import os
import shlex
import shutil
import subprocess
import sys
import fabric.contrib.project as project

from fabric.api import env, hosts, lcd, local
from pelican.server import ComplexHTTPRequestHandler

# Local path configuration (can be absolute or relative to fabfile)
env.deploy_path = 'output'
DEPLOY_PATH = env.deploy_path

# Remote server configuration
PRODUCTION = 'omiday@roadrunner.infrabit.net:22'
DEST_PATH = '/var/www/vhosts/omiday.infrabit.net/html/'

# Rackspace Cloud Files configuration settings
env.cloudfiles_username = 'my_rackspace_username'
env.cloudfiles_api_key = 'my_rackspace_api_key'
env.cloudfiles_container = 'my_cloudfiles_container'

# Github Pages configuration
env.github_pages_branch = "gh-pages"

# Port for `serve`
PORT = 8000


def clean():
    """Remove generated files"""
    if os.path.isdir(DEPLOY_PATH):
        shutil.rmtree(DEPLOY_PATH)
        os.makedirs(DEPLOY_PATH)


def build():
    """Build local version of site"""
    local('pelican -s pelicanconf.py')


def rebuild():
    """`clean` then `build`"""
    clean()
    build()


def regenerate():
    """Automatically regenerate site upon file modification"""
    pelican_cmd = 'pelican -r -s pelicanconf.py'
    args = shlex.split(pelican_cmd)
    # local('pelican -r -s pelicanconf.py')
    try:
        pelican_regenerate_process = subprocess.Popen(args)
    except KeyboardInterrupt:
        pelican_regenerate_process.terminate()


def serve():
    """Serve site at http://localhost:8000/"""
    build()
    os.chdir(env.deploy_path)

    class AddressReuseTCPServer(SocketServer.TCPServer):
        """Server object"""
        allow_reuse_address = True

    server = AddressReuseTCPServer(('', PORT), ComplexHTTPRequestHandler)

    sys.stderr.write('Serving on port {0} ...\n'.format(PORT))
    server.serve_forever()


def preview():
    """Regenerate and serve local site."""
    regenerate()
    serve()


def cf_upload():
    """Publish to Rackspace Cloud Files"""
    rebuild()
    # disable pylint here as per https://github.com/PyCQA/pylint/issues/782
    # pylint: disable=not-context-manager
    with lcd(DEPLOY_PATH):
        local('swift -v -A https://auth.api.rackspacecloud.com/v1.0 '
              '-U {cloudfiles_username} '
              '-K {cloudfiles_api_key} '
              'upload -c {cloudfiles_container} .'.format(**env))


@hosts(PRODUCTION)
def publish():
    """Publish to production via rsync"""
    local('pelican -s publishconf.py')
    project.rsync_project(
        remote_dir=DEST_PATH,
        exclude=".DS_Store",
        local_dir=DEPLOY_PATH.rstrip('/') + '/',
        delete=True,
        extra_opts='-c',
    )


def gh_pages():
    """Publish to GitHub Pages"""
    rebuild()
    local("ghp-import -b {github_pages_branch} {deploy_path}".format(**env))
    local("git push origin {github_pages_branch}".format(**env))
