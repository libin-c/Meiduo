import re

from rest_framework import serializers

from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'password')
        extra_kwargs = {
            'username': {
                'max_length': 20,
                'min_length': 5
            },
            'password':
                {'max_length': 20,
                 'min_length': 8,
                 'write_only': True

                 }
        }

    def validate_mobile(self, attrs):
        """
        手机号验证
        :param attrs:
        :return:
        """
        if not re.match(r'^1[3-9]\d{9}$', attrs):
            raise serializers.ValidationError('手机格式不正确')
        else:
            return attrs

    def create(self, validated_data):
        #
        # user = super().create(validated_data)
        # user.set_password(validated_data['password'])
        # user.save()

        user = User.objects.create(**validated_data)
        return user
