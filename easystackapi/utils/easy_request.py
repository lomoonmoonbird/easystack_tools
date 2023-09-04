# -*- coding: utf-8 -*-
import json
import os
from pprint import pprint

import requests
import sys
from easystackapi.utils.commonvariable import EASYSTACCK_KEYSTONE_HOST, EASYSTACCK_NOVA_HOST, EASYSTACCK_GLANCE_HOST, \
    EASYSTACCK_CINDER_HOST, EASYSTACCK_NEUTRON_HOST, username, user_domain_name, password, tenant_id, project_name
from mcloud_v1.exceptions import NotAuthorized
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

'''
封装请求easy stack api 的方法
'''


class EasyStackApi(object):
    '''
    调用EasyStackApi专用类
    '''

    def __init__(self):
        self.req = requests.session()
        self.get_session()
        self.req_base_url = EASYSTACCK_KEYSTONE_HOST

    def get_session(self):
        self._get_sessin()

    def __call__(self, url, method="GET", URL_BASH=None, data=None, **kwargs):
        self.get_session()
        if URL_BASH:
            if URL_BASH == "Nova":
                self.req_base_url = EASYSTACCK_NOVA_HOST
            elif URL_BASH == 'Image':
                self.req_base_url = EASYSTACCK_GLANCE_HOST
            elif URL_BASH == 'Neutron':
                self.req_base_url = EASYSTACCK_NEUTRON_HOST
            elif URL_BASH == 'Cinder':
                self.req_base_url = EASYSTACCK_CINDER_HOST
            else:
                raise TypeError("Args: 组件不存在")
        else:
            self.req_base_url = EASYSTACCK_KEYSTONE_HOST

        handler = getattr(self, method.lower())
        return handler(url, data=data, **kwargs)


    def _get_sessin(self,request=None,usn=None,psd=None,udn=None):
        """获取Token

        :return:
        """
        Keystone_url = EASYSTACCK_KEYSTONE_HOST + "/v3/auth/tokens"

        _auth = {"auth": {"identity": {"methods": ["password"], "password": {
            "user": {"name": username if usn is None else usn, "domain": {"name": user_domain_name if udn is None else udn}, "password": password if psd is None else psd}}},
                          "scope": {"domain": {"name": user_domain_name if udn is None else udn}}}}

        try:
            login_response = self.req.post(Keystone_url, data=json.dumps(_auth),
                                           headers={'Content-Type': "application/json"})
        except Exception as e:
            raise ValueError("Login Error: {}".format(str(e)))

        response_data = json.loads(login_response.content.decode())

        # 登陆失败
        if 'error' in response_data:
            return False

        # 登录成功
        if request:
            request.session['token'] = login_response.headers.get('X-Subject-Token')
            request.session['roles'] = response_data['token']['roles']
            request.session['domain'] = response_data['token']['domain']
            request.session['user'] = response_data['token']['user']
            return True
        else:
            self.headers = {'Content-Type': "application/json",
                        'X-Auth-Token': login_response.headers.get('X-Subject-Token')}

            return None

    def _get_project_sessin(self,request=None,usn=None,psd=None,udn=None,pjn=None):
        """获取Token

        :return:
        """

        Keystone_url = EASYSTACCK_KEYSTONE_HOST + "/v3/auth/tokens"

        _auth = {"auth": {"identity": {"methods": ["password"], "password": {
            "user": {"name": username if usn is None else usn, "domain": {"name": user_domain_name if udn is None else udn}, "password": password if psd is None else psd}}},
                          "scope": {"project": {"domain": {"name": user_domain_name if udn is None else udn},
                                                "name": project_name if pjn is None else pjn
                                                }}}}
        try:
            login_response = self.req.post(Keystone_url, data=json.dumps(_auth),
                                           headers={'Content-Type': "application/json"})
        except Exception as e:
            raise ValueError("Login Error: {}".format(str(e)))

        response_data = json.loads(login_response.content.decode())
        # 登陆失败
        if 'error' in response_data:
            return False
        # 登录成功
        if request:
            request.session['token'] = login_response.headers.get('X-Subject-Token')
            return True
        else:
            self.headers = {'Content-Type': "application/json",
                            'X-Auth-Token': login_response.headers.get('X-Subject-Token')}
            return None

    def ChangeUrl(self, URL_BASH=None):
        """
        根据传入的节点名称，修改节点路由和请求头的token
        :param URL_BASH: Nova、Image、Neutron、Cinder   为None默认为Keystone
        :return:
        """
        if URL_BASH:
            if URL_BASH == "Nova":
                self._get_project_sessin()
                self.req_base_url = EASYSTACCK_NOVA_HOST
            elif URL_BASH == 'Image':
                self.get_session()
                self.req_base_url = EASYSTACCK_GLANCE_HOST
            elif URL_BASH == 'Neutron':
                self.get_session()
                self.req_base_url = EASYSTACCK_NEUTRON_HOST
            elif URL_BASH == 'Cinder':
                self._get_project_sessin()
                self.req_base_url = EASYSTACCK_CINDER_HOST
            else:
                raise TypeError("Args: 组件不存在")

        else:
            self.get_session()
            self.req_base_url = EASYSTACCK_KEYSTONE_HOST

    def get(self, url,request=None, **kwargs):
        if request:
            self.headers = {'Content-Type': "application/json",
                        'X-Auth-Token': request.session.get('token')}
        res = self.req.get(self.req_base_url + url, headers=self.headers)
        if res.status_code == 401:
            raise NotAuthorized('未授权或授权已失效')
        try:
            result = res.json()
        except Exception as e:
            result = res.content.decode()
        return result, res.status_code

    def put(self, url, data=None,request=None,isJson=True, **kwargs):
        if request:
            self.headers = {'Content-Type': "application/json",
                        'X-Auth-Token': request.session.get('token')}
        if kwargs.get("headers", None):
            self.headers.update(kwargs['headers'])
        if data:
            if isJson:
                res = self.req.put(self.req_base_url + url, headers=self.headers, data=json.dumps(data))
            else:
                res = self.req.put(self.req_base_url + url, headers=self.headers, data=data)

        else:
            res = self.req.put(self.req_base_url + url, headers=self.headers)
        if res.status_code == 401:
            raise NotAuthorized('未授权或授权已失效')
        try:
            result = res.json()
        except Exception as e:
            result = res.content.decode()
        return result, res.status_code

    def post(self, url, data=None, request=None,**kwargs):
        if request:
            self.headers = {'Content-Type': "application/json",
                        'X-Auth-Token': request.session.get('token')}
        res = self.req.post(self.req_base_url + url, headers=self.headers, data=json.dumps(data))
        if res.status_code == 401:
            raise NotAuthorized('未授权或授权已失效')
        try:
            result = res.json()
        except Exception as e:
            result = res.content.decode()
        return result, res.status_code

    def delete(self, url, data=None, request=None,**kwargs):
        if request:
            self.headers = {'Content-Type': "application/json",
                        'X-Auth-Token': request.session.get('token')}
        if data:
            res = self.req.delete(self.req_base_url + url, headers=self.headers, data=json.dumps(data))
        else:
            res = self.req.delete(self.req_base_url + url, headers=self.headers)
        if res.status_code == 401:
            raise NotAuthorized('未授权或授权已失效')
        try:
            result = res.json()
        except Exception as e:
            result = res.content.decode()
        return result, res.status_code

    def patch(self, url, data=None, request=None,**kwargs):
        if request:
            self.headers = {'Content-Type': "application/json",
                        'X-Auth-Token': request.session.get('token')}
        if data:
            res = self.req.patch(self.req_base_url + url, headers=self.headers, data=json.dumps(data))
        else:
            res = self.req.patch(self.req_base_url + url, headers=self.headers)
        if res.status_code == 401:
            raise NotAuthorized('未授权或授权已失效')
        try:
            result = res.json()
        except Exception as e:
            result = res.content.decode()
        return result, res.status_code


