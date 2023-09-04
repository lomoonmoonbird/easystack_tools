import socket
import struct
import sys
import traceback
from pprint import pprint

# from easystackapi.utils.easy_request import easystack_api
from easyopenapi.stack_request import StackApi
from easyopenapi.defaults import username, password, project_domain_name
easystack_api = StackApi

from easystackapi.utils.commonvariable import project_id, default_network_type, tenant_id
import exceptions

Version = '2.0'
# '10.10.0.32'- '10.10.255.224'
Cidr = [i for i in range(168427552, 168493024, 32)]
Cidr_index = 0


def get_networks(request=None):
    easystack_api.ChangeUrl('Neutron')
    networks = easystack_api.get('/v2.0/networks', request=request)
    return networks['networks']


def get_network_byname(network_name, request=None):
    # from easyopenapi.defaults import username, password, project_domain_name
    # easystack_api.login(userName=username,passWord=password, projectName=project_domain_name)
    # easystack_api.ChangeUrl('Neutron')
    print('network name -->', network_name)
    easystack_api.ChangeUrl('Neutron')
    network = easystack_api.get('/v2.0/networks', request=request)
    print('networknetworknetworknetworknetworknetworknetworknetwork', network)
    for net in network['networks']:
        if net['name'] == network_name:
            return net
    return None


def create_network(network_name, projectid=project_id, network_type=default_network_type, request=None):
    # 创建网络， project_id， project_id都是默认的，在那个域和project下认证，就会默认在那个域下创建网络，网络类型也是neutron配置的网络类型，可以不写,segmentation_id也可以不写，随机分配
    # network = {'name': network_name, 'admin_state_up': True, 'project_id': projectid,'provider:network_type': 'vxlan','provider:segmentation_id': id}

    easystack_api.ChangeUrl('Neutron')
    # 判断网络名称是否存在
    network_info = get_network_byname(network_name, request=request)
    if not network_info:
        network_param = {
            "network": {
                "name": network_name,
                "admin_state_up": True,
                "project_id": projectid,
                "provider:network_type": network_type,
            }
        }

        try:
            network = easystack_api.post('/v2.0/networks', data=network_param, request=request)
            return network['network']
        except:
            raise exceptions.CreateMimicError('网络创建失败：请求失败')
    else:
        return network_info
        # raise exceptions.CreateMimicError('网络创建失败:网络名{}已存在'.format(network_name))


def delete_network(network_name, request=None):
    easystack_api.ChangeUrl('Neutron')
    network_info = get_network_byname(network_name, request=request)
    if not network_info == 0:
        return
    network_id = network_info['networks'][0]['id']
    network = easystack_api.delete('/v2.0/networks/' + network_id, request=request)
    return network_info


def int_to_ip_address(int_ip):
    ip = socket.inet_ntoa(struct.pack('I', socket.htonl(int_ip)))
    return ip


def create_networkwithsubnet(network_name, subnetname, projectid=project_id, network_type=default_network_type, request=None):
    # 创建网络， project_id， project_id都是默认的，在那个域和project下认证，就会默认在那个域下创建网络，网络类型也是neutron配置的网络类型，可以不写,segmentation_id也可以不写，随机分配
    # network = {'name': network_name, 'admin_state_up': True, 'project_id': projectid,'provider:network_type': 'vxlan','provider:segmentation_id': id}
    easystack_api.ChangeUrl('Neutron')
    network_info = create_network(network_name, projectid, network_type, request=request)

    if type(network_info) is str:
        return network_info

    network_id = network_info['network']['id']

    # 同一租户下的网络是不能重叠的，一个网络对应一个子网，通过子网来隔离Pass应用
    # a = random.randint(2, 254)   #有可能会重叠
    global Cidr_index
    a = Cidr[Cidr_index]
    ip = int_to_ip_address(a)
    cidr = ip + '/27'
    gateway_ip = int_to_ip_address(a + 1)
    subnet = {
        'subnet': {'name': subnetname, 'tenant_id': tenant_id, 'network_id': network_id, 'ip_version': 4, 'cidr': cidr,
                   'gateway_ip': gateway_ip}}
    easystack_api.ChangeUrl('Neutron')
    subnet_info = easystack_api.post('/v2.0/subnets', data=subnet, request=request)
    # 子网创建失败时，删除之前创建的网络
    if type(subnet_info) is str:
        delete_network(network_name)
        return subnet_info

    Cidr_index = Cidr_index + 1
    if (Cidr_index > 2045):
        Cidr_index = 0

    subnet_id = subnet_info[0]['subnet']['id']
    return network_id, subnet_id, cidr, gateway_ip


