logit
=====

Simple python module to send log messages in JSON format to remote host. It wraps the `logging` package, therefore normal logging operation is not interuppted. Project, App and User-Defined tags are available. It uses the `watchdog` library to observe directory changes and upload log files automatically. This library is in active development. Observe caution while using.

Features
========
1. Project, App and User Defined log tags
2. Start and Stop logging to remote host
3. Local log caching

Dependencies
===========

`pip install -U jsonpickle`

`pip install simplejson`

`pip install requests`

`pip install watchdog`

`pip install pathtools`

Config
=====

`endpoint` : remote host url
`headers`: http request headers
`cacheEnabled` : if `True` all logs are saved to filesytem before uploading
`maxSize`: Maximum size of an App log payload before it's uploaded or cached(on `cacheEnabled` or remote host failure)
`cachedFilesPath`: log directory path. ensure permission.
`cachedFileExtensionSuffix`: log file extension

Usage
=====

Modify `endpoint` in `logit.py` to put in your host url.

```
from logit import Logit
# returns a singleton instance.
log = Logit("project-tag","app1-tag")
#to create new/switch app level tag just do:
log.setAppTag("app2-tag")

log.debug("my-tag", "this is is a debug message")
log.warning("my-tag","this is a warning")
log.error("my-tag","this is an error")
```

A posted json from logit looks like this:

{"message": "this is a debug message", "tag": "new tag", "uuid": "CirfYraXEeKDrtRbUXfAdHxg", "level": "debug"}


TODOS
====
1. Better configuration
2. Cache Max Age
3. Testing





