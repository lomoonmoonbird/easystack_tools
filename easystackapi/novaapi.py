import base64
import json
import logging
import time
from pprint import pprint
import random

from easystackapi import neutronapi, glanceapi
from easystackapi.neutronapi import get_floating_ip
from easystackapi.utils.commonvariable import OS_Types
from easystackapi.utils.commonvariable import tenant_id
from easystackapi.utils.commonvariable import zone_name
# from easystackapi.utils.easy_request import easystack_api

from easyopenapi.stack_request import StackApi
from easyopenapi.defaults import username, password, project_domain_name
easystack_api = StackApi

Version = 2.1
# setting log
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(filename='easystack-nova-api.log', level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)

def reboot(server_id, project_id=tenant_id, reboot_type='HARD', request=None):
    easystack_api.ChangeUrl('Nova')
    url = project_id + '/servers/' + server_id + '/action'
    info = easystack_api.post(url, data={"reboot":{"type": reboot_type}}, request=request)
    logging.info(server_id + " 虚拟机重启")
    return info

def get_server(project_id=tenant_id, request=None):
    easystack_api.ChangeUrl('Nova')
    servers = easystack_api.get(project_id + '/servers', request=request)
    return (servers['servers'])


def get_hypervisors_stats_cpu_info(project_id=tenant_id, request=None):
    easystack_api.ChangeUrl('Nova')
    hypervisors = easystack_api.get(project_id + '/os-hypervisors/detail',request=request)
    hypervisorslist = []
    for hypervisor in hypervisors['hypervisors']:
        hypervisorslist.append(hypervisor)
    result = {}
    if hypervisorslist:
        hypervisors = hypervisorslist[0]
        cpu_info = hypervisors['cpu_info']
        result = cpu_info
        result['vcpus'] = hypervisors['vcpus']
        result['vcpus_used'] = hypervisors['vcpus_used']
        result['memory_mb'] = hypervisors['memory_mb']
        result['memory_mb_used'] = hypervisors['memory_mb_used']
        result['local_gb_used'] = hypervisors['local_gb_used']
        result['local_gb'] = hypervisors['local_gb']
    return result


def get_hypervisors_statistics(hypervisorname='', project_id=tenant_id,request=None):
    """版本参数有差异"""
    easystack_api.ChangeUrl('Nova')
    hypervisors_statistics = easystack_api.get(project_id + '/os-hypervisors/statistics', request=request)
    statistics = {}
    hypervisor = hypervisors_statistics['hypervisor_statistics']
    statistics['vcpus'] = hypervisor['vcpus'] - hypervisor['vcpus_used']
    statistics['mem'] = hypervisor['free_ram_mb']
    statistics['disk'] = hypervisor['free_disk_gb']
    statistics['running_vms'] = hypervisor['running_vms']
    statistics['current_workload'] = hypervisor['current_workload']
    # todo 字段不一致
    # statistics['cpu_vendor'] = eval(hypervisor.cpu_info)['vendor']
    # statistics['cpu_arch'] = eval(hypervisor.cpu_info)['arch']
    # statistics['os_type'] = OS_Types[hypervisorname]

    hypervisors = get_hypervisors_stats_cpu_info(request=request)

    # todo 数据先置空
    statistics['cpu_vendor'] = hypervisors['vendor']
    statistics['cpu_arch'] = hypervisors['arch']
    # statistics['vcpus_used'] = hypervisors['vcpus_used']
    # statistics['memory_mb'] = hypervisors['memory_mb']
    # statistics['memory_mb_used'] = hypervisors['memory_mb_used']
    # statistics['local_gb'] = hypervisors['local_gb']
    # statistics['local_gb_used'] = hypervisors['local_gb_used']
    statistics['os_type'] = OS_Types[hypervisorname] if hypervisorname in OS_Types else ''

    return statistics