easystack_api = EasyStackApi()

if __name__ == '__main__':
    # 获取domain
    ret, code = easystack_api.get('/v3/domains')
    # =======================================镜像相关===========================================
    # 修改路由到glance host
    easystack_api.ChangeUrl('Image')
    # 获取images列表
    ret = easystack_api.get('/v2/images')
    for i in ret['images']:
        if i['name'] == 'test_image_':
            result,code = easystack_api.delete('/v2/images/' + i['id'])
    #         # # 镜像打tag
    # print('镜像打tag', '=' * 20)
    # ret, code = easystack_api.put('/v2/images/a70b2015-227f-4546-9b73-5c615ed7b73e/tags/'+'image_type:dd')
    # print(ret)

    # 获取image详情
    # print('获取image详情', '=' * 20)
    # ret, code = easystack_api.get('/v2/images/a70b2015-227f-4546-9b73-5c615ed7b73e')
    # ret, code = easystack_api.get('/v2/images/de679b30-72f4-460a-a21e-e8ff61c4009a')
    # pprint(ret)
    #
    # # 删除镜像的tags
    # # print('删除镜像的tags', '=' * 20)
    # # ret, code = easystack_api.delete('/v2/images/a70b2015-227f-4546-9b73-5c615ed7b73e/tags/test_tag')
    # # print(ret)
    #
    # # 获取image详情
    # print('获取image详情', '=' * 20)
    # ret, code = easystack_api.get('/v2/images/a70b2015-227f-4546-9b73-5c615ed7b73e')
    # print(ret)
    # ===================================  虚拟机相关===================================
    # # 获取虚机列表
    # print('获取虚机列表', '=' * 20)
    # easystack_api.ChangeUrl('Nova')
    # ret, code = easystack_api.get('/v2.0/servers')
    # pprint(ret)
    #
    # # 获取云盘列表
    # print('获取云盘列表', '=' * 20)
    # easystack_api.ChangeUrl('Neutron')
    # ret, code = easystack_api.get('/v2.0/networks')
    # print(ret)

# curl -i -X POST http://keystone.openstack.svc.cluster.local/v3/auth/tokens -H "Content-type: application/json" -d '{"auth": {"identity": {"methods": ["password"],"password": {"user":{"id": "0928b1ec64544a378d37ab7d6437de37","password": "Admin@ES20!8"}}}, "scope": {"domain": {"id": "default"}}}}'|grep X-Subject-Token
# curl -i -X POST http://keystone.openstack.svc.cluster.local/v3/auth/tokens -H "Content-type: application/json" -d '{"auth": {"identity": {"methods": ["password"],"password": {"user":{"name": "admin","password": "Admin@ES20!8"}}}, "scope": {"domain": {"id": "default"}}}}'|grep X-Subject-Token
# curl -i -X POST http://keystone.openstack.svc.cluster.local/v3/auth/tokens -H "Content-type: application/json" -d '{"auth": {"identity": {"methods": ["password"],"password": {"user":{"email": "admin@example.org","password": "Admin@ES20!8"}}}, "scope": {"domain": {"name": "default"}}}}'|grep X-Subject-Token
