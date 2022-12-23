from sys import version_info
from collections import namedtuple

if version_info.minor >= 7:
    ObjectID = namedtuple('ObjectID',
                          field_names=('object_id', 'class_id'),
                          defaults=(None, None))
else:
    ObjectID = namedtuple('ObjectID', field_names=('object_id', 'class_id'))