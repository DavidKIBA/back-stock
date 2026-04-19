from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
 
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # On ajoute des infos utiles directement dans le token JWT
        token['role']      = user.role
        token['full_name'] = user.get_full_name()
        token['email']     = user.email
        return token