def get_availability_zones(zonename=None, hypervisor_hostname=None, projeact_id=tenant_id, request=None):
    easystack_api.ChangeUrl('Nova')
    url = tenant_id + '/os-availability-zone/detail'

    ret = easystack_api.get(url, request=request)
    availability_zones = ret['availabilityZoneInfo']
    zoneslist = []
    for availability_zone in availability_zones:
        temp = {}
        # 按 zonename 查询
        if zonename:
            if availability_zone['zoneName'] == zonename:
                logging.debug('按 zonename 查询: ' + zonename)
                temp = availability_zone_struct(availability_zone)
                return temp
            else:
                return None
        elif hypervisor_hostname:
            hostlist = list(availability_zone['hosts'])
            for host in hostlist:
                if host == hypervisor_hostname:
                    return availability_zone['zoneName']
                else:
                    return 'unknown'

        temp = availability_zone_struct(availability_zone)
        zoneslist.append(temp)
    return zoneslist


def availability_zone_struct(availability_zone):
    temp = {}
    temp['zonename'] = availability_zone['zoneName']
    temp['hostslist'] = list(availability_zone['hosts'])
    temp['status'] = availability_zone['zoneState']['available']
    temp['iscompute'] = False
    values = availability_zone['hosts'].values()
    if 'nova-compute' in values:
        temp['iscompute'] = True

    temp['vcpus'] = 0
    temp['mem'] = 0
    temp['disk'] = 0
    temp['running_vms'] = 0
    temp['current_workload'] = 0
    temp['cpu_vendor'] = ''
    temp['cpu_arch'] = ''
    temp['os_type'] = ''
    if temp['iscompute'] is True:
        for host in temp['hostslist']:
            statistics = get_hypervisors_statistics(host)
            temp['vcpus'] += statistics['vcpus']
            temp['mem'] += statistics['mem']
            temp['disk'] += statistics['disk']
            temp['cpu_vendor'] = statistics['cpu_vendor']
            temp['cpu_arch'] = statistics['cpu_arch']
            temp['os_type'] = statistics['os_type']
            temp['running_vms'] += statistics['running_vms']
            temp['current_workload'] += statistics['current_workload']
    return temp


def get_availability_zonebyname(zone_name):
    availability_zone = get_availability_zones(zonename=zone_name)
    return availability_zone


def get_hypervisors_zone(hypervisorHostname, project_id=tenant_id, request=None):
    hypervisor_zone = get_availability_zones(hypervisor_hostname=hypervisorHostname, request=request)
    return hypervisor_zone


def get_hypervisors_ip(hypervisor_hostname=None, project_id=tenant_id, request=None):
    hypervisors = get_hypervisors(hypervisor_hostname, request=request)
    if hypervisor_hostname:
        if hypervisors['node_name'] == hypervisor_hostname:
            return hypervisors['node_ip']
    return hypervisors


