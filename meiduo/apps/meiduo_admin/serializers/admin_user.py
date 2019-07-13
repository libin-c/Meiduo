from rest_framework import serializers

from apps.users.models import User


class AdminSerializer(serializers.ModelSerializer):
    '''
    管理员用户
    '''

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def create(self, validated_data):
        #
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.is_staff = True
        user.save()

        # user = User.objects.create(**validated_data)
        return user
