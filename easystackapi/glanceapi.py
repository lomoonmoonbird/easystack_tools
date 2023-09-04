# from easystackapi.novaapi import get_flavor
from easystackapi import novaapi
Version = '2'
# from easystackapi.utils.easy_request import easystack_api
from easyopenapi.stack_request import StackApi
from easyopenapi.defaults import username, password, project_domain_name
easystack_api = StackApi

def upload_image_mata_data(url,data,header=None,request=None):
    easystack_api.ChangeUrl('Image')
    if header:
        easystack_api.headers.update(header)
    return easystack_api.post(url=url,data=data,request=request)

def upload_image_file(url,data,header,request=None):
    easystack_api.ChangeUrl('Image')
    if header:
        easystack_api.headers.update(header)
    return easystack_api.put(url=url, data=data,isJson=False,request=request)

def delete_image_mata_data(url,header,request=None):
    easystack_api.ChangeUrl('Image')
    if header:
        easystack_api.headers.update(header)
    return easystack_api.delete(url=url,request=request)

def get_images(request=None):
    easystack_api.ChangeUrl('Image')
    # 获取images列表
    images = easystack_api.get('/v2/images',request=request)
    return images['images']

def delete_image(image_id,request=None):
    easystack_api.ChangeUrl('Image')
    # 获取images列表
    images, code = easystack_api.delete('/v2/images/'+image_id,request=request)
    return images, code


def get_parseimagestag(tags):
    labels = ['image_os', 'image_type', 'image_arch', 'image_webserver', 'app_version', 'imageisagent', 'flavor', 'imageDeploy', 'image_server_port','disk_format' ]
    temp = {'image_os':'', 'image_type':'', 'image_arch':'', 'image_webserver':'', 'app_version':"", 'imageisagent':'', 'imageDeploy':'', 'flavor':'', 'image_server_port': 0,'disk_format':'' }
    for i in labels:
        if i == 'image_server_port':
            temp[i] = 0
        else:
            temp[i] = ''
        for tag in tags:
            index = -1
            index = tag.find(i)
            if index >= 0:
                temp[i] = tag[len(i)+1:len(tag)]
    return(temp)



def get_imageslist(request=None):
    easystack_api.ChangeUrl('Image')
    # 获取images列表
    images = easystack_api.get('/v2/images',request=request)
    # todo 等easystack确认flavor接口内容
    flavor = novaapi.get_flavor(request=request)[0]
    imageslist = []
    for image in images['images']:
        temp = {}
        #temp['domain']=image.domain
        temp['image_name'] = image['name']
        temp['image_id']  = image['id']
        temp['description']  = image['description'] if 'description' in image else ''
        temp['filepath'] = image['file']
        temp['image_size']  = image['size']
        temp['image_status'] = image['status']
        tag = get_parseimagestag(image['tags'])
        temp['image_os'] = tag['image_os']
        temp['image_type'] = tag['image_type']
        temp['image_arch'] = tag['image_arch']
        temp['image_webserver'] =tag['image_webserver']
        temp['app_version'] = tag['app_version']
        temp['imageisagent'] = False
        temp['image_server_port'] = tag['image_server_port']
        temp['disk_format'] = tag['disk_format']
        if(tag['imageisagent'] == 'true') or (tag['imageisagent'] == 'True'):
            temp['imageisagent'] = True

        if temp['imageisagent']==False:
            temp['imageDeploy']=0
        else:
            temp['imageDeploy']=tag['imageDeploy']
        # todo 等easystack确认flavor接口内容
        temp['flavor'] = tag['flavor']
        if tag['flavor'] == '':
            temp['flavor'] = flavor['flavor_name']
        imageslist.append(temp)
    return imageslist

def del_image_tags(image_id,tags,request=None):
    easystack_api.ChangeUrl('Image')
    from easyopenapi import exceptions
    try:
        easystack_api.delete('/v2/images/'+image_id+'/tags/'+tags,request=request)
    except exceptions.HTTP404:
        return None
    return None

def add_image_tags(image_id,tags,request=None):
    easystack_api.ChangeUrl('Image')
    from urllib.parse import urlencode
    encode_res = urlencode({'k': tags}, encoding='utf-8')
    keyword = encode_res.split('=')[1]
    ret = easystack_api.put('/v2/images/'+image_id+'/tags/'+keyword,request=request)
    return ret

def get_imagebynane(name=None,id=None, request=None):
    easystack_api.ChangeUrl('Image')
    # 获取images列表
    images = easystack_api.get('/v2/images', request=request)
    # 等easystack确认flavor接口内容
    flavor = novaapi.get_flavor(request=request)[0]
    temp = {}
    for image in images['images']:
        if temp:
            break
        if name:
            if image['name'] != name:
                continue
        if id:
            if image['id'] != id:
                continue
        # temp['domain']=image.domain
        temp['image_name'] = image['name']
        temp['image_id'] = image['id']
        temp['filepath'] = image['file']
        temp['image_size'] = image['size']
        temp['image_status'] = image['status']
        tag = get_parseimagestag(image['tags'])
        temp['image_os'] = tag['image_os']
        temp['image_type'] = tag['image_type']
        temp['image_arch'] = tag['image_arch']
        temp['image_webserver'] = tag['image_webserver']
        temp['app_version'] = tag['app_version']
        temp['imageisagent'] = False
        temp['image_server_port'] = tag['image_server_port']
        if (tag['imageisagent'] == 'true') or (tag['imageisagent'] == 'True'):
            temp['imageisagent'] = True

        if temp['imageisagent'] == False:
            temp['imageDeploy'] = 0
        else:
            temp['imageDeploy'] = tag['imageDeploy']
        # 等easystack确认flavor接口内容
        temp['flavor'] = tag['flavor']
        if tag['flavor'] == '':
            temp['flavor'] = flavor['flavor_name']
    return temp