def get_hypervisors(name=None, project_id=tenant_id, request=None):
    easystack_api.ChangeUrl('Nova')
    hypervisors = easystack_api.get(project_id + '/os-hypervisors/detail', request=request)

    hypervisorslist = []
    if "hypervisors" not in hypervisors:
        return ()
    for hypervisor in hypervisors['hypervisors']:
        if name:
            if hypervisor['hypervisor_hostname'] == name:
                temp = {}
                temp['node_name'] = hypervisor['hypervisor_hostname']
                temp['node_ip'] = hypervisor['host_ip']
                temp['status'] = hypervisor['status']
                temp['state'] = hypervisor['state']
                temp['node_id'] = hypervisor['id']
                temp['hypervisor_type'] = hypervisor['hypervisor_type']
                statistics = get_hypervisors_statistics(hypervisor['hypervisor_hostname'])
                # todo 调试使用后续删掉
                # temp['statistics'] = statistics
                pprint(statistics)

                temp['vcpus'] = statistics['vcpus']
                temp['mem'] = statistics['mem']
                temp['disk'] = statistics['disk']
                temp['cpu_vendor'] = statistics['cpu_vendor']
                temp['cpu_arch'] = statistics['cpu_arch']
                temp['os_type'] = statistics['os_type']
                temp['running_vms'] = statistics['running_vms']
                temp['current_workload'] = statistics['current_workload']
                temp['zone'] = get_hypervisors_zone(hypervisor['hypervisor_hostname'])
                return temp
        temp = {}
        temp['node_name'] = hypervisor['hypervisor_hostname']
        temp['node_ip'] = hypervisor['host_ip']
        temp['status'] = hypervisor['status']
        temp['state'] = hypervisor['state']
        temp['node_id'] = hypervisor['id']
        temp['hypervisor_type'] = hypervisor['hypervisor_type']
        statistics = get_hypervisors_statistics(hypervisor['hypervisor_hostname'], request=request)
        # todo 调试使用后续删掉
        # temp['statistics'] = statistics
        temp['vcpus'] = statistics['vcpus']
        temp['mem'] = statistics['mem']
        temp['disk'] = statistics['disk']
        temp['cpu_vendor'] = statistics['cpu_vendor']
        temp['cpu_arch'] = statistics['cpu_arch']
        temp['os_type'] = statistics['os_type']
        temp['running_vms'] = statistics['running_vms']
        temp['current_workload'] = statistics['current_workload']
        temp['zone'] = get_hypervisors_zone(hypervisor['hypervisor_hostname'], request=request)
        hypervisorslist.append(temp)
    return (hypervisorslist)


def get_hypervisorsbyname(hypervisor_hostname, request=None):
    temp = get_hypervisors(name=hypervisor_hostname, request=request)
    return (temp)


def get_flavor(name=None, id=None, project_id=tenant_id, request=None):
    easystack_api.ChangeUrl('Nova')
    flavors = easystack_api.get(project_id + '/flavors/detail', request=request)
    flavorlist = []
    if "flavors" not in flavors:
        return []
    print("============")
    print(flavors)
    print("=============")
    for flavor in flavors['flavors']:
        print("flavor['name'] ----------->", flavor['name'])
        temp = {}
        if (id and flavor['id'] == id) or (name and flavor['name'] == name):
            temp['flavor_name'] = flavor['name']
            temp['vcpus'] = flavor['vcpus']
            temp['ram'] = flavor['ram']
            temp['disk'] = flavor['disk']
            temp['flavor_id'] = flavor['id']
            temp['is_public'] = flavor['os-flavor-access:is_public']
            return temp
        temp['flavor_name'] = flavor['name']
        temp['vcpus'] = flavor['vcpus']
        temp['ram'] = flavor['ram']
        temp['disk'] = flavor['disk']
        temp['flavor_id'] = flavor['id']
        temp['is_public'] = flavor['os-flavor-access:is_public']
        flavorlist.append(temp)
    return flavorlist



def get_servers(name=None, id=None, project_id=tenant_id,request=None):
    from easyopenapi.defaults import username, password, project_domain_name
    easystack_api.login(userName=username,passWord=password, projectName=project_domain_name)
    easystack_api.ChangeUrl('Nova')
    servers = easystack_api.get(project_id + '/servers/detail', request=request)
    hypervisors = get_hypervisors_ip(request=request)
    # nova = client.Client(Version, session=keystone.session)
    # servers= nova.servers.list(detailed=True)
    vmslist = []
    if "servers" not in servers:
        return []
    for server in servers['servers']:
        # if server['status'] == 'BUILD':
        #     continue
        temp = {}
        # 获取vm 网络中第一个网络的名称
        if (id and server['id'] == id) or (name and server['name'] == name):
            if server['addresses']:
                network_name = list(server['addresses'].keys())[0]
                temp['vm_intranetip'] = list(server['addresses'][network_name])[0][
                    'addr']
            else:
                temp['vm_intranetip'] = ''

            temp['vm_name'] = server['name']
            temp['vm_id'] = server['id']
            temp['status'] = server['status']


            temp['vm_nodeZone'] = server['OS-EXT-AZ:availability_zone']
            temp['node'] = server['OS-EXT-SRV-ATTR:host']
            temp['volumes'] = json.dumps(server['os-extended-volumes:volumes_attached'])

            for hypervisor in hypervisors:
                if hypervisor['node_name'] == temp['node']:
                    temp['node_ip'] = hypervisor['node_ip']
            return temp

        if server['addresses']:
            network_name = list(server['addresses'].keys())[0]
            temp['vm_intranetip'] = list(server['addresses'][network_name])[0][
                'addr']
        else:
            temp['vm_intranetip'] = ''

        temp['vm_name'] = server['name']
        temp['vm_id'] = server['id']
        temp['status'] = server['status']
        temp['vm_nodeZone'] = server['OS-EXT-AZ:availability_zone']
        temp['node'] = server['OS-EXT-SRV-ATTR:host']
        for hypervisor in hypervisors:
            if hypervisor['node_name'] == temp['node']:
                temp['node_ip'] = hypervisor['node_ip']
        temp['volumes'] = json.dumps(server['os-extended-volumes:volumes_attached'])
        vmslist.append(temp)

    return vmslist


