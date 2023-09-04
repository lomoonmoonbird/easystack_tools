# from easystackapi.utils.easy_request import easystack_api
from easyopenapi.stack_request import StackApi
from easyopenapi.defaults import username, password, project_domain_name
easystack_api = StackApi

def get_doaminsfull(request=None):
    easystack_api.ChangeUrl()
    ret, code = easystack_api.get('/v3/domains', request=request)
    domains = ret
    # for domain in domains:
    #     doaminlist.append(domain.to_dict())
    return domains['domains']


def get_usersfullbydoamin(domainid, request=None):
    easystack_api.ChangeUrl()
    users, code = easystack_api.get('/v3/users', request=request)
    userlist = []
    for user in users['users']:
        if user['email'] is not None and user['domain_id'] == domainid:
            userlist.append(user)
    return userlist

def get_projectfullsbydoamin(domainid, request=None):
    easystack_api.ChangeUrl()
    projects, code = easystack_api.get('/v3/projects', request=request)
    projectlist = []
    for project in projects['projects']:
        if project['domain_id'] == domainid:
            projectlist.append(project)
    return projectlist



def get_doamins(request=None):
    doaminlist = []
    easystack_api.ChangeUrl()
    domains = easystack_api.get('/v3/domains',request)
    # domains = keystone.domains.list()
    users = get_usres()
    projects = get_projects()
    for domain in domains['domains']:
        tmp = {}
        tmp['domain_name'] = domain['name']
        tmp['domain_id'] = domain['id']
        tmp['domain_status'] = domain['enabled']
        user_list = []
        for user in users:
            if user['domain_id'] == tmp['domain_id']:
                user_list.append(user)
        project_list = []
        for project in projects:
            if project['domain_id'] == tmp['domain_id']:
                project_list.append(project)
        tmp['users'] = user_list
        tmp['projects'] = project_list
        doaminlist.append(tmp)
    return doaminlist

def update_domain(domain_id,enable=False,name=None,description=None,request=None):
    data = {
        'domain':{
        }
    }
    if name:
        data['domain']['name'] = name
    if enable:
        data['domain']['enable'] = enable
    if description:
        data['domain']['description'] = description
    return easystack_api.patch(url='/v3/domains/'+domain_id,data=data,request=request)

def create_domain(enable=False,name=None,description=None,request=None):
    data = {
        'domain':{
        }
    }
    if name:
        data['domain']['name'] = name
    if enable:
        data['domain']['enable'] = enable
    if description:
        data['domain']['description'] = description
    return easystack_api.post(url='/v3/domains/',data=data,request=request)

def create_user(name,email, description,password,enabled,domain_id,request=None):
    data = {
    "user": {
        "domain_id": domain_id,
        "enabled": enabled,
        "name": name,
        "password": password,
        "description": description,
        "email": email,
        }
    }
    return easystack_api.post(url='/v3/users/',data=data,request=request)

def add_domain_user_role(domain_id,user_id,role_id,request=None):
    return easystack_api.put('/v3/domains/{domain_id}/users/{user_id}/roles/{role_id}'.format(domain_id=domain_id,user_id=user_id,role_id=role_id,request=request))


def delete_domain(domain_id,request=None):
    return easystack_api.delete(url='/v3/domains/'+domain_id,request=request)

def delete_user(user_id,request=None):
    return easystack_api.delete(url='/v3/users/'+user_id,request=request)



def get_user_list(domain_id=None,request=None):
    if domain_id:
        user_list = get_usersbydoamin(domain_id,request=request)
    else:
        easystack_api.ChangeUrl()
        users, code = easystack_api.get('/v3/users',request=request)
        # domains = keystone.domains.list()
        user_list = users['users']
    return user_list

def get_roles(request=None):
    easystack_api.ChangeUrl()
    roles, code = easystack_api.get('/v3/roles',request=request)
    roles_list = roles['roles']
    return roles_list

def get_usersbydoamin(domainid,request=None):
    users = get_usres(request=request)
    userlist = []
    for user in users:
        if user['email'] is not None and user['domain_id'] == domainid:
            tmp = {}
            tmp['name'] = user['name']
            tmp['id'] = user['id']
            userlist.append(tmp)
    return userlist


def get_projectsbydoamin(domainid, request=None):
    projectlist = []
    projects = get_projects(request=request)
    for project in projects:
        if project['domain_id'] == domainid:
            tmp = {}
            tmp['name'] = project['name']
            tmp['id'] = project['id']
            projectlist.append(tmp)
    return projectlist



def get_doaminbyid(domainid,request=None):
    easystack_api.ChangeUrl()
    domains = easystack_api.get(url='/v3/domains',request=request)
    # domains = keystone.domains.list()
    tmp = {}
    for domain in domains.get('domains', []):
        if domain['id'] == domainid:
            tmp['domain_name'] = domain['name']
            tmp['domain_id'] = domain['id']
            tmp['domain_status'] = domain['enabled']
    return tmp




def get_doaminbyname(domainname, request=None):
    easystack_api.ChangeUrl()
    domains = easystack_api.get('/v3/domains', request=request)
    # domains = keystone.domains.list()
    users = get_usres(request=request)
    projects = get_projects(request=request)
    tmp = {}
    for domain in domains['domains']:
        if domain['name'] == domainname:
            tmp['domain_name'] = domain['name']
            tmp['domain_id'] = domain['id']
            tmp['domain_status'] = domain['enabled']
            user_list = []
            for user in users:
                if user['domain_id'] == tmp['domain_id']:
                    user_list.append(user)
            project_list = []
            for project in projects:
                if project['domain_id'] == tmp['domain_id']:
                    project_list.append(project)
            tmp['users'] = user_list
            tmp['projects'] = project_list
            return tmp


def get_projects(request=None):
    projectlist = []
    # projects = keystone.projects.list(domainid)
    easystack_api.ChangeUrl()
    projects = easystack_api.get('/v3/projects', request=request)
    for project in projects['projects']:
            tmp = {}
            tmp['name'] = project['name']
            tmp['id'] = project['id']
            tmp['domain_id'] = project['domain_id']
            projectlist.append(tmp)
    return projectlist

def get_usres(request=None):
    userlist = []
    easystack_api.ChangeUrl()
    users = easystack_api.get('/v3/users', request=request)
    for user in users['users']:
            tmp = {}
            tmp['name'] = user.get('name', '')
            tmp['id'] = user.get('id', '')
            tmp['domain_id'] = user.get('domain_id', '')
            tmp['email'] = user.get('email', '')
            userlist.append(tmp)
    return userlist