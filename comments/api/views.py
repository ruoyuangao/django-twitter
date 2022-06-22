from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from comments.api.serializers import (
    CommentSerializerForCreate,
    CommentSerializer,
    CommentSerializerForUpdate,
)
from comments.models import Comment
from comments.api.permissions import IsObjectOwner



class CommentViewSet(viewsets.GenericViewSet):
    """
    we only realize list, create, update, and destroy
    we do not define retrieve (find one comment)
    because we do not need it
    """
    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()
    filterset_fields = ('tweet_id',)

    def get_permissions(self):
        # use AllowAny() / IsAuthenticated() to realize the object
        # not using AllowAny / IsAuthenticated
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ['destroy', 'update']:
            return [IsAuthenticated(), IsObjectOwner()]
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

    def update(self, request, *args, **kwargs):
        # get_object is wrapped by DRF, it will raise 404 if not found
        # as a result, we do not need to check it here
        serializer = CommentSerializerForUpdate(
            instance=self.get_object(),
            data=request.data,
        )
        if not serializer.is_valid():
            raise Response({
                'message': 'Please check input'
            }, status=status.HTTP_400_BAD_REQUEST)
        # save method will use update method in serializer,
        # save will decide whether run create or update using instance parameter
        comment = serializer.save()
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        comment.delete()
        # DRF will return status code = 204 no content as default
        # here we return success=True to make frontend to make the decision
        return Response({'success': True}, status=status.HTTP_200_OK)


    # get comment list
    def list(self, request, *args, **kwargs):
        if 'tweet_id' not in request.query_params:
            return Response(
                {
                    'message': 'missing tweet_id in request',
                    'success': False,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        queryset = self.get_queryset()
        comments = self.filter_queryset(queryset).order_by('created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(
            {'comments': serializer.data},
            status=status.HTTP_200_OK,
        )