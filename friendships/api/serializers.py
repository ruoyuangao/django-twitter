from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from accounts.api.serializers import UserSerializer
from friendships.models import Friendship

# create friendships serializer
class FriendshipSerializerForCreate(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    class Meta:
        model = Friendship
        fields = ('from_user_id', 'to_user_id')

    # users cannot follow their selves
    def validate(self, attrs):
        if attrs['from_user_id'] == attrs['to_user_id']:
            raise ValidationError({
                'message': 'from_user_id and to_user_id should be different'
            })
        return attrs

    # create function to save data
    def create(self, validated_data):
        from_user_id = validated_data['from_user_id']
        to_user_id = validated_data['to_user_id']
        return Friendship.objects.create(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
        )

#  to get all followers' information
class FollowerSerializer(serializers.ModelSerializer):
    user = UserSerializer(source='from_user')
    created_at = serializers.DateTimeField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at')

# to get all fans' information
class FollowingSerializer(serializers.ModelSerializer):
    user = UserSerializer(source='to_user')
    created_at = serializers.DateTimeField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at')