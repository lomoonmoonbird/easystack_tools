# -*- coding: utf-8 -*-

import json
import os
import sys

import requests
# from horizon_mimic import cache, exceptions
import memcache

from easyopenapi import exceptions
from easyopenapi.exceptions import NotAuthorized, HTTP400, HTTP401, HTTP403, HTTP409, HTTP404, HTTP405, \
    HTTP413, HTTP503, HTTP415

from easyopenapi.defaults import EASYSTACCK_KEYSTONE_HOST, EASYSTACCK_NOVA_HOST, EASYSTACCK_GLANCE_HOST, \
    EASYSTACCK_CINDER_HOST, EASYSTACCK_NEUTRON_HOST, EASYSTACCK_0CTAVIA_HOST, username, user_domain_name, password, \
    project_name, JUDGE_URL, \
    JUDGE, STACK_TYPE
import logging

logger = logging.getLogger("api")

local_cache = memcache.Client(['localhost:11211'], debug=True)

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

'''
封装请求easy stack api 的方法
'''


class ResponseCode():
    """
    返回状态码
    """

    def __init__(self, res):
        self.res = res
        self.code = res.status_code

    def __call__(self, *args, **kwargs):
        result = self.res.content.decode()
        if self.code == 400:
            raise HTTP400(f'Bad Request：{result}')
        elif self.code == 401:
            raise NotAuthorized('Authotized Fail')
        elif self.code == 403:
            raise HTTP403(f'Forbidden：{result}')
        elif self.code == 404:
            raise HTTP404(f'Not Found：{result}')
        elif self.code == 405:
            raise HTTP405(f'Method Not Allowed：{result}')
        elif self.code == 413:
            raise HTTP413(f'Request Entity Too Large：{result}')
        elif self.code == 409:
            raise HTTP409(f'Conflict：{result}')
        elif self.code == 415:
            raise HTTP415(f'Unsupported Media Type：{result}')
        elif self.code == 503:
            raise HTTP503(f'Service Unavailable：{result}')
        elif self.code in [200, 202, 204]:
            return self.code
        else:
            raise ValueError("Response Error: {}-{}".format(self.code, result))


def sid_detail(current_sid, url=''):
    """
    生成唯一的sid标识
    """
    global local_cache
    try:
        sid_cache = local_cache.get(current_sid)
    except Exception as e:
        local_cache = memcache.Client(['localhost:11211'], debug=True)
        sid_cache = local_cache.get(current_sid)

    # SidLogInfo.objects.create(
    #     current_sid=current_sid,
    #     memcache_sid=sid_cache,
    #     url=url
    # )
    if sid_cache is not None:
        index = int(sid_cache)
        new_index = index + 1
        new_sid = current_sid + '_' + str(new_index)
        sid_cache = new_index
    else:
        sid_cache = 0
        new_sid = current_sid + '_0'
    local_cache.set(current_sid, str(sid_cache))
    return new_sid


