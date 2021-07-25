from jwt import exceptions
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authentication import BaseAuthentication
from django.conf import settings
import jwt
import datetime


class JwtAuthentication(BaseAuthentication):
    """
        自定义用户token认证
        一般在认证成功后，把jwt生成的token返回给用户，以后用户再次访问时候需要携带token，此时jwt需要对token进行超时及合法性校验。
        获取token之后，会按照以下步骤进行校验：
        将token分割成 header_segment、payload_segment、crypto_segment 三部分
        jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        signing_input, crypto_segment = jwt_token.rsplit(b'.', 1)
        header_segment, payload_segment = signing_input.split(b'.', 1)
        对第一部分header_segment进行base64url解密，得到header
        对第二部分payload_segment进行base64url解密，得到payload
        对第三部分crypto_segment进行base64url解密，得到signature
        对第三部分signature部分数据进行合法性校验
        拼接前两段密文，即：signing_input
        从第一段明文中获取加密算法，默认：HS256
        使用 算法+盐 对signing_input 进行加密，将得到的结果和signature密文进行比较。
    """

    def authenticate(self, request):
        token = request.META.get('HTTP_X_TOKEN', '')
        salt = settings.SECRET_KEY
        try:
            # 从token中获取payload【校验合法性】
            #                    需要解析的jwt 密钥 使用和加密时相同的算法
            payload = jwt.decode(token, salt, algorithms=['HS256'])
        except exceptions.ExpiredSignatureError:
            raise AuthenticationFailed({'code': 50014, 'error': 'token已失效'})
        except jwt.DecodeError:
            raise AuthenticationFailed({'code': 50014, 'error': 'token认证失败'})
        except jwt.InvalidTokenError:
            raise AuthenticationFailed({'code': 50014, 'error': '非法的token'})
        return (payload, token)


def getToken(payload, timeout=1):
    salt = settings.SECRET_KEY
    headers = {
        'typ': 'jwt',
        'alg': 'HS256'
    }
    payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(days=timeout)
    token = jwt.encode(payload=payload, key=salt, algorithm='HS256', headers=headers)
    return token