def get_servers_interface_port(server_id=None, project_id=tenant_id, request=None):
    easystack_api.ChangeUrl('Nova')
    servers = easystack_api.get(project_id + '/servers/' + server_id + '/os-interface', request=request)
    return servers['interfaceAttachments'][0]['port_id']

def get_serversbyname(vmname, request=None):
    vm = get_servers(name=vmname, request=request)
    return vm


def create_instance_with_floatingip(network_name, image_name, flavor_name, instancename, externalnetworkname,
                                    data=None, request=None):
    return create_instance(network_name, image_name, flavor_name, instancename, externalnetworkname, data=data, request=None)


def create_mimic_main(instancename):
#     user_data = """#!/bin/bash
# cd /opt
# touch proxy_data
# echo "database ip: %(database_ip)s: %(database_port)d"  >> /opt/proxy_data
# echo "redis ip: %(redis_ip)s: %(redis_port)d" >> /opt/proxy_data
# echo "master ip: %(master_ip)s: %(master_port)d" >> /opt/proxy_data
# echo "volume ip: %(volume_ip)s: %(volume_port)d" >> /opt/proxy_data
# """
    user_data = """#!/bin/sh
tee /opt/proxy_data<<-'EOF'
database ip: %(database_ip)s: %(database_port)d
redis ip: %(redis_ip)s: %(redis_port)d
master ip: %(master_ip)s: %(master_port)d
volume ip: %(volume_ip)s: %(volume_port)d
EOF
passwd root<<EOF
comleader@12
comleader@12
EOF
sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/g' /etc/ssh/sshd_config
service sshd restart
"""
    user_datas = user_data % dict(database_ip='192.168.100.10', database_port=5432,
                                  redis_ip='192.168.100.10', redis_port=6379,
                                  master_ip='192.168.100.10', master_port=9333,
                                  volume_ip='192.168.100.10', volume_port=18080)


    print(user_datas)
    encodeStr = base64.b64encode(user_datas.encode(encoding='utf-8'))
    pprint(encodeStr)
    config_data = str(encodeStr, 'utf-8')
    # config_data = base64.encodestring(user_datas)
    pprint(config_data)

    server, code = create_instance(network_name='share_net', image_name='centos7.6-1811-2nic.raw', flavor_name='4-8192-100',
                                   instancename=instancename, zonename='default-az', data=config_data,
                                   project_id=tenant_id)

    return server, code


