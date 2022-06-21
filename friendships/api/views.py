from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from friendships.api.serializers import (
    FollowerSerializer,
    FollowingSerializer,
    FriendshipSerializerForCreate,
)
from friendships.models import Friendship


class FriendshipViewSet(viewsets.GenericViewSet):
    # we want POST /api/friendship/1/follow is to follow user whose id = 1
    # so the queryset need to be User.objects.all()
    # if we use Friendship.objects.all, there will be 404
    # because detail = True will first use get_object()
    # queryset.filter(pk=1) will first find whether the object exist

    queryset = User.objects.all()

    # get fans' information
    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        friendships = Friendship.objects.filter(to_user_id=pk).order_by('-created_at')
        serializer = FollowerSerializer(friendships, many=True)
        return Response(
            {'followers': serializer.data},
            status=status.HTTP_200_OK,
        )

    # get followee information
    # AllowAny: any user can visit this list
    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        friendships = Friendship.objects.filter(from_user_id=pk).order_by('-created_at')
        serializer = FollowingSerializer(friendships, many=True)
        return Response(
            {'followings': serializer.data},
            status=status.HTTP_200_OK,
        )

    # create friendships
    # only authenticated user can create this
    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def follow(selfself, request, pk):
        # if repeat follow in some minutes, do not return errors
        # give the net some time to react
        if Friendship.objects.filter(from_user=request.user, to_user=pk).exists():
            return Response({
                'success': True,
                'duplicate': True,
            }, status=status.HTTP_201_CREATED)
        serializer = FriendshipSerializerForCreate(data={
            'from_user_id': request.user.id,
            'to_user_id': pk,
        })
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({'success': True}, status=status.HTTP_201_CREATED)

    # delete a friendship
    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk):
        # pk is str, we need to convert into int
        if request.user.id == int(pk):
            return Response({
                'success': False,
                'message': 'You cannot unfollow yourself',
            }, status=status.HTTP_400_BAD_REQUEST)
        # we should not use CASCADE here, because it will delete all related data
        deleted, _ = Friendship.objects.filter(
            from_user=request.user,
            to_user=pk,
        ).delete()
        return Response({'success': True, 'deleted': deleted})