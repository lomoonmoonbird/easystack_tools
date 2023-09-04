# coding = utf-8
#auth_url = 'http://172.168.108.88:35357/v3'
# auth_url = 'http://controller:5000/v3'
# auth_url = 'http://keystone.openstack.svc.cluster.local/v3'


from easyopenapi import defaults

EASYSTACCK_KEYSTONE_HOST = defaults.EASYSTACCK_0CTAVIA_HOST
EASYSTACCK_GLANCE_HOST = defaults.EASYSTACCK_GLANCE_HOST
EASYSTACCK_NOVA_HOST = defaults.EASYSTACCK_NOVA_HOST
EASYSTACCK_CINDER_HOST = defaults.EASYSTACCK_CINDER_HOST
EASYSTACCK_NEUTRON_HOST = defaults.EASYSTACCK_NEUTRON_HOST




username = defaults.username
user_domain_name = defaults.user_domain_name
password = defaults.password
networkzone = 'nova'
externalnetworkname = 'provider'
tenant_id = defaults.tenant_id
project_id = defaults.project_id
project_name = defaults.project_name
project_domain_name =defaults.project_domain_name
security_group_name = 'exec-security'
zone_name = 'default_az'
# intranetname = 'selfservice'  # =slice.intranetname
# router_id = '9de80e3d-aa11-4ce4-95b1-e90e35dc645f'  # 实际查找确定补充
default_network_type = 'vxlan'
ioproxy_ip = '192.168.0.17'
left_bracket_ip = ''
right_bracket_ip = ''
feedback_ip = ''

feedback_url="127.0.0.1"
feedback_user='root'
feedback_passwd='123456'
feedback_dbname='feedback'





#预先注册控制节点OS信息
#
# OS_Types = {
#             "node-1.domain.tld": "CentOS",
#             "node-2.domain.tld": "Redhat",
#             'node-3.domain.tld': "Ubuntu",
#           }
OS_Types = {
            # "compute03": "CentOS",
            "compute-hg": "Ubuntu",
            # 'compute-kp': "CentOS",
            "compute-x86": "CentOS",
          }