def get_subnet_id_by_network_name(network_name, request=None):
    network_info = get_network_byname(network_name, request=request)
    if type(network_info) is str:
        return network_info

    subnets = network_info['networks'][0]['subnets']
    if len(subnets) == 0:
        return subnets
    return subnets[0]


def listfirtstrouterid(request=None):
    # 获取第一条路由信息s
    easystack_api.ChangeUrl('Neutron')
    routerlist = easystack_api.get('/v2.0/routers', request=request)
    router_id = routerlist[0]['routers'][0]['id']
    return router_id

def create_router(name,network_id, request=None):
    # 获取第一条路由信息s
    easystack_api.ChangeUrl('Neutron')
    data = {
        "router": {
            "name": name,
            "tenant_id":tenant_id,
            "admin_state_up": True,
            "external_gateway_info": {
                "network_id": network_id,
                "enable_snat": True,
            },

        }
    }
    router = easystack_api.post(url='/v2.0/routers',data=data, request=request)
    router_id = router['router']['id']
    return router_id

def delete_router(router_id, request=None):
    # 获取第一条路由信息s
    easystack_api.ChangeUrl('Neutron')
    url = '/v2.0/routers/' + router_id
    try:
        code = easystack_api.delete(url, request=request)
        if code < 300:
            return True
    except:
        raise exceptions.CreateMimicError('router删除失败{}'.format(router_id))

def delete_network_by_id(network_id, request=None):
    # 获取第一条路由信息s
    easystack_api.ChangeUrl('Neutron')
    url = '/v2.0/networks/' + network_id
    try:
        code = easystack_api.delete(url, request=request)
        if code < 300:
            return True
    except:
        raise exceptions.CreateMimicError('networks删除失败{}'.format(network_id))




def add_interface_router(route_id, subnet_id, request=None):
    # 获取第一条路由信息
    easystack_api.ChangeUrl('Neutron')
    data = {"subnet_id": subnet_id}
    url = '/v2.0/routers/' + route_id + '/add_router_interface'
    interface_router = easystack_api.put(url, data, request=request)
    pprint(interface_router)
    return interface_router


