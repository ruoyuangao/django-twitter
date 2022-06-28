from rest_framework import serializers

from accounts.api.serializers import UserSerializer


class NotificationSerializer(serializers.ModelSerializer):
    recipient = UserSerializer()

    class Meta:
        model = Notification
        fields = {
            'id',
            'recipient',
            'actor_content_type',
            'verb',
            'action_object_content_type',
            'action_object_object_id',
            'target_content_type',
            'target_object_id',
            'timestamp',
            'unread',
        }

class NotificationSerializerForUpdate(serializers.ModelSerializer):
    # true, false, "true", "false", "True" ... are compatible in BooleanField
    unread = serializers.BooleanField()

    class Meta:
        model = Notification
        fields = ('unread',)

    def update(self, instance, validated_data):
        instance.unread = validated_data['unread']
        instance.save()
        return instance

