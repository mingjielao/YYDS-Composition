from datetime import datetime
import asyncio

import requests

url_event = 'http://ec2-18-217-39-84.us-east-2.compute.amazonaws.com:5000/api/event/1'
url_user = 'http://ec2-18-217-39-84.us-east-2.compute.amazonaws.com:5001/api/user/1'


async def user():
	requests.get(url_user)
	return 1


async def event():
	requests.get(url_event)
	return 1

async def dynamo():
  await asyncio.sleep(1)
  return 1

# Python 3.7+
async def main():
    s = datetime.now()
    L = await asyncio.gather(
        user(),
        event(),
    )
		
    e = datetime.now()
    print("async results: ", e-s)

def test_async():
	asyncio.run(main())

def test_sync():
	s = datetime.now()
	res = []
	res.append(requests.get(url_event))
	res.append(requests.get(url_user))
	e = datetime.now()
	print(res)
	return res