def create_networkwithsubnetrouterinterface(network_name, subnetname, route_id, projectid=project_id,
                                            network_type=default_network_type,cidr_index=0,request=None):
    # 创建网络， project_id， project_id都是默认的，在那个域和project下认证，就会默认在那个域下创建网络，网络类型也是neutron配置的网络类型，可以不写,segmentation_id也可以不写，随机分配
    # network = {'name': network_name, 'admin_state_up': True, 'project_id': projectid,'provider:network_type': 'vxlan','provider:segmentation_id': id}

    # 创建网络和子网
    network_info = get_network_byname(network_name, request=request)
    if not network_info:
        network_info = create_network(network_name, projectid, network_type, request=request)

    network_id = network_info['id']

    # 同一租户下的网络是不能重叠的，一个网络对应一个子网，通过子网来隔离Pass应用
    # a = random.randint(2, 254)   #有可能会重叠
    # global Cidr_index
    a = Cidr[cidr_index]
    ip = int_to_ip_address(a)
    cidr = ip + '/27'
    gateway_ip = int_to_ip_address(a + 1)
    subnet = {
        'subnet': {'name': subnetname, 'tenant_id': tenant_id, 'network_id': network_id, 'ip_version': 4, 'cidr': cidr,
                   'gateway_ip': gateway_ip}}
    easystack_api.ChangeUrl('Neutron')
    subnet_info = easystack_api.post('/v2.0/subnets', data=subnet, request=request)
    print("------------------>subnet_info", subnet_info)
    # 子网创建失败时，删除之前创建的网络
    if 'NeutronError' in subnet_info:
        # delete_network(network_name)
        raise exceptions.CreateMimicError('子网创建失败：' + subnet_info['NeutronError']['message'])

    # Cidr_index = Cidr_index + 1
    # if (Cidr_index > 2045):
    #     Cidr_index = 0

    subnet_id = subnet_info['subnet']['id']
    # network_id, subnet_id, cidr, gateway_ip = create_networkwithsubnet(network_name, subnetname, projectid, network_type)
    # 添加路由接口
    router_interface_info = add_interface_router(route_id, subnet_id, request=request)  # 通过路由器将vxlan子网与外网绑定
    # print(router_interface_info){'network_id': '71a6dfcc-f1e5-4ab0-b808-db967e6a4dc4', 'project_id': '949129b008c44a8facc5373bec462eae', 'subnet_id': 'ef69b409-22d5-47b0-9cd6-0dc737711ea2', 'subnet_ids': ['ef69b409-22d5-47b0-9cd6-0dc737711ea2'], 'port_id': 'b9dca8ff-407b-409c-a084-593f379eefba', 'id': 'ac76db9e-1c14-4854-bf36-be70b91bf270'}
    return network_id, subnet_id, cidr, gateway_ip, router_interface_info


def neutron_create_floatingip(externalnetworkname, portid=None, tenantid=tenant_id, floatingip=None, request=None):
    from easyopenapi.defaults import username, password, project_domain_name
    easystack_api.login(userName=username,passWord=password, projectName=project_domain_name, request=request)
    easystack_api.ChangeUrl('Neutron')
    count = 0
    while count < 10:
        try:
            print('externalnetworknameexternalnetworknameexternalnetworkname', externalnetworkname)
            network_info = get_network_byname(externalnetworkname, request=request)
            # 判断网络是否存在且网络类型为外部网络
            network_id = network_info['id']
            data = {
                "floatingip": {
                    "floating_network_id": network_id,
                    "port_id": portid,
                    "tenant_id": tenantid,
                    "description": "floating ip for create"
                }
            }

            url = '/v2.0/floatingips'
            floatingip_info = easystack_api.post(url, data, request=request)
            # if code > 300:
            #     count += 1
            #     print('floating_ip绑定失败',floatingip_info)
            # else:
            return floatingip_info
        except Exception as e:
            traceback.print_exc()
            return False
    return False
    # {'floatingip': {'router_id': 'ac76db9e-1c14-4854-bf36-be70b91bf270', 'status': 'DOWN', 'description': '', 'tags': [], 'project_id': '949129b008c44a8facc5373bec462eae', 'created_at': '2020-04-10T02:40:29Z', 'updated_at': '2020-04-10T02:40:29Z', 'floating_network_id': '41b61eba-bc91-4a92-b81b-80fdb836b7be', 'port_details': {'status': 'ACTIVE', 'name': '', 'admin_state_up': True, 'network_id': '719c0f37-3c3b-4b6c-a25b-fdb1367ad0fc', 'device_owner': 'compute:zone3', 'mac_address': 'fa:16:3e:07:9b:ca', 'device_id': '910e3144-8bbc-4d29-9365-5898c6b2d593'}, 'fixed_ip_address': '19.0.0.202', 'floating_ip_address': '172.171.19.237', 'revision_number': 0, 'project_id': '949129b008c44a8facc5373bec462eae', 'port_id': '1d359f63-f439-4110-b257-86f23d68b282', 'id': {'floatingip': {'router_id': 'ac76db9e-1c14-4854-bf36-be70b91bf270', 'status': 'DOWN', 'description': '', 'tags': [], 'project_id': '949129b008c44a8facc5373bec462eae', 'created_at': '2020-04-10T02:40:29Z', 'updated_at': '2020-04-10T02:40:29Z', 'floating_network_id': '41b61eba-bc91-4a92-b81b-80fdb836b7be', 'port_details': {'status': 'ACTIVE', 'name': '', 'admin_state_up': True, 'network_id': '719c0f37-3c3b-4b6c-a25b-fdb1367ad0fc', 'device_owner': 'compute:zone3', 'mac_address': 'fa:16:3e:07:9b:ca', 'device_id': '910e3144-8bbc-4d29-9365-5898c6b2d593'}, 'fixed_ip_address': '19.0.0.202', 'floating_ip_address': '172.171.19.237', 'revision_number': 0, 'project_id': '949129b008c44a8facc5373bec462eae', 'port_id': '1d359f63-f439-4110-b257-86f23d68b282', 'id': 'd55ee257-838c-467e-a322-5a27fef3c76c'}}
    # ['19.0.0.202']


