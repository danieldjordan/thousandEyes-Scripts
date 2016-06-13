#ThousandEyes metrics REST request
#!/usr/bin/env python3

import requests
import argparse

parser = argparse.ArgumentParser(description='Enter Time Frame by using the command line variables.  The Username and API token will be read from credentials.txt which should contain the userline on the first line and API token on the second')
parser.add_argument('-id', help='Test ID', required=False, type=int, metavar='', default=0)
parser.add_argument('-t', '--time', help='Amount of Time', required=True, type=int, metavar='')
parser.add_argument('-I', '--Interval', help='Interval of Time. Allowed values are m, h, d, w (minute, hour, day, week)', required=True, choices=['m', 'h', 'd', 'w'], metavar='')
parser.add_argument('-T', '--Test', help='Test type. Allowed values are loss, latency, or jitter', required=True, choices=['loss', 'latency', 'jitter'], metavar='')
args = parser.parse_args()

apiUrl = ('https://api.thousandeyes.com/v6/')

def getTests(user, pwd):
	testUrl = (apiUrl + 'tests.json')
	testResponse = requests.get(testUrl, auth=(user, pwd))

	if testResponse.status_code != 200:
		print('Status Code:', response.status_code, '-', response.reason)
		exit()

	testData = testResponse.json()

	testName = testData['test']
	testList = []
	print('TestID : Test name - Test type')
	for test in testName:
		print(test['testId'],':',test['testName'], '-', test['type'])
		testList.append(test['testId'])

	validID = False
	while validID == False:
		testChoice = input('Enter Test ID to continue:')
		if int(testChoice) in testList:
			validID = True
	return testChoice

#Pull in user credentials from file, if no credentials file found request from user
try:
	with open('credentials.txt', 'r') as ins:
		credList = ins.read().splitlines()
		user = credList[0]
		pwd = credList[1]
except:
	print('No credentials file found')
	user = input('Enter your username: ')
	pwd = input('Enter your API Token: ')

if args.id == 0:
	print('ID variable Missing')
	testId = input('Enter the ID of the test you would like to test (enter ? for a list of tests): ')
	if testId == '?':
		args.id = getTests(user, pwd)

#107148
url = (apiUrl + 'net/metrics/%s.json?window=%s%s' % (args.id, args.time, args.Interval))

#Convert short argument to full word for use later
if args.Interval == 'm':
	intervalLong = 'Minutes'
elif args.Interval == 'h':
	intervalLong = 'Hours'
elif args.Interval == 'd':
	intervalLong = 'Days'
else:
	intervalLong = 'Weeks'

#Change latency argument to avgLatency returned by API and set units based on test
if args.Test == 'latency':
	test = 'avgLatency'
	units = 'ms'
elif args.Test == 'loss':
	test = args.Test
	units = '%'
else:
	test = args.Test
	units = 'ms'


response = requests.get(url, auth=(user, pwd))

# check for response other than 200
if response.status_code != 200:
	#statusCode()
	print('Status Code:', response.status_code, '-', response.reason)
	exit()

data = response.json()


metric_list = data['net']['metrics']
test_details = data['net']['test']

print ('Selected Test:', test_details['testName'])
out = []
for metric in metric_list:
	out.append(metric[test])

if len(out) != 0:
	testAverage = "%0.2f" % (sum(out)/len(out))
	print('The Average',args.Test, 'for the last', args.time, intervalLong, "is: " + testAverage + units)
else:
	print('No data returned by API')
