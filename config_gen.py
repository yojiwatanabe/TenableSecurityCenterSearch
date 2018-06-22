import json
from base64 import b64encode
import getpass

print 'Enter the following mandatory information:'
config_file = raw_input('Enter the name of the config file: ')
user = raw_input('Username: ')
passwd = b64encode(getpass.getpass())
plugin_id = raw_input('Plugin ID: ')
print

print 'Enter the optional arguments. Leave blank if you dont want to pass these arguments'
search_queries = raw_input('Name of file with search queries: ')
repo_list = raw_input('Name of file with list of repositories: ')
host_list = raw_input('Name of the file with the list of IP addresses ')
ip_range = raw_input('IP range in CIDR notation ')
duplicates = raw_input('Do you want to see multiple data for the same host? (yes/no) ') == 'yes'
csv = raw_input('Do you want CSV output? (yes/no) ') == 'yes'

js = {'user':user, 'pass':passwd, 'plugin_id':plugin_id, 'search_list':search_queries, 'repo_list':repo_list, 
	'host_list': host_list, 'ip_range':ip_range, 'duplicates': duplicates, 'csv':csv}
js = json.dumps(js)
f = open(config_file, 'w')
f.write(js)