def get_floating_ip(externalnetworkname, portid=None, tenantid=tenant_id, floatingip=None, request=None):
    floatIpInfo = neutron_create_floatingip(externalnetworkname, portid, tenantid, floatingip, request=request)
    if floatIpInfo:
        data = {'floating_ip_address': floatIpInfo['floatingip']['floating_ip_address'],
                'id': floatIpInfo['floatingip']['id']}
        return data


def neutron_delete_floatingip(floatingip_id, request=None):
    easystack_api.ChangeUrl('Neutron')

    url = '/v2.0/floatingips/' + floatingip_id
    floatingip_info = easystack_api.delete(url, request=request)
    return floatingip_info


def get_floatingipall(request=None):
    easystack_api.ChangeUrl('Neutron')
    url = '/v2.0/floatingips'
    floatingip_info, code = easystack_api.get(url, request=request)
    pprint(floatingip_info)
    return floatingip_info


def create_port(name, network_id, request=None):
    easystack_api.ChangeUrl('Neutron')
    url = '/v2.0/ports'
    data = {
        "network_id": network_id,
        "name": name,
        "admin_state_up": True
    }
    port_info, code = easystack_api.post(url, data, request=request)
    return port_info


def get_ports(request=None):
    easystack_api.ChangeUrl('Neutron')
    url = '/v2.0/ports'
    ports, code = easystack_api.get(url, request=request)
    pprint(ports)
    pprint(ports['ports'][0]['id'])
    return ports


def delete_port(port_id, request=None):
    easystack_api.ChangeUrl('Neutron')
    url = '/v2.0/ports/' + port_id
    port, code = easystack_api.delete(url, request=request)
    return port


def del_router_interface(route_id, subnet_id, request=None):
    easystack_api.ChangeUrl('Neutron')
    data = {"subnet_id": subnet_id}
    url = '/v2.0/routers/' + route_id + '/remove_router_interface'
    pprint(url)
    pprint(data)
    interface_router = easystack_api.put(url, data, request=request)
    pprint(interface_router)
    return interface_router


'''
desc: 将指定 floatingIP 绑定到指定 port,port_id 为 None 时解绑
method: put
uri: /v2.0/floatingips/{floatingip_id}
params:
    {
        "floatingip": {
            "port_id": "fc861431-0e6c-4842-a0ed-e2363f9bc3a8"
        }
    } 
resp:
    {
        "floatingip": {
            "created_at": "2016-12-21T10:55:50Z",
            "description": "floating ip for testing",
            "dns_domain": "my-domain.org.",
            "dns_name": "myfip",
            "fixed_ip_address": "10.0.0.4",
            "floating_ip_address": "172.24.4.228",
            "floating_network_id": "376da547-b977-4cfe-9cba-275c80debf57",
            "id": "2f245a7b-796b-4f26-9cf9-9e82d248fda7",
            "port_id": "fc861431-0e6c-4842-a0ed-e2363f9bc3a8",
            "project_id": "4969c491a3c74ee4af974e6d800c62de",
            "revision_number": 3,
            "router_id": "d23abc8d-2991-4a55-ba98-2aaea84cc72f",
            "status": "ACTIVE",
            "tags": ["tag1,tag2"],
            "tenant_id": "4969c491a3c74ee4af974e6d800c62de",
            "updated_at": "2016-12-22T03:13:49Z",
            "port_details": {
                "status": "ACTIVE",
                "name": "",
                "admin_state_up": true,
                "network_id": "02dd8479-ef26-4398-a102-d19d0a7b3a1f",
                "device_owner": "compute:nova",
                "mac_address": "fa:16:3e:b1:3b:30",
                "device_id": "8e3941b4-a6e9-499f-a1ac-2a4662025cba"
            },
            "port_forwardings": []
        }
    }
'''


