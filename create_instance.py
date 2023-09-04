import requests
import json
import easystackapi.neutronapi as neutronapi
import easystackapi.cinderapi as cinderapi
from easystackapi import novaapi
from easystackapi.novaapi import get_servers
from easystackapi.utils import commonvariable, Stack
from easystackapi.utils.commonvariable import externalnetworkname
from easyopenapi.stack_request import StackApi

HOST = '192.168.204.46'
STACK_TYPE = 'OPENSTACK'
KEYSTONE_HOST = "http://%s:5000/" % HOST
GLANCE_HOST = "http://%s:9292/" % HOST
NOVA_HOST = "http://%s:8774/v2.1/" % HOST
CINDER_HOST = "http://%s:8776/" % HOST
NEUTRON_HOST = "http://%s:9696/" % HOST
ACTAVIA_HOST = "http://%s:9876/" % HOST
PROJECT_ID = "d5fc33c31d724263bbc45d7e1d8cd1ff"

headers =  {'Content-Type': "application/json",
                'X-Openstack-Nova-API-Version': "2.64",
                'X-Auth-Token': "gAAAAABf4bQxKiwfzXBbR4S_VRjE8Gp2_HNrUpohSuKwjOw9l06OIL7gqestfM4vlHRXVdE1eOo05fOWoppJn6BpHsxwzzQHJNBqxPdBevC8LyOnMeT2WjKKfoKgpJDl-Q1dlI_5PHrP4AypCuOBFn44g7jHQnpq-tbP9nr4DOmp8PrbDqvypmc"}


StackApi.openstack_login(userName='admin', passWord='123456', userDomainName='default', projectName='mx-im')
def create_full_instance(instance_name='', iamge_name="", image_flavor='',hypervisor_hostname='compute-hg', vm_config_list=[], request=None):

    ips = neutronapi.get_floating_ip(externalnetworkname, request=request)

    intranetname='jp_network'
    router_name = 'router_xxxx'
    subnetname = 'jp_network_subnet'
    # public_net_id = neutronapi.get_network_byname('provider', request=request)['id']
    # route_id = neutronapi.create_router(router_name, public_net_id, request=request)

    # print("当前route ID是 " + route_id)
    print("当前intranetname是 " + intranetname)
    print("当前subnetname是 " + subnetname)
    # [network_id, subnet_id, cidr, gateway_ip,
    #  router_interface_info] = neutronapi.create_networkwithsubnetrouterinterface(
    #     intranetname, subnetname, route_id, cidr_index=11, request=request)
    import base64
    user_data = """#!/bin/sh
passwd <<EOF
123456
123456
EOF

sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/g' /etc/ssh/sshd_config

service sshd restart
                        """
    encodeStr = base64.b64encode(user_data.encode(encoding='utf-8'))
    config_data = str(encodeStr, 'utf-8')
    [server, succ] = novaapi.create_instance_with_nofloatingip(intranetname, iamge_name,
                                                               image_flavor, instance_name,data=config_data,
                                                               hypervisor_hostname=hypervisor_hostname,
                                                               request=request)

    # print('创建网络结果', [network_id, subnet_id, cidr, gateway_ip,
    #                  router_interface_info])

    print('数据库云主机创建结果')

    vm_floatingipid = ips['id']
    vm_floatingip = ips['floating_ip_address']
    vm_config_list.append({
        'vm_id': server['vm_id'],
        'vm_internalip': server['vm_intranetip'],
        'vm_adminPass': server['adminPass'],
        'vm_type': 'DB',
        'request_ip': vm_floatingip,
        'is_detail': False,
        'vm_floatingip': vm_floatingip,
        'vm_floatingipid': vm_floatingipid,
        'instancename': instance_name,
    })

    import exceptions
    hasNoDetail = True
    while hasNoDetail:
        hasNoDetail = False
        for cfg in vm_config_list:
            if cfg['is_detail']:
                continue
            hasNoDetail = True
            _server = get_servers(id=cfg['vm_id'], request=request)
            if _server['status'] == 'ERROR':
                raise exceptions.CreateMimicError('虚拟机创建失败')
            elif _server['status'] == 'ACTIVE':
                if cfg['vm_type'] == 'DB':
                    res = neutronapi.add_floatingip_to_port(cfg['vm_floatingipid'],
                                                            port_id=novaapi.get_servers_interface_port(
                                                                _server['vm_id']),
                                                            request=request)
                    if res:
                        print('数据库绑定浮动 IP 成功')
                    else:
                        raise exceptions.CreateMimicError('数据库绑定浮动 IP 失败')
                    cfg['is_detail'] = True



def create_instance(image_id="", network_id="", falvor_id=""):

    data = {
        "server": {
            "config_drive": True,
            "availability_zone": "default_az:compute-x86:compute-x86",
            "imageRef": "03f04a77-35e6-4625-88e1-a893bdc0cf0e",
            "flavorRef": "2-2048-100",
            # "adminPass": '123456',
            "name": "ntpservice",
            "networks": [{
                "uuid": "5e7af2a1-1da7-4b96-a1d4-64f25418302a"
            }]
        }


    }
    res = requests.post(NOVA_HOST + "/"+ PROJECT_ID +'/servers', data = json.dumps(data), headers = headers)
    print(res.content)

def get_instance_prot(server_id=""):
    res = requests.get(NOVA_HOST + '/' + PROJECT_ID + '/' + 'servers/' + server_id + '/os-interface', headers=headers)
    print(res.content)

def show_server_passwd(server_id=""):
    print(NOVA_HOST  + 'servers/'+ server_id + '/os-server-password')
    res = requests.get(NOVA_HOST  + 'servers/'+ server_id + '/os-server-password' , headers=headers)
    print(res.content)
# show_server_passwd(server_id='6cbdd924-0eb2-4cd7-a7cc-01c782f155d7')
create_full_instance(instance_name='OA', iamge_name="clound-centos", image_flavor='4-4096-100',hypervisor_hostname='compute-hg', vm_config_list=[], request=None)