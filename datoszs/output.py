from spiderpig.msg import print_info
import os
import spiderpig as sp


@sp.configured()
def save_csv(data, filename, output_dir=None):
    filename = os.path.join(output_dir, '{}.csv'.format(filename))
    data.to_csv(filename, index=False, sep=';')
    print_info('Saving data to {}'.format(filename))
