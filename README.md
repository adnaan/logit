logit
=====

Simple python module to save log messages in JSON format to remote host.

Dependencies
===========

`pip install -U jsonpickle`

`pip install simplejson`

`pip install requests`

Usage
=====

Modify `endpoint` in `logit.py` to put in your host url.

```
from logit import Logit

log = Logit("mytag")
log.debug("this is a debug message")
log.warning("this is a warning")
log.error("this is an error")
```

A posted json from logit looks like this:

{"message": "this is a debug message", "tag": "new tag", "uuid": "BirfYraTEeKRbQAXfAvHxg", "level": "debug"}


