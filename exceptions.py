class CloudManageError(Exception):
    pass
class CloudControlError(Exception):
    pass

class NotAuthorized(CloudManageError):
    pass

class CreateMimicError(CloudControlError):
    pass
class DeleteMimicError(CloudControlError):
    pass

if __name__ == '__main__':
    try:
        raise NotAuthorized('未授权或权限已过期')
    except Exception as e:
        print(e)