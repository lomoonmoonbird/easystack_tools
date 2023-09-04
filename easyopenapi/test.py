from easyopenapi.stack_request import StackApi

if __name__ == '__main__':
    api = StackApi()
    res = api.openstack_login(userName='admin', passWord='123456',userDomainName='default',projectName='mx-im')
    print(res)
    api.ChangeUrl('Image')
    print(api.req_base_url)
    r = api.delete('v2/images/e24d95aa-9679-4adf-9b31-534dcea588f0/tags/image_type')
    print(r)