class AuthError(Exception):
    '''
    权限异常基类
    '''
    pass

class NotAuthorized(AuthError):
    # 未登录或已过期
    pass

class AuthTimeOut(Exception):
    # 未登录或已过期
    pass


class ApiError(Exception):
    '''
    Api异常基类
    '''
    pass



class KeyStoneApiError(ApiError):
    '''
    KeystoneApi异常基类
    '''
    pass

class GlanceApiError(ApiError):
    '''
    GlanceApi异常基类
    '''
    pass

class CinderApiError(ApiError):
    '''
    CinderApi异常基类
    '''
    pass

class NovaApiError(ApiError):
    '''
    NovaApi异常基类
    '''
    pass

class NeutronApiError(ApiError):
    '''
    NeutronApi异常基类
    '''
    pass


class DomainError(KeyStoneApiError):
    '''
    Domain异常基类
    '''
    pass



class DomainCreateError(DomainError):
    pass


class ProjectError(KeyStoneApiError):
    '''
    项目异常基类
    '''
    pass

class ProjectCreateError(ProjectError):
    pass

class UserError(KeyStoneApiError):
    '''
    用户管理异常基类
    '''
    pass

# 实例异常
class InstanceError(NovaApiError):
    '''
    实例异常基类
    '''
    pass

#
class LockError(Exception):
    pass


class OpenkStackApiError(Exception):
    '''
    OPENSTACK API 异常 基类
    '''
    pass

class HTTP400(OpenkStackApiError):
    pass
class HTTP401(OpenkStackApiError):
    pass
class HTTP403(OpenkStackApiError):
    pass
class HTTP404(OpenkStackApiError):
    pass
class HTTP405(OpenkStackApiError):
    pass
class HTTP413(OpenkStackApiError):
    pass
class HTTP415(OpenkStackApiError):
    pass
class HTTP409(OpenkStackApiError):
    pass
class HTTP503(OpenkStackApiError):
    pass

class ParamsMiss():
    Value = {
        "code": 201,
        "msg": "参数缺失",
        "data": "",
        "success": False
    }

class Success():
    """
    返回成功数据
    """
    Value = ""
    def __init__(self, data="", msg="OK"):
        self.Value = {
            "code": 200,
            "msg": msg,
            "success": True,
            "data": data
        }


class InfoError():
    Value = ""
    def __init__(self, code, msg):
        self.Value = {
            "msg": msg,
            "success": False,
            "code": code,
            "data": ""
        }


class Failed():
    Value = ""
    def __init__(self, msg, data="", code=201):
        self.Value = {
            "msg": msg,
            "success": False,
            "code": code,
            "data": data
        }


# 临时
class RESTAPI():
    def __init__(self, success=True, code=200, data={}, msg=''):
        self.result = {
            'msg': msg,
            'success': success,
            'code': code,
            'data': data
        }


def restapi(success=True, code=200, data={}, msg=''):
    return RESTAPI(success, code, data, msg).result