def create_instance(network_name, image_name, flavor_name, instancename, externalnetworkname=None, zonename=zone_name,
                    data=None, project_id=tenant_id, hypervisor_hostname=None, request=None):

    # 获取镜像
    image = glanceapi.get_imagebynane(name=image_name, request=request)
    # 获取flavor
    flavor = get_flavor(flavor_name, request=request)
    print('create_instance_falvor')
    print(flavor_name)
    print(flavor)
    # 获取network
    network = neutronapi.get_network_byname(network_name, request=request)

    if not image:
        print("镜像无法找到")
        if externalnetworkname:
            return (None, None, False)
        else:
            return (None, False)
    if not flavor:
        print("镜像无法找到")
        if externalnetworkname:
            return (None, None, False)
        else:
            return (None, False)

    if not network:
        print("网络无法找到")
        if externalnetworkname:
            return (None, None, False)
        else:
            return (None, False)

    create_data = {}
    if data is not None:
        create_data['user_data'] = data
        create_data['config_drive'] = True
    if zonename:
        if hypervisor_hostname is not None:
            create_data['availability_zone'] = '{}:{}:{}'.format(zonename,hypervisor_hostname,hypervisor_hostname)
        else:
            create_data['availability_zone'] = zonename

    # 通过 hypervisor_hostname 指定 VM 在指定计算节点创建
    # if hypervisor_hostname is not None:
    #     create_data['hostname'] = hypervisor_hostname

    # create_data['networks.uuid'] = network['id']
    # create_data['networks.id'] = network['id']
    create_data['config_drive'] = True
    create_data['imageRef'] = image['image_id']
    create_data['flavorRef'] = flavor['flavor_id']
    create_data['name'] = instancename
    create_data['networks'] = [{
        "uuid": network['id']

    }]


    # 随机生成 vm 管理密码
    #create_data['adminPass'] = generate_random_str(10)
    create_data['adminPass'] = 'viewadmin'

    # 请求创建实例接口
    easystack_api.ChangeUrl('Nova')
    pprint({'server': create_data})
    servers = easystack_api.post(project_id + '/servers', data={'server': create_data}, request=request)
    server_id = servers['server']['id']
    # 获取创建实例详情，查询结果
    _server = get_servers(id=server_id)
    _server['adminPass'] = create_data['adminPass']

    # 如果不需要浮动ip
    if externalnetworkname is None:
        return (_server, True)
    else:
        while _server['status'] == "BUILD":
            print(instancename + "is building, please wait")
            _server = get_servers(id=server_id)
            print(_server['status'])
            time.sleep(10)
        if _server['status'] == "ERROR":
            print("the server is in error state")
            print(_server)
            delete_instance(server_id)
            return (None,None, False)
        portid = get_servers_interface_port(server_id, request=request)
        floating_ip = get_floating_ip(externalnetworkname, (portid), request=request)
        _server = get_servers(id=server_id, request=request)
        return (_server, floating_ip, True)



def create_instance_with_nofloatingip(network_name, image_name, flavor_name, instancename, data=None,hypervisor_hostname=None, request=None):
    return create_instance(network_name, image_name, flavor_name, instancename, data=data,hypervisor_hostname=hypervisor_hostname, request=request)
    # keystone = get_keystone()
    # nova = client.Client(Version, session=keystone.session)
    #
    # image = nova.glance.find_image(image_name)  # To find specific image
    # flavor = nova.flavors.find(name=flavor_name)  # To find specific flavor
    # network = nova.neutron.find_network(name=network_name)  # To find specific internal network
    # print(network.__dict__)
    # if data is None:
    #     server = nova.servers.create(name=instancename, image=image, flavor=flavor, nics=[{'net-id': network.id}])
    # else:
    #     print(data)
    #     server = nova.servers.create(name=instancename, image=image, flavor=flavor, nics=[{'net-id': network.id}],
    #                                  userdata=data, config_drive=True)
    # while server.status == "BUILD":
    #     print(instancename + "is building, please wait")
    #     server = nova.servers.find(id=server.id)
    #     print(server.status)
    #     time.sleep(10)
    #
    # if server.status == "ERROR":
    #     print("the server is in error state")
    #     nova.servers.force_delete(server)  # delete wrong vm
    #     return (None, False)
    # return (server, True)


