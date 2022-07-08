from django.core import serializers
from utils.json_encoder import JSONEncoder


class DjangoModelSerializer:

    @classmethod
    def serialize(cls, instance):
        # Django serializers need a QuerySet or list data to do the serialization
        # as a result we should add [] to make instance a list
        return serializers.serialize('json', [instance], cls=JSONEncoder)

    @classmethod
    def deserialize(cls, serialized_data):
        # we need to add ".object" to get the original model's object
        # otherwise, we will not get an ORM object, but a DeserializedObject
        return list(serializers.deserialize('json', serialized_data))[0].object
