from collections import namedtuple

ObjectID = namedtuple(
    "ObjectID", field_names=("object_id", "class_id"), defaults=(None, None)
)
