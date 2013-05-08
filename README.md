logit
=====

Simple python module to send log messages in JSON format to remote host. This module is in active development. See branch->exp for latest changes.

Dependencies
===========

`pip install -U jsonpickle`

`pip install simplejson`

`pip install requests`

Usage
=====

Modify `endpoint` in `logit.Logit` to put in your host url.

```
from logit import Logit

log = Logit("mytag")
log.debug("this is a debug message")
log.warning("this is a warning")
log.error("this is an error")
```

A posted json from logit looks like this:

{"message": "this is a debug message", "tag": "new tag", "uuid": "CirfYraXEeKDrtRbUXfAdHxg", "level": "debug"}


