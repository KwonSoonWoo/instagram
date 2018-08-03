from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.compat import authenticate
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from members.models import User
from members.serializers import UserBaseSerializer


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserBaseSerializer


# class AuthToken1(ObtainAuthToken):
#
#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data,
#                                            context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']
#         token, created = Token.objects.get_or_create(user=user)
#         return Response({
#             'token': token.key,
#             'user_id': user.pk,
#             'email': user.email
#         })


class AuthToken(APIView):
    def post(self, request):
        # 전달받은 데이터에서 username, password추출
        username = request.data.get('username')
        password = request.data.get('password')

        # authenticate 실행
        user = authenticate(username=username, password=password)

        # authenticate가 성공한 경우
        if user:
            # Token을 가져오거나 없으면 생성
            token, __ = Token.objects.get_or_create(user=user)
            # Response에 돌려줄 데이터
            data = {
                'token': token.key,
            }
            return Response(data)
        # authenticate에 실패한 경우
        raise AuthenticationFailed('인증정보가 올바르지 않습니다.')


class AuthenticationTest(APIView):
    # URL: /api/users/auth-test/
    def get(self, request):
        # request.user가 인증 된 상태일 경우, UserSerializer를 사용해 렌더링한 데이터를 보내줌
        # 인증되지 않았을 경우 NotAuthenticated Exception을 raise
        if request.user.is_authenticated:
            return Response(UserBaseSerializer(request.user).data)
        raise NotAuthenticated('로그인 되어있지 않습니다')

