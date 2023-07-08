from rest_framework import serializers

from blog.models import Post, Comments

class CommentsSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Comments
        fields = ['name', 'email']

class PostSerializer(serializers.ModelSerializer):
    comments = CommentsSerializer(many=True, read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'user_id', 'comments']