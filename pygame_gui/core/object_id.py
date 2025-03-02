from collections import namedtuple

ObjectID = namedtuple(
    "ObjectID", ("object_id", "class_id"), defaults=(None, None)
)
