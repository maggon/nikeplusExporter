#    This file is part of python-nikeplus-2013.
#
#    Copyright 2013 Daniel Alexander Smith
#    Copyright 2013 University of Southampton
#
#    python-nikeplus-2013 is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    python-nikeplus-2013 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with python-nikeplus-2013.  If not, see <http://www.gnu.org/licenses/>.

import argparse, getpass, logging, nikeplus, pprint, pywebbox, urllib2, sys, json

""" A simple command-line client to demontrate usage of the library. """

logging.basicConfig(level = logging.DEBUG)

parser = argparse.ArgumentParser(description = "Use the Nike+ API")
parser.add_argument('email', type = str, help = "E-mail address of the user in the Nike+ system")
parser.add_argument('user', type=str, help="Webbox username, e.g. webbox")
parser.add_argument('address', type=str, help="Address of the webbox server, e.g. http://webbox.example.com:8211/")
parser.add_argument('box', type=str, help="Box to assert data into")
parser.add_argument('--appid', type=str, default="Nike+ Harvester", help="Override the appid used for the webbox assertions")
parser.add_argument('--debug', default=False, action="store_true", help="Enable debugging")

args = vars(parser.parse_args())
password = getpass.getpass("Nike+ password: ")
webbox_password = getpass.getpass("Webbox password: ")

if args['debug']:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

webbox = pywebbox.WebBox(args['address'], args['box'], args['user'], webbox_password, args['appid'])
version = 0 # box version

def update(data):
    """ Assert data into the webbox.
        If the version is incorrect, the correct version will be grabbed and the update re-sent.

        data -- An object to assert into the box.
    """
    global version
    try:
        response = webbox.update(version, data)
        version = response['data']['@version'] # update the version
    except Exception as e:
        if isinstance(e, urllib2.HTTPError) and e.code == 409: # handle a version incorrect error, and update the version
            response = e.read()
            json_response = json.loads(response)
            version = json_response['@version']
            update(data) # try updating again now the version is correct
        else:
            logging.error("Error updating webbox: {0}".format(e))
            sys.exit(0)


nikeplus = nikeplus.NikePlus()
nikeplus.login(args['email'], password)
nikeplus.get_token()

activities = nikeplus.get_activities()
for activity in activities:
    activity_id = activity['activityId']
    logging.debug("activity id: {0}".format(activity_id))
    detail = nikeplus.get_activity_detail(activity_id)
    logging.debug("activity_details: {0}".format(pprint.pformat(detail)))
    detail['@id'] = "Nike+ Activity: {0}".format(activity_id)
    update(detail)
    