def add_floatingip_to_port(floatingip_id, port_id=None, request=None):
    easystack_api.ChangeUrl('Neutron')
    uri = "/v2.0/floatingips/" + floatingip_id
    data = {
        "floatingip": {
            "port_id": port_id
        }
    }
    floatingip_info = easystack_api.put(uri, data, request=request)
    print('绑定浮动ip结果:', floatingip_info)
    if "floatingip" in floatingip_info:
        # TODO 数据写入数据库
        return True
    else:
        return False


'''
desc: 创建 安全组
methods: Post
uri: /v2.0/security-groups
params:
    {
        "security_group": {
            "name": "new-webservers",
            "description": "security group for webservers",
            "stateful": true
        }
    }
resp: 
{
    "security_group": {
        "description": "security group for webservers",
        "id": "2076db17-a522-4506-91de-c6dd8e837028",
        "name": "new-webservers",
        "security_group_rules": [
            {
                "direction": "egress",
                "ethertype": "IPv4",
                "id": "38ce2d8e-e8f1-48bd-83c2-d33cb9f50c3d",
                "port_range_max": null,
                "port_range_min": null,
                "protocol": null,
                "remote_group_id": null,
                "remote_ip_prefix": null,
                "security_group_id": "2076db17-a522-4506-91de-c6dd8e837028",
                "project_id": "e4f50856753b4dc6afee5fa6b9b6c550",
                "created_at": "2018-03-19T19:16:56Z",
                "updated_at": "2018-03-19T19:16:56Z",
                "revision_number": 1,
                "revisio[n_number": 1,
                "tags": ["tag1,tag2"],
                "tenant_id": "e4f50856753b4dc6afee5fa6b9b6c550",
                "description": ""
            }
        ],
        "project_id": "e4f50856753b4dc6afee5fa6b9b6c550",
        "created_at": "2018-03-19T19:16:56Z",
        "updated_at": "2018-03-19T19:16:56Z",
        "revision_number": 1,
        "tags": ["tag1,tag2"],
        "tenant_id": "e4f50856753b4dc6afee5fa6b9b6c550",
        "stateful": true
    }
}  
    
'''


def create_security_group(name, description="", project_id=project_id, tenant_id=tenant_id, stateful=False, request=None):
    easystack_api.ChangeUrl('Neutron')
    data = {
        "security_group": {
            "name": name,
            "description": description,
            "project_id": project_id,
            "tenant_id": tenant_id,
            # "stateful": stateful
        }
    }
    url = '/v2.0/security-groups'
    security_group = easystack_api.post(url, data, request=request)
    if "security_group_rule" in security_group:
        # TODO 保存信息到数据库
        return True
    else:
        return False


'''
desc: 通过安全组名称获取安全组信息
method: Get
uri: /v2.0/security-groups
params: 
resp:
{
    "security_groups": [
        {
            "description": "default",
            "id": "85cc3048-abc3-43cc-89b3-377341426ac5",
            "name": "default",
            "security_group_rules": [
                {
                    "direction": "egress",
                    "ethertype": "IPv6",
                    "id": "3c0e45ff-adaf-4124-b083-bf390e5482ff",
                    "port_range_max": null,
                    "port_range_min": null,
                    "protocol": null,
                    "remote_group_id": null,
                    "remote_ip_prefix": null,
                    "security_group_id": "85cc3048-abc3-43cc-89b3-377341426ac5",
                    "project_id": "e4f50856753b4dc6afee5fa6b9b6c550",
                    "revision_number": 1,
                    "tags": ["tag1,tag2"],
                    "tenant_id": "e4f50856753b4dc6afee5fa6b9b6c550",
                    "created_at": "2018-03-19T19:16:56Z",
                    "updated_at": "2018-03-19T19:16:56Z",
                    "description": ""
                }
            ],
            "project_id": "e4f50856753b4dc6afee5fa6b9b6c550",
            "revision_number": 8,
            "created_at": "2018-03-19T19:16:56Z",
            "updated_at": "2018-03-19T19:16:56Z",
            "tags": ["tag1,tag2"],
            "tenant_id": "e4f50856753b4dc6afee5fa6b9b6c550",
            "stateful": true
        }
    ]
}
    
'''


