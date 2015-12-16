# Crawler
Python URL Crawler

- Can use any services (like Scrapy, BS4)
- App will take a list of url as input.
- The data extracted will be a list of images (gif, jpg, png) as output
- App should crawl the URLs recursively only until the second
level (to avoid a large amount of data): Parse all URLs encountered
and add them to the queue, only if you are on the first level of
crawling.
-Serialize the input and output - the result doesn't have to be exactly like the example, but it should be in JSON format.

Example:
$ curl -X POST -d@- http://myapp.domain.tld/jobs << EOF
[
"http://www.beatport.com/",
"http://www.docker.com/"
]
EOF

This request triggers the crawler. The result should be a 202 Accepted, with a job_id in the response.

Then, I need to see what is happening for a given job ID (42 in this example):

$ curl -X GET http://myapp.domain.tld/jobs/42/status
{
"completed": 2,
"inprogress": 2
}

Then I want to get the results of a job:

$ curl -X GET http://myapp.domain.tld/jobs/42
{
"id": 42,
"domains": {
"http://www.beatport.com": [
"http://www.beatport.com/static/img/bodybg.png",
"http://www.beatport.com/static/img/logo.png",
(...)
],
"http://www.docker.com": [
"http://www.docker.com/static/img/padlock.png",
"http://www.docker.com/static/img/navbar-signup.png",
(...)
]
}
}