from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from comments.api.serializers import CommentSerializerForCreate, CommentSerializer
from comments.models import Comment


class CommentViewSet(viewsets.GenericViewSet):
    """
    we only realize list, create, update, and destroy
    we do not define retrieve (find one comment)
    because we do not need it
    """
    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()

    def get_permissions(self):
        # use AllowAny() / IsAuthenticated() to realize the object
        # not using AllowAny / IsAuthenticated
        if self.action == 'create':
            return [IsAuthenticated()]
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        data = {
            'user_id': request.user.id,
            'tweet_id': request.data.get('tweet_id'),
            'content': request.data.get('content'),
        }
        # we must add "data=" to give parameter to specific data
        # because the default first parameter is instance
        serializer = CommentSerializerForCreate(data=data)
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        # save method will user create method in serializer
        comment = serializer.save()
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )