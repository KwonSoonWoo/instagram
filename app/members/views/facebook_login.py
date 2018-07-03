import json

import requests
from django.conf import settings
from django.contrib.auth import login, get_user_model
from django.shortcuts import redirect

User = get_user_model()

__all__ = (
    'facebook_login',
)


def facebook_login(request):
    def get_access_token(code):
        """
        Authorization code를 사용해 액세스 토큰을 받아옴
        :param code: 유저의 페이스북 인증 후 전달되는 Authorization code
        :return: 액세스 토큰 문자열
        """
        # GET parameter의 'code'에 값이 전달됨 (authentication code)
        # 전달받은 인증코드를 사용해서 액세스토큰을 받음
        url = 'https://graph.facebook.com/v3.0/oauth/access_token'
        params = {
            'client_id': settings.FACEBOOK_APP_ID,
            'redirect_uri': 'http://localhost:8000/members/facebook-login/',
            'client_secret': settings.FACEBOOK_APP_SECRET_CODE,
            'code': code,
        }
        response = requests.get(url, params)
        # 파이썬에 내장된 json모듈을 사용해서, JSON형식의 텍스트를 파이썬 Object로 변환
        response_dict = json.loads(response.text)
        # 위와 같은 결과
        response_dict = response.json()
        access_token = response_dict['access_token']
        return access_token

    def debug_token(token):
        """
        주어진 token을 Facebook의 debug_token API Endpoint를 사용해 검사
        :param token: 액세스 토큰
        :return: JSON응답을 파싱한 파이썬 Object
        """
        # 받은 액세스 토큰을 debug
        # 결과에서 해당 토큰의 user_id(사용자 고유값)를 가져올 수 있음
        url = 'https://graph.facebook.com/debug_token'
        params = {
            'input_token': token,
            'access_token': '{}|{}'.format(
                settings.FACEBOOK_APP_ID,
                settings.FACEBOOK_APP_SECRET_CODE,
            )
        }
        response = requests.get(url, params)
        return response.json()

    def get_user_info(token, fields=('id', 'name', 'first_name', 'last_name', 'picture')):
        """
        주어진 token에 해당하는 Facebook User의 정보를 리턴
        'id,name,first_name,last_name,picture'
        :param token: Facebook User토큰
        :param fields: join()을 사용해 문자열을 만들 Sequence객체
        :return: JSON응답을 파싱한 파이썬 Object
        """
        # GraphAPI의 'me'(User)를 이용해서 Facebook User정보 받아오기
        url = 'https://graph.facebook.com/v3.0/me'
        params = {
            'fields': ','.join(fields),
            # 'fields': 'id,name,first_name,last_name,picture',
            'access_token': token,
        }
        response = requests.get(url, params)
        return response.json()

    def create_user_from_facebook_user_info(user_info):
        """
        Facebook GraphAPI의 'User'에 해당하는 응답인 user_info로부터
        id, first_name, last_name, picture항목을 사용해서
        Django의 User를 가져오거나 없는경우 새로 만듬 (get_or_create)
        :param user_info: Facebook GraphAPI - User의 응답
        :return: get_or_create의 결과 tuple (User instance, Bool(created))
        """
        # 받아온 정보 중 회원가입에 필요한 요소들 꺼내기
        facebook_user_id = user_info['id']
        first_name = user_info['first_name']
        last_name = user_info['last_name']
        url_img_profile = user_info['picture']['data']['url']

        # facebook_user_id가 username인 User를 기준으로 가져오거나 새로 생성
        return User.objects.get_or_create(
            username=facebook_user_id,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
            },
        )

    code = request.GET.get('code')
    access_token = get_access_token(code)
    user_info = get_user_info(access_token)
    user, user_created = create_user_from_facebook_user_info(user_info)

    # 생성한 유저로 로그인
    login(request, user)
    return redirect('index')