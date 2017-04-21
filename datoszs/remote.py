import os
import spiderpig as sp


@sp.configured()
def get_filename(filename, ssh_host=None, data_dir=None):
    if ssh_host is None:
        return filename
    else:
        local_copy = '{}/local_copy/{}'.format(data_dir, filename)
        if not os.path.exists(local_copy):
            dirs = os.path.dirname(local_copy)
            if not os.path.exists(dirs):
                os.makedirs(dirs)
            os.system("scp {}:{} {}".format(ssh_host, filename, local_copy))
        return local_copy
