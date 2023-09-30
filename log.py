from time import strftime


def LOG(info):
    print('[%s] %s\n' % (strftime('%H:%M:%S'), info))


def LOGI(info):
    print('[%s] \033[94m[INFO]\033[0m%s\n' % (strftime('%H:%M:%S'), info))


def LOGE(info):
    print('[%s] \033[91m[ERROR]\033[0m%s\n' % (strftime('%H:%M:%S'), info))


def LOGW(info):
    print('[%s] \033[93m[WARNING]\033[0m%s\n' % (strftime('%H:%M:%S'), info))


def LOGS(info):
    print('[%s] \033[92m[SUCCESS]\033[0m%s\n' % (strftime('%H:%M:%S'), info))