def create_instance_with_zone_nofip(network_name, image_name, zonename, flavor_name, instancename,
                                    data=None,hypervisor_hostname=None, request=None):
    return create_instance(network_name, image_name, flavor_name, instancename, zonename=zonename,
                           data=data,hypervisor_hostname=hypervisor_hostname,request=request)

    # keystone = get_keystone()
    # nova1 = client.Client(Version, session=keystone.session)
    # image = nova1.glance.find_image(image_name)  # To find specific image
    # flavor = nova1.flavors.find(name=flavor_name)  # To find specific flavor
    # network = nova1.neutron.find_network(name=network_name)  # To find specific internal network
    # # launch a instance
    #
    # if data is None:
    #     server = nova1.servers.create(name=instancename, image=image, flavor=flavor, nics=[{'net-id': network.id}],
    #                                   availability_zone=zonename)  # zone 含服务器名称
    # else:
    #     server = nova1.servers.create(name=instancename, image=image, flavor=flavor, nics=[{'net-id': network.id}],
    #                                   availability_zone=zonename, userdata=data, config_drive=True)  # zone 含服务器名称
    #
    # time.sleep(10)
    # # add functtion, if status is error, delete the just created vm, and report an error and exit!!!!!!!!!!!
    # if server.status == "ERROR":
    #     print("the server is in error state")
    #     nova1.servers.force_delete(server)  # delete wrong vm
    #     return (None, False)
    # while 1:
    #     time.sleep(10)
    #     print("the server is NOT ready")
    #     server = nova1.servers.find(id=server.id)
    #     if server.status == "ACTIVE":
    #         break
    #     if server.status == "ERROR":
    #         print("the server is in error state")
    #         nova1.servers.force_delete(server)  # delete wrong vm
    #         return (None, False)
    #
    # print(server.status)
    # return (server, True)


def create_instance_with_zone_and_fip(network_name, image_name, zonename, flavor_name, instancename,
                                      externalnetworkname, data=None,hypervisor_hostname=None, request=None):
    return create_instance(network_name, image_name, flavor_name, instancename, externalnetworkname=externalnetworkname,
                           zonename=zonename, data=data,hypervisor_hostname=hypervisor_hostname, request=request)

    # keystone = get_keystone()
    # nova1 = client.Client(2, session=keystone.session)
    #
    # image = nova1.glance.find_image(image_name)  # To find specific image
    # flavor = nova1.flavors.find(name=flavor_name)  # To find specific flavor
    # network = nova1.neutron.find_network(name=network_name)  # To find specific internal network
    #
    # print("------------当前实例所在的网络----------")
    # print(network.id)
    # if image is None:
    #     print("镜像无法找到")
    #     return (None, None, False)
    #
    # if flavor is None:
    #     print("镜像无法找到")
    #     return (None, None, False)
    #
    # if network is None:
    #     print("网络无法找到")
    #     return (None, None, False)
    #
    # if data is None:
    #     server = nova1.servers.create(name=instancename, image=image, flavor=flavor, nics=[{'net-id': network.id}],
    #                                   availability_zone=zonename)  # zone 含服务器名称
    # else:
    #     server = nova1.servers.create(name=instancename, image=image, flavor=flavor, nics=[{'net-id': network.id}],
    #                                   availability_zone=zonename, userdata=data, config_drive=True)  # zone 含服务器名称
    #
    # time.sleep(10)
    # # add functtion, if status is error, delete the just created vm, and report an error and exit!!!!!!!!!!!
    # if server.status == "ERROR":
    #     print("the server is in error state")
    #     nova1.servers.force_delete(server)  # delete wrong vm
    #     return (None, None, False)
    # '''
    # 一 vm_state
    # 1 虚拟机处在稳定状态，通过api产生的状态。
    # 2 有Active,Error,Reboot,Build,Shutoff五种状态
    # '''
    # creatTime = 10
    # print(server.__dict__)
    # while 1:
    #     time.sleep(10)
    #     print("the server is NOT ready")
    #     server = nova1.servers.find(id=server.id)
    #     if server.status == "ACTIVE":
    #         break
    #     if server.status == "ERROR" or creatTime > 300:
    #         print("the server is in error state or timeout")
    #         nova1.servers.force_delete(server)  # delete wrong vm
    #         return (None, None, False)
    #     print(server.status)
    #     print(server.id)
    #     creatTime += 10
    #
    # portidd = server.interface_list()  # list just created vm's interface , class type
    # floating_ip = neutron_create_floatingip(keystone, externalnetworkname, (portidd[0].id))
    #
    # # print the just created vm's network information
    # list2 = server.networks.get(network_name)  # vm's network attribute
    # print(list2)
    # list2.append(floating_ip['floatingip']['floating_ip_address'])
    # # list2.append(server.networks.get(externalnetworkname) ) # vm's network attribute
    # print(list2)
    # # print(a)
    # print(list2[0])  # internal ip
    # if len(list2) >= 2:
    #     print(list2[1])  # floating ip, if exits
    # print(server.status)
    #
    # return (server, floating_ip, True)


