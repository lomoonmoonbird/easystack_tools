# coding = utf-8

# ======================================云管配置==================================
# 限制
API_RESULT_LIMIT = 3

# 回收站软删除小时设置
SOFT_DELETE_HOURS = 24

# 是否开启裁决
JUDGE = False

# 路由权限配置
url_auth = True
url_role = {
    '/api/auth/': ['user', 'admin', None],
    '/api/compute/': ['user', 'admin'],
    '/api/home_page/': ['user', 'admin'],
    '/api/project_manager/': ['user', 'admin'],
    '/api/networks/': ['user', 'admin'],
    '/api/cinder/': ['user', 'admin'],
    '/api/monitor/': ['admin'],
}

# 安全组协议
PROTOCOL = {
    "any": "任何",
    0: "任何",
}

data_user = {
    "username": "admin",
    "password": "comleader@123",
    "domain": "default"
}

# ======================================云平台相关配置==================================

# 兼容EASYSTACK
STACK_TYPE = 'OPENSTACK'
# STACK_TYPE = 'EASYSTACK'

# 是否为测试环境
IS_TEST = False

if STACK_TYPE == 'OPENSTACK':

    if IS_TEST:
        # 测试环境云平台
        OPENSTACK_HOST = '192.168.204.194'
        # 裁决地址
        JUDGE_URL = 'http://192.168.204.112:8001'
    else:
        # 开发环境云平台
        OPENSTACK_HOST = '192.168.204.46'
        # 裁决地址
        JUDGE_URL = 'http://192.168.204.193:8001'
        # 调试环境云平台
        # OPENSTACK_HOST = '192.168.204.30'

    EASYSTACCK_KEYSTONE_HOST = "http://%s:5000/" % OPENSTACK_HOST
    EASYSTACCK_GLANCE_HOST = "http://%s:9292/" % OPENSTACK_HOST
    EASYSTACCK_NOVA_HOST = "http://%s:8774/v2.1/" % OPENSTACK_HOST
    EASYSTACCK_CINDER_HOST = "http://%s:8776/" % OPENSTACK_HOST
    EASYSTACCK_NEUTRON_HOST = "http://%s:9696/" % OPENSTACK_HOST
    EASYSTACCK_0CTAVIA_HOST = "http://%s:9876/" % OPENSTACK_HOST

    if OPENSTACK_HOST == '192.168.204.194':
        # 194节点 配置项
        username = 'admin'
        user_domain_name = 'Default'
        password = 'comleader@123'

        tenant_id = '9d33941f3fc945faa634ad4d404baf53'
        project_id = '9d33941f3fc945faa634ad4d404baf53'

        project_name = 'admin'
        project_domain_name = 'default'

        DEFAULT_ADMIN_PROJECT_ID = "9d33941f3fc945faa634ad4d404baf53"

    elif OPENSTACK_HOST == '192.168.204.197':
        # 194节点 配置项
        username = 'admin'
        user_domain_name = 'Default'
        password = 'comleader@123'

        tenant_id = '4a7f779675484c15b73c2b14bceffa99'
        project_id = '4a7f779675484c15b73c2b14bceffa99'

        project_name = 'admin'
        project_domain_name = 'default'

        DEFAULT_ADMIN_PROJECT_ID = "4a7f779675484c15b73c2b14bceffa99"


    elif OPENSTACK_HOST == '192.168.204.30':
        # 194节点 配置项
        username = 'admin'
        user_domain_name = 'Default'
        password = '123456'

        tenant_id = 'd18dd7c5ca2840eeafa8a317758908c0'
        project_id = 'd18dd7c5ca2840eeafa8a317758908c0'

        project_name = 'admin'
        project_domain_name = 'default'

        DEFAULT_ADMIN_PROJECT_ID = "d18dd7c5ca2840eeafa8a317758908c0"
    else:
        username = 'admin'
        user_domain_name = 'Default'
        password = '123456'

        tenant_id = 'd5fc33c31d724263bbc45d7e1d8cd1ff'
        project_id = 'd5fc33c31d724263bbc45d7e1d8cd1ff'

        project_name = 'admin'
        project_domain_name = 'default'

        DEFAULT_ADMIN_PROJECT_ID = "d5fc33c31d724263bbc45d7e1d8cd1ff"
        # 服务器默认管理密码
        adminPass = "123456"

