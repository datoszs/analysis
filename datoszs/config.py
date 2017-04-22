import spiderpig as sp


@sp.configured()
def storage_path(storage_path=None):
    return storage_path


@sp.configured()
def host_name(host_name='devel.cestiadvokati.cz'):
    return host_name