def get_security_group(name, p_id=project_id, t_id=tenant_id, request=None):
    easystack_api.ChangeUrl('Neutron')
    url = '/v2.0/security-groups?' + 'name=' + name + '&project_id=' + p_id + '&tenant_id=' + t_id
    pprint(url)
    security_group, code = easystack_api.get(url, request=request)
    pprint(security_group)
    return security_group


'''
desc: 指定安全组，添加安全规则
uri: /v2.0/security-group-rules
params:
    {
        "security_group_rule": {
            "direction": "ingress",
            "port_range_min": "80",
            "ethertype": "IPv4",
            "port_range_max": "80",
            "protocol": "tcp",
            "remote_group_id": "85cc3048-abc3-43cc-89b3-377341426ac5",
            "security_group_id": "a7734e61-b545-452d-a3cd-0189cbd9747a"
        }
    }

resp:   
{
    "security_group_rule": {
        "direction": "ingress",
        "ethertype": "IPv4",
        "id": "2bc0accf-312e-429a-956e-e4407625eb62",
        "port_range_max": 80,
        "port_range_min": 80,
        "protocol": "tcp",
        "remote_group_id": "85cc3048-abc3-43cc-89b3-377341426ac5",
        "remote_ip_prefix": null,
        "security_group_id": "a7734e61-b545-452d-a3cd-0189cbd9747a",
        "project_id": "e4f50856753b4dc6afee5fa6b9b6c550",
        "revision_number": 1,
        "tenant_id": "e4f50856753b4dc6afee5fa6b9b6c550",
        "created_at": "2018-03-19T19:16:56Z",
        "updated_at": "2018-03-19T19:16:56Z",
        "description": ""
    }
}

'''


def add_security_group_rule(security_group_name, remote_ip_prefix=None, direction=None, ethertype=None, protocol=None, request=None):
    if direction is None:
        direction = "ingress"

    if ethertype is None:
        ethertype = "IPv4"

    if protocol is None:
        protocol = "tcp"
    if remote_ip_prefix is None:
        remote_ip_prefix = "0.0.0.0/0"

    security_group_info = get_security_group(security_group_name, request=request)
    pprint(security_group_info)
    security_group_id = security_group_info["security_groups"][0]['id']

    easystack_api.ChangeUrl('Neutron')

    data = {
        "security_group_rule": {
            "direction": direction,
            "ethertype": ethertype,
            "protocol": protocol,
            "remote_ip_prefix": remote_ip_prefix,
            "security_group_id": security_group_id,
            "tenant_id": tenant_id
        }

    }
    url = '/v2.0/security-group-rules'

    security_group_rule, code = easystack_api.post(url, data, request=request)
    pprint(security_group_rule)
    if code > 300:
        return False
    else:
        return True
    if "security_group_rule" in security_group_rule:
        # TODO 保存信息到数据库
        return True
    else:
        return False


'''
desc: 按规则 Id 删除指定安全组规则 
methods: delete
uri: /v2.0/security-group-rules/{id}
resp: ''
'''


def del_security_group_rule(id=None, request=None):
    easystack_api.ChangeUrl('Neutron')
    url = '/v2.0/security-group-rules/' + id
    security_group_rule, code = easystack_api.delete(url, request=request)
    if security_group_rule == '':
        # TODO 删除数据库中规则信息
        return True
    else:
        return False


# if __name__ == '__main__':
#     data = neutron_create_floatingip('public_net')
#     pprint(data)
