from .config import get_config
import os


def get_filename(filename):
    ssh_host = get_config('ssh.host')
    if ssh_host is None:
        return filename
    else:
        data_dir = get_config('data.dir', required=True)
        local_copy = '{}/local_copy/{}'.format(data_dir, filename)
        if not os.path.exists(local_copy):
            dirs = os.path.dirname(local_copy)
            if not os.path.exists(dirs):
                os.makedirs(dirs)
            os.system("scp {}:{} {}".format(ssh_host, filename, local_copy))
            print("scp {}:{} {}".format(ssh_host, filename, local_copy))
        return local_copy