elif STACK_TYPE == 'EASYSTACK':
    # todo 使用easystackt调试时，需要在代码运行的地方修改系统hosts文件，具体如下：
    # 1、Windows系统： cmd中运行命令：
    # TAKEOWN /F %windir%\System32\drivers\etc\hosts & echo Y| cacls %windir%\system32\drivers\etc\hosts /s:"D:AI(A;ID;FA;;;SY)(A;ID;FA;;;BA)(A;ID;0x1200a9;;;BU)(A;ID;0x1200a9;;;AC)" & notepad %windir%\system32\drivers\etc\hosts
    #    Linux系统： vim /etc/hosts
    # 2、将下列内容粘贴到文件中并保存
    '''
192.168.211.2  cinder.openstack.svc.cluster.local
192.168.211.2  nova.openstack.svc.cluster.local
192.168.211.2  glance.openstack.svc.cluster.local
192.168.211.2  neutron.openstack.svc.cluster.local
192.168.211.2  cinder.openstack.svc.cluster.local
192.168.211.2  keystone.openstack.svc.cluster.local
192.168.211.2  monitoring.openstack.svc.cluster.local
192.168.211.2  alert.openstack.svc.cluster.local
192.168.211.2  monitoring.openstack.svc.cluster.local
192.168.211.2  alert.openstack.svc.cluster.local
192.168.211.2  gnocchi.openstack.svc.cluster.local

192.168.211.2  cinder-api.openstack.svc.cluster.local
192.168.211.2  nova-api.openstack.svc.cluster.local
192.168.211.2  glance-api.openstack.svc.cluster.local
192.168.211.2  neutron-api.openstack.svc.cluster.local
192.168.211.2  cinder-api.openstack.svc.cluster.local
192.168.211.2  keystone-api.openstack.svc.cluster.local
'''

    EASYSTACCK_KEYSTONE_HOST = "http://keystone.openstack.svc.cluster.local/"
    EASYSTACCK_GLANCE_HOST = "http://glance.openstack.svc.cluster.local/"
    EASYSTACCK_NOVA_HOST = "http://nova.openstack.svc.cluster.local/v2.1/"
    EASYSTACCK_CINDER_HOST = "http://cinder.openstack.svc.cluster.local/"
    EASYSTACCK_NEUTRON_HOST = "http://neutron.openstack.svc.cluster.local/"
    # EASYSTACCK_0CTAVIA_HOST = "http://neutron.openstack.svc.cluster.local/"
    # 211.2节点 配置项
    username = 'admin'
    user_domain_name = 'default'
    password = 'Admin@ES20!8'

    tenant_id = 'b525a3a0f11640dcb2d030d287256bda'
    project_id = 'b525a3a0f11640dcb2d030d287256bda'
    project_name = 'admin'
    project_domain_name = 'Default'

    DEFAULT_ADMIN_PROJECT_ID = "b525a3a0f11640dcb2d030d287256bda"

    # 服务器默认管理密码
    adminPass = "123456"

_OPENSTACK_IMAGE_DISK_FORMAT = {
    # '-': 'Select format',
    'aki': 'AKI - Amazon Kernel Image',
    'ami': 'AMI - Amazon Machine Image',
    'ari': 'ARI - Amazon Ramdisk Image',
    # 'docker': 'Docker',
    'iso': 'ISO - Optical Disk Image',
    # 'ova': 'OVA - Open Virtual Appliance',
    'ploop': 'PLOOP - Virtuozzo/Parallels Loopback Disk',
    'qcow2': 'QCOW2 - QEMU Emulator',
    'raw': 'Raw',
    'vdi': 'VDI - Virtual Disk Image',
    'vhd': 'VHD - Virtual Hard Disk',
    'vhdx': 'VHDX - Large Virtual Hard Disk',
    'vmdk': 'VMDK - Virtual Machine Disk',
}
OPENSTACK_IMAGE_DISK_FORMAT = {
    # '-': 'Select format',
    'aki': 'AKI - Amazon 内核镜像',
    'ami': 'AMI - Amazon 机器镜像',
    'ari': 'ARI - Amazon Ramdisk 镜像',
    # 'docker': 'Docker',
    'iso': 'ISO - 光盘镜像',
    # 'ova': 'OVA - 开放式虚拟设备',
    'ploop': 'PLOOP - Virtuozzo/并行环回磁盘',
    'qcow2': 'QCOW2 - QEMU 模拟器',
    'raw': '原始',
    'vdi': 'VDI - 虚拟磁盘镜像',
    'vhd': 'VHD - 虚拟硬盘',
    'vhdx': 'VHDX - 大型虚拟硬盘',
    'vmdk': 'VMDK - 虚拟机磁盘',
}

status_msg = {
    200: "调用成功",
    201: "用户新建或者修改数据成功",
    202: "表示请求已经进入后台排队（异步任务）",
    400: "请求有错误",
    401: "用户没有权限",
    403: "禁止访问",
    404: "地址错误/资源未找到",
    406: "用户请求的格式不可得",
    410: "用户请求的资源被永久删除",
    422: "创建对象时发生验证错误",
    500: "内部服务错误",
    502: "网关错误",
    301: "永久重定向",
    302: "临时重定向"
}

ExecStatusDICT = {
    -1: "离线",
    1: "在线",
    0: "备用",
}

# 0: "CentOS"
# 1: "Debian"
# 2: "Ubuntu"
# 3: "Fedora"
# 4: "SUSE"
# 5: "Windows"
# 6: "RHEL"
# 7: "FreeBSD"
# 8: "Oracle Linux"
# 9: "Others"

# 操作系统下拉框
IMAGE_OS_SELECT = {
    "CentOS": "CentOS",
    "Debian": "Debian",
    "Ubuntu": "Ubuntu",
    "Fedora": "Fedora",
    "Windows": "Windows",
    "RHEL": "RHEL",
    "Oracle Linux": "Oracle Linux",
    "Others": "Others",
}

# 负载均衡算法
LB_ALGORITHM = {
    "循环": "ROUND_ROBIN",
    "最少连接数": "LEAST_CONNECTIONS",
    "源IP": "SOURCE_IP",
    "源IP端口": "SOURCE_IP_PORT",
}

# 负载均衡资源池协议，池及其成员侦听的协议
LB_PROTOCOL = ["HTTP", "HTTPS", "PROXY", "PROXYV2", "SCTP", "TCP", "UDP"]

# 负载均衡资源池会话持久性方法
LB_SESSION_PERSISTENCE = ["None", "APP_COOKIE", "HTTP_COOKIE", "SOURCE_IP"]

# 健康监控器的类型
LB_HEALTH = ["HTTP", "HTTPS", "PING", "SCTP", "TCP", "TLS-HELLO", "UDP-CONNECT"]