class StackApi(object):
    '''
    调用EasyStackApi专用类
    '''

    def __init__(self, assembly="Keystone"):
        self.req = requests.session()
        self.keystone_token = ''
        self.project_token = ''
        self.system_token = ''

        self.use_project_token = False
        self.assembly = assembly
        self.ChangeUrl()

    def login(self, userName=username, passWord=password, userDomainName=user_domain_name, projectName=project_name,
              request=None):
        self.req_base_url = EASYSTACCK_KEYSTONE_HOST
        if STACK_TYPE == 'OPENSTACK':
            return self.openstack_login(userName=userName, passWord=passWord, userDomainName=userDomainName,
                                        projectName=projectName, request=request)
        else:
            self.easystack_get_keystone_session(userName=userName, passWord=passWord, userDomainName=userDomainName,
                                                projectName=projectName, request=request)
            return self.easystack_get_project_session(userName=userName, passWord=passWord,
                                                      userDomainName=userDomainName,
                                                      projectName=projectName, request=request)

    def easystack_get_keystone_session(self, userName=None, passWord=None, userDomainName=None, projectName=None,
                                       request=None, ):
        """获取Token

        :return:
        """

        Keystone_url = EASYSTACCK_KEYSTONE_HOST + "/v3/auth/tokens"
        JUDGE_URL_login = JUDGE_URL + "/v3/auth/tokens"
        # 获取keystone token

        _auth = {"auth": {"identity": {"methods": ["password"], "password": {
            "user": {"name": username if userName is None else userName,
                     "domain": {"name": user_domain_name if userDomainName is None else userDomainName},
                     "password": password if passWord is None else passWord}}},
                          "scope": {
                              "domain": {"name": user_domain_name if userDomainName is None else userDomainName}}}}
        headers = {'Content-Type': "application/json", 'X-Openstack-Nova-API-Version': "2.64"}
        if JUDGE:
            if request:
                headers['backend'] = Keystone_url
                headers['sid'] = sid_detail(request.META.get("HTTP_SID"), url=Keystone_url)
                headers['Mimic-Host'] = request.META.get("HTTP_MIMIC_HOST")
                headers['Server-Array'] = request.META.get("HTTP_SERVER_ARRAY")
                headers['msgid'] = request.META.get("HTTP_MSGID") if request.META.get("HTTP_MSGID") else ''
                headers['Req-Info'] = request.META.get("HTTP_REQ_INFO")

            else:
                headers['backend'] = Keystone_url
                headers['sid'] = 'system'
                headers['Mimic-Host'] = ''
                headers['Server-Array'] = ''
                headers['msgid'] = 'system'
                headers['Req-Info'] = ''

        try:
            login_response = self.req.post(JUDGE_URL_login if JUDGE else Keystone_url, data=json.dumps(_auth),
                                           headers=headers)
            logger.info("获取keystone token" + "method: POST - URL: {url} - CODE: {code}".format(
                url=Keystone_url + '---' + JUDGE_URL_login if JUDGE else Keystone_url,
                code=login_response.status_code))
        except Exception as e:
            raise ValueError("Login Error: {}".format(str(e)))

        response_data = json.loads(login_response.content.decode())
        logger.info('easystack_get_keystone_session keystone login result' + login_response.content.decode())
        # 登陆失败
        if 'error' in response_data:
            return False, None
        self.req.close()
        headers['X-Auth-Token'] = login_response.headers.get('X-Subject-Token')
        self.req.close()
        # # 登录成功
        print('request',request)

        if request:
            request.session['token'] = login_response.headers.get('X-Subject-Token')
            request.session['roles'] = response_data['token']['roles']
            request.session['domain'] = response_data['token']['domain']
            request.session['user'] = response_data['token']['user']
            request.session['login_info'] = {
                'userName': userName,
                'passWord': passWord,
                'userDomainName': userDomainName,
                'projectName': projectName
            }

        else:
            logger.info('系统Keystone登录成功：' + login_response.headers.get('X-Subject-Token'))
            self.keystone_token = login_response.headers.get('X-Subject-Token')
            if self.use_project_token == False:
                self.system_token = self.keystone_token

    def easystack_get_project_session(self, userName=None, passWord=None, userDomainName=None, projectName=None,
                                      request=None, ):
        """获取Token

        :return:
        """
        Keystone_url = EASYSTACCK_KEYSTONE_HOST + "/v3/auth/tokens"
        JUDGE_URL_login = JUDGE_URL + "/v3/auth/tokens"

        # 获取项目token
        _auth = {"auth": {"identity": {"methods": ["password"], "password": {
            "user": {"name": username if userName is None else userName,
                     "domain": {"name": user_domain_name if userDomainName is None else userDomainName},
                     "password": password if passWord is None else passWord}}},
                          "scope": {"project": {
                              "domain": {"name": user_domain_name if userDomainName is None else userDomainName},
                              "name": project_name if projectName is None else projectName
                          }}}}
        headers = {'Content-Type': "application/json", 'X-Openstack-Nova-API-Version': "2.64"}
        if JUDGE:
            if request:
                headers['backend'] = Keystone_url
                headers['sid'] = sid_detail(request.META.get("HTTP_SID"), url=Keystone_url)
                headers['Mimic-Host'] = request.META.get("HTTP_MIMIC_HOST")
                headers['Server-Array'] = request.META.get("HTTP_SERVER_ARRAY")
                headers['msgid'] = request.META.get("HTTP_MSGID") if request.META.get("HTTP_MSGID") else ''
                headers['Req-Info'] = request.META.get("HTTP_REQ_INFO")
            else:
                headers['backend'] = Keystone_url
                headers['sid'] = 'system'
                headers['Mimic-Host'] = ''
                headers['Server-Array'] = ''
                headers['msgid'] = 'system'
                headers['Req-Info'] = ''
        try:
            login_response = self.req.post(JUDGE_URL_login if JUDGE else Keystone_url, data=json.dumps(_auth),
                                           headers=headers)
            logger.info("获取项目 token" + "method: POST - URL: {url} - CODE: {code}".format(
                url=Keystone_url + '---' + JUDGE_URL_login if JUDGE else Keystone_url,
                code=login_response.status_code))

        except Exception as e:
            raise ValueError("Login Error: {}".format(str(e)))
        response_data = json.loads(login_response.content.decode())

        self.req.close()
        logger.info("login result:" + json.dumps(response_data))
        # 登陆失败
        logger.info('easystack_get_project_session project login result' + login_response.content.decode())
        self.req.close()
        # 登陆失败
        logger.info("login result:" + json.dumps(response_data))
        if 'error' in response_data:
            return False, None
        self.req.close()
        # 登录成功

        if request:
            request.session['project_token'] = login_response.headers.get('X-Subject-Token')
            request.session['roles'] = response_data['token']['roles']
            request.session['domain'] = response_data['token']['user']['domain']
            request.session['user'] = response_data['token']['user']
            request.session['project'] = response_data['token']['project']
            request.session['login_info'] = {
                'userName': userName,
                'passWord': passWord,
                'userDomainName': userDomainName,
                'projectName': projectName
            }
            return True, response_data['token']['user']
        else:
            self.project_token = login_response.headers.get('X-Subject-Token')

            if self.use_project_token:
                self.system_token = self.project_token

    def openstack_login(self, userName=None, passWord=None, userDomainName=None, projectName=None, request=None ):
        """获取Token

        :return:
        """

        Keystone_url = EASYSTACCK_KEYSTONE_HOST + "/v3/auth/tokens"
        JUDGE_URL_login = JUDGE_URL + "/v3/auth/tokens"
        _auth = {"auth": {"identity": {"methods": ["password"], "password": {
            "user": {"name": username if userName is None else userName,
                     "domain": {"name": user_domain_name if userDomainName is None else userDomainName},
                     "password": password if passWord is None else passWord}}}}}

        headers = {'Content-Type': "application/json", 'X-Openstack-Nova-API-Version': "2.64"}

        logger.info("login data:" + json.dumps(_auth))
        try:
            login_response = self.req.post(JUDGE_URL_login if JUDGE else Keystone_url, data=json.dumps(_auth),
                                           headers=headers)
            logger.info("method: POST - URL: {url} - CODE: {code}".format(
                url=Keystone_url + '---' + JUDGE_URL_login if JUDGE else Keystone_url,
                code=login_response.status_code))

        except Exception as e:
            raise ValueError("Login Error: {}".format(str(e)))
        self.req.close()
        response_data = json.loads(login_response.content.decode())

        print('response_data', response_data)
        # 登陆失败
        if 'error' in response_data:
            if request:
                return False, None
            else:
                logging.error(response_data)
                raise exceptions.KeyStoneApiError('系统登录出错')
        self.req.close()
        # 登录成功
        if request:
            print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$', login_response.headers.get('X-Subject-Token'))
            request.session['project_token'] = login_response.headers.get('X-Subject-Token')
            request.session['token'] = login_response.headers.get('X-Subject-Token')
            request.session['roles'] = response_data['token']['roles']
            request.session['domain'] = response_data['token']['user']['domain']
            request.session['user'] = response_data['token']['user']
            request.session['project'] = response_data['token']['project']
            request.session['login_info'] = {
                'userName': userName,
                'passWord': passWord,
                'userDomainName': userDomainName,
                'projectName': projectName
            }
            return True, response_data['token']['user']
        else:
            # headers['X-Auth-Token'] = login_response.headers.get('X-Subject-Token')
            self.keystone_token = login_response.headers.get('X-Subject-Token')
            self.project_token = self.keystone_token
            self.system_token = self.keystone_token

    def ChangeUrl(self, assembly=None):
        """
        根据传入的节点名称，修改节点路由和请求头的token
        :param URL_BASH: Nova、Image、Neutron、Cinder   为None默认为Keystone
        :return:
        """
        if assembly != None:
            self.assembly = assembly
        if self.assembly == "Nova":
            self.use_project_token = True
            self.system_token = self.project_token
            self.req_base_url = EASYSTACCK_NOVA_HOST
        elif self.assembly == 'Image':
            self.use_project_token = False
            self.system_token = self.keystone_token
            self.req_base_url = EASYSTACCK_GLANCE_HOST
        elif self.assembly == 'Neutron':
            self.use_project_token = False
            self.system_token = self.keystone_token
            self.req_base_url = EASYSTACCK_NEUTRON_HOST
        elif self.assembly == 'Cinder':
            self.use_project_token = True
            self.system_token = self.project_token
            self.req_base_url = EASYSTACCK_CINDER_HOST
        elif self.assembly == 'Octavia':
            self.use_project_token = False
            self.system_token = self.keystone_token
            self.req_base_url = EASYSTACCK_0CTAVIA_HOST
        else:
            self.use_project_token = False
            self.system_token = self.keystone_token
            self.req_base_url = EASYSTACCK_KEYSTONE_HOST

    def get(self, url, request=None, **kwargs):
        """
        get 方法请求openstack
        """
        print('get url ----->', url)
        headers = {'Content-Type': "application/json", 'X-Openstack-Nova-API-Version': "2.64"}
        if request:
            headers['X-Auth-Token'] = request.session.get(
                'project_token') if self.use_project_token else request.session.get('token')
        else:
            # TODO 使用system_token有鉴权风险，会导致未传入requst的用户也可以获取数据
            headers['X-Auth-Token'] = self.system_token

        url = url.lstrip('/') if url.startswith('/') else url.rstrip('/')
        if JUDGE:
            headers['backend'] = self.req_base_url + url
            if request:
                headers['sid'] = sid_detail(request.META.get("HTTP_SID"), url=url)
                headers['Mimic-Host'] = request.META.get("HTTP_MIMIC_HOST")
                headers['Server-Array'] = request.META.get("HTTP_SERVER_ARRAY")
                headers['msgid'] = request.META.get("HTTP_MSGID") if request.META.get("HTTP_MSGID") else ''
                headers['Req-Info'] = request.META.get("HTTP_REQ_INFO")
            else:
                headers['sid'] = 'system'
                headers['Mimic-Host'] = ''
                headers['Server-Array'] = ''
                headers['msgid'] = 'system'
                headers['Req-Info'] = ''
            logger.info(f"method: GET - URL: {JUDGE_URL+url} - SID: {headers['sid']}")

        res = self.req.get(JUDGE_URL if JUDGE else self.req_base_url + url, headers=headers)
        print('get request------------->', JUDGE_URL if JUDGE else self.req_base_url + url)
        print('get result ------------>', res)
        self.req.close()
        logger.info(f"method: GET - URL: {JUDGE_URL if JUDGE else self.req_base_url}/{url} - CODE: {res.status_code}")
        if res.status_code == 200:
            result = res.json()

            return result
        else:
            code_object = ResponseCode(res)
            code_object()

    def put(self, url, data=None, request=None, isJson=True, **kwargs):
        """
        使用PUT方法请求openstack api接口
        """
        print('put url ----->', url)
        headers = {'Content-Type': "application/json", 'X-Openstack-Nova-API-Version': "2.64"}
        if request:
            headers['X-Auth-Token'] = request.session.get(
                'project_token') if self.use_project_token else request.session.get('token')
        else:
            # TODO 使用system_token有鉴权风险，会导致未传入requst的用户也可以获取数据
            headers['X-Auth-Token'] = self.system_token

        url = url.lstrip('/') if url.startswith('/') else url.rstrip('/')
        headers['Accept-Charset'] = 'utf-8'
        if JUDGE:
            headers['backend'] = self.req_base_url + url
            if request:
                headers['sid'] = sid_detail(request.META.get("HTTP_SID"), url=url)
                headers['Mimic-Host'] = request.META.get("HTTP_MIMIC_HOST")
                headers['Server-Array'] = request.META.get("HTTP_SERVER_ARRAY")
                headers['msgid'] = request.META.get("HTTP_MSGID") if request.META.get("HTTP_MSGID") else ''
                headers['Req-Info'] = request.META.get("HTTP_REQ_INFO")
            else:
                headers['sid'] = 'system'
                headers['Mimic-Host'] = ''
                headers['Server-Array'] = ''
                headers['msgid'] = 'system'
                headers['Req-Info'] = ''
            logger.info(f"method: PUT - URL: {JUDGE_URL+url} - SID: {headers['sid']}")

        if kwargs.get("headers", None):
            headers.update(kwargs['headers'])

        print(JUDGE_URL if JUDGE else self.req_base_url + url)
        if data:
            if isJson:
                res = self.req.put(JUDGE_URL if JUDGE else self.req_base_url + url, headers=headers,
                                   data=json.dumps(data))
                logger.info(
                    f"method: PUT - URL: {JUDGE_URL if JUDGE else self.req_base_url}/{url} - CODE: {res.status_code} - {json.dumps(data)}")
            else:
                res = self.req.put(JUDGE_URL if JUDGE else self.req_base_url + url, headers=headers, data=data)
                logger.info(
                    f"method: PUT - URL: {JUDGE_URL if JUDGE else self.req_base_url}/{url} - CODE: {res.status_code} - {data}")
        else:
            res = self.req.put(JUDGE_URL if JUDGE else self.req_base_url + url, headers=headers)
            logger.info(
                f"method: PUT - URL: {JUDGE_URL if JUDGE else self.req_base_url}/{url} - CODE: {res.status_code} - ")
        self.req.close()

        if res.status_code in [200, 201]:
            return res.json()
        elif res.status_code in [204, 415]:
            return res.status_code
        else:
            code_object = ResponseCode(res)
            code_object()

    def post(self, url, data=None, request=None, headers=None):
        """
        POST 方法请求openstak api接口
        """
        print('post url ----->', url)
        if not headers:
            headers = {'Content-Type': "application/json", 'X-Openstack-Nova-API-Version': "2.64"}
        else:
            # TODO 使用system_token有鉴权风险，会导致未传入requst的用户也可以获取数据
            headers = headers

        url = url.lstrip('/') if url.startswith('/') else url.rstrip('/')
        if request:
            headers['X-Auth-Token'] = request.session.get(
                'project_token') if self.use_project_token else request.session.get('token')
        else:
            # TODO 使用system_token有鉴权风险，会导致未传入requst的用户也可以获取数据
            headers['X-Auth-Token'] = self.system_token

        if JUDGE:
            headers['backend'] = self.req_base_url + url
            if request:
                headers['sid'] = sid_detail(request.META.get("HTTP_SID"), url=url)
                headers['Mimic-Host'] = request.META.get("HTTP_MIMIC_HOST")
                headers['Server-Array'] = request.META.get("HTTP_SERVER_ARRAY")
                headers['msgid'] = request.META.get("HTTP_MSGID") if request.META.get("HTTP_MSGID") else ''
                headers['Req-Info'] = request.META.get("HTTP_REQ_INFO")
            else:
                headers['sid'] = 'system'
                headers['Mimic-Host'] = ''
                headers['Server-Array'] = ''
                headers['msgid'] = 'system'
                headers['Req-Info'] = ''
            logger.info(f"method: POST - URL: {JUDGE_URL+url} - SID: {headers['sid']}")

        res = self.req.post(JUDGE_URL if JUDGE else self.req_base_url + url, headers=headers, json=data)
        logger.info(
            f"method: POST - URL: {JUDGE_URL if JUDGE else self.req_base_url} - CODE: {res.status_code} - {json.dumps(data)}")
        self.req.close()

        if res.status_code in [200, 201, 202]:
            try:
                result = res.json()
            except Exception:
                result = {}
            return result
        else:
            code_object = ResponseCode(res)
            code_object()

    def delete(self, url, data=None, request=None, **kwargs):
        """
        delete 方法请求openstack api接口
        """
        print('delete url ----->', url, self.req_base_url + url)
        headers = {'Content-Type': "application/json", 'X-Openstack-Nova-API-Version': "2.64"}

        if request:
            headers['X-Auth-Token'] = request.session.get(
                'project_token') if self.use_project_token else request.session.get('token')
        else:
            # TODO 使用system_token有鉴权风险，会导致未传入requst的用户也可以获取数据
            headers['X-Auth-Token'] = self.system_token

        url = url.lstrip('/') if url.startswith('/') else url.rstrip('/')
        if JUDGE:
            headers['backend'] = self.req_base_url + url
            if request:
                headers['sid'] = sid_detail(request.META.get("HTTP_SID"), url=url)
                headers['Mimic-Host'] = request.META.get("HTTP_MIMIC_HOST")
                headers['Server-Array'] = request.META.get("HTTP_SERVER_ARRAY")
                headers['msgid'] = request.META.get("HTTP_MSGID") if request.META.get("HTTP_MSGID") else ''
                headers['Req-Info'] = request.META.get("HTTP_REQ_INFO")
            else:
                headers['sid'] = 'system'
                headers['Mimic-Host'] = ''
                headers['Server-Array'] = ''
                headers['msgid'] = 'system'
                headers['Req-Info'] = ''
            logger.info(f"method: DELETE - URL: {JUDGE_URL + url} - SID: {headers['sid']}")
        print(headers)
        print('data', data)
        if data:

            res = self.req.delete(JUDGE_URL if JUDGE else self.req_base_url + url, headers=headers,
                                  data=json.dumps(data))
            logger.info(
                f"method: DELETE - URL: {JUDGE_URL if JUDGE else self.req_base_url}/{url} - CODE: {res.status_code} - {json.dumps(data)}")
        else:

            res = self.req.delete(JUDGE_URL if JUDGE else self.req_base_url + url, headers=headers)
            logger.info(
                f"method: DELETE - URL: {JUDGE_URL if JUDGE else self.req_base_url}/{url} - CODE: {res.status_code} - ")
        self.req.close()

        if res.status_code == 204:
            return res.status_code
        else:
            code_object = ResponseCode(res)
            code_object()

    def patch(self, url, data=None, request=None, **kwargs):
        """
        patch 方法请求openstack api接口
        """
        print('patch url ----->', url)
        headers = {'Content-Type': "application/json", 'X-Openstack-Nova-API-Version': "2.64"}
        if request:
            headers['X-Auth-Token'] = request.session.get(
                'project_token') if self.use_project_token else request.session.get('token')
        else:
            # TODO 使用system_token有鉴权风险，会导致未传入requst的用户也可以获取数据
            headers['X-Auth-Token'] = self.system_token

        url = url.lstrip('/') if url.startswith('/') else url.rstrip('/')
        if JUDGE:
            headers['backend'] = self.req_base_url + url
            if request:
                headers['sid'] = sid_detail(request.META.get("HTTP_SID"), url=url)
                headers['Mimic-Host'] = request.META.get("HTTP_MIMIC_HOST")
                headers['Server-Array'] = request.META.get("HTTP_SERVER_ARRAY")
                headers['msgid'] = request.META.get("HTTP_MSGID") if request.META.get("HTTP_MSGID") else ''
                headers['Req-Info'] = request.META.get("HTTP_REQ_INFO")
            else:
                headers['sid'] = 'system'
                headers['Mimic-Host'] = ''
                headers['Server-Array'] = ''
                headers['msgid'] = 'system'
                headers['Req-Info'] = ''
            logger.info(f"method: PATCH - URL: {JUDGE_URL + url} - SID: {headers['sid']}")

        if kwargs.get("headers", None):
            headers.update(kwargs['headers'])

        if data:

            res = self.req.patch(JUDGE_URL if JUDGE else self.req_base_url + url, headers=headers,
                                 data=json.dumps(data))
            logger.info(
                f"method: PATCH - URL: {JUDGE_URL if JUDGE else self.req_base_url}/{url} - CODE: {res.status_code} - {json.dumps(data)}")
        else:
            res = self.req.patch(JUDGE_URL if JUDGE else self.req_base_url + url, headers=headers)
            logger.info(
                f"method: PATCH - URL: {JUDGE_URL if JUDGE else self.req_base_url} - CODE: {res.status_code} - ")

        self.req.close()

        if res.status_code == 200:
            return res.json()
        else:
            code_object = ResponseCode(res)
            code_object()

StackApi = StackApi()