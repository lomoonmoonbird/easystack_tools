# coding = utf-8
from pprint import pprint

# from easystackapi.utils.easy_request import easystack_api
from easystackapi.utils.commonvariable import project_id, tenant_id
from easyopenapi.stack_request import StackApi
from easyopenapi.defaults import username, password, project_domain_name
easystack_api = StackApi

Version = '3'


def get_volumes(request=None):
    easystack_api.ChangeUrl('Cinder')
    project_id if project_id is None else tenant_id
    url = project_id + '/volumes/detail'
    volumes, code = easystack_api.get(url, request=request)
    # cinder = ret
    print(volumes)
    return volumes
    # print(dir(cinder))
    # volume = cinder.volumes.create(size=10, volume_type='volume_type')
    # cinder.volumes.attach(volume, '2355d095-c150-4900-9138-517b3766c891','/dev/vdb')
    # nova.volumes.create_server_volume('2355d095-c150-4900-9138-517b3766c891', volume.id)
    # volumes = cinder.volumes.list()
    # print(dir(cinder.volumes))
    # for volume in volumes:
    #     print(volume.to_dict())
    #     cinder.volumes.detach(volume)
    #     cinder.volumes.delete(volume)
    #
    # volume_types = cinder.volume_types.list()
    # for volume_type in volume_types:
    #     print(volume_type.to_dict())


def get_volume(volume_id, request=None):
    easystack_api.ChangeUrl('Cinder')
    project_id if project_id is None else tenant_id
    url = project_id + '/volumes/' + volume_id
    ret, code = easystack_api.get(url, request=request)
    if type(ret) is dict:
        if 'itemNotFound' in ret.keys():
            return ret
        else:
            volume = ret['volume']
            return volume
    else:
        return ret





def create_volume(size, volume_type=None, name=None, project_id=None, request=None):
    easystack_api.ChangeUrl('Cinder')
    project_id if project_id is None else tenant_id
    url = project_id + '/volumes'
    data = {
        "volume": {
            'size': size,
            'volume_type': volume_type if volume_type is not None else 'hdd',
            'name': name,
            'project_id': project_id
        }
    }
    ret, code = easystack_api.post(url, data, request=request)
    return ret


def delete_volume(volume_id,project_id=None, request=None):
    # 删除卷之前，先卸载云硬盘
    deattach_volume(volume_id)
    easystack_api.ChangeUrl('Cinder')
    project_id = project_id if project_id is not None else tenant_id
    url = project_id + '/volumes/' + volume_id

    ret, code = easystack_api.delete(url, request=request)
    return ret


def attach_volume(instance_id, volume_id,project_id=None, request=None):
    easystack_api.ChangeUrl('Cinder')
    project_id = project_id if project_id is not None else tenant_id
    url = project_id + '/volumes/' + volume_id + '/action'
    data = {
        "os-attach": {
            "instance_uuid": instance_id,
        }
    }

    ret, code = easystack_api.post(url, data, request=request)
    return ret


def deattach_volume(volume_id, request=None):
    easystack_api.ChangeUrl('Cinder')
    project_id if project_id is None else tenant_id
    url = project_id + '/volumes/' + volume_id + '/action'
    # 通过 volume_id 获取 accachment_id
    volumeinfo = get_volume(volume_id, request=request)
    if 'attachments' in volumeinfo and len(volumeinfo['attachments']) > 0:
        for v in volumeinfo['attachments']:
            if volume_id == v['volume_id']:
                attachment_id = v['attachment_id']
                data = {
                    "os-detach": {
                        "attachment_id": attachment_id,
                    }
                }

                ret, code = easystack_api.post(url, data)


    else:
        ret = {"data": "该卷未挂载到实例,不需要解绑"}

    return ret