# 删除实例到回收站
def delete_instance(vmid, project_id=tenant_id, request=None):
    easystack_api.ChangeUrl('Nova')
    url = project_id + '/servers/' + vmid
    servers = easystack_api.delete(url, request=request)
    pprint(servers)
    logging.info(vmid + " 服务终止，虚拟机放入回收站")
    return 0


#直接删除实例
def force_delete_instance(vmid, force_delete=None, project_id=tenant_id, request=None):
    easystack_api.ChangeUrl('Nova')
    url = project_id + '/servers/' + vmid + '/action'
    data = {
        "forceDelete": force_delete
    }
    servers = easystack_api.post(url,data, request=request)
    pprint(servers)
    logging.info(vmid + " 服务终止，虚拟机被删除")
    if servers == '':
        return True
    else:
        return False


def add_security_group(server_id, security_group_name, request=None):
    """
    :desc 为虚拟机添加安全组
    :method: post
    :uri: /servers/{server_id}/action
    :param server_id: 虚拟机 Id
    :param security_group_name: 安全组名称
    :params
        {
            "addSecurityGroup": {
                "name": "test"
            }
        }
    resp:
    """
    easystack_api.ChangeUrl("Nova")
    url = "/servers/" + server_id + "/action"
    data = {
        "addSecurityGroup": {
            "name": security_group_name
        }
    }
    res = easystack_api.post(url, data, request=request)
    return res


def change_passwd(server_id, admin_pass, request=None):
    """
    :desc 修改虚拟机密码
    :uri /servers/{server_id}/action
    :method: post
    :parameter
        {
            "changePassword" : {
                "adminPass" : {admin_pass}
            }
        }
    :param server_id:
    :param admin_pass:
    :resp
    """
    easystack_api.ChangeUrl("Nova")
    url = "/servers/" + server_id + "/action"
    data = {
        "changePassword": {
            "adminPass": admin_pass
        }
    }

    res = easystack_api.post(url, data, request=request)
    pprint(res)
    return res


def server_metadata(server_id, metadata, request=None):
    """
    desc: 向虚拟机注入 metadata ，键值对数据，虚拟机通过 curl -sL 169.254.169.254/openstack/latest/meta_data.json 获取数据
    method: post
    uri: /servers/{server_id}/metadata
    :param
        {
            "metadata": {
                "foo": "Foo Value",
                "ss": "asa"
            }
        }

    """

    easystack_api.ChangeUrl("Nova")
    url = "/servers/" + server_id + "/metadata"
    res = easystack_api.post(url, metadata, request=request)
    pprint(res)
    return res

def generate_random_str(randomlength=10):
  """
  生成一个指定长度的随机字符串
  """
  random_str = ''
  base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
  length = len(base_str) - 1
  for i in range(randomlength):
    random_str += base_str[random.randint(0, length)]
  return random_str
