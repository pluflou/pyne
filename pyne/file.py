

import json
import os

import h5py
import numpy as np


class File:
    def __init__(self, directory):
        self.directory = directory
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)
        self.metadata_file = os.path.join(self.directory, 'meta.json')
        self.adc_file = os.path.join(self.directory, '{}.npz')

    def __bool__(self):
        return len(os.listdir(self.directory)) > 0

    def read_adc(self, name):
        f = np.load(self.adc_file.format(name))
        return f['bins'], f['counts'], f['energies']

    def save_adc(self, name, bins, counts, energies):
        np.savez(self.adc_file.format(name),
                 bins=bins, counts=counts, energies=energies)

    def read_attributes(self):
        with open(self.metadata_file, 'r') as f:
            return json.load(f)

    def save_attributes(self, attributes):
        with open(self.metadata_file, 'w') as f:
            json.dump(attributes, f, indent=4)

    def add_attribute(self, **kwargs):
        '''Add and save additional attributes through keyword arguments.'''
        attrs = self.read_attributes()
        attrs.update(kwargs)
        self.save_attributes(attrs)


class FileH5:
    def __init__(self, filename, access='r', *, open=False):
        self.filename = filename
        self.access = access
        if open:
            self.__enter__()

    def __enter__(self):
        self.f = h5py.File(self.filename, self.access)
        return self

    def __exit__(self, *args):
        self.close()

    def save_attributes(self, attributes):
        for key, value in attributes.items():
            self.f.attrs[key] = value

    def save_adc(self, name, bins, counts, energies):
        adc = self.f.create_group(name)
        adc.attrs['bins'] = bins
        adc.create_dataset('counts', data=counts, shape=(bins,))
        adc.create_dataset('energies', data=energies, shape=(bins,))

    def read_attributes(self):
        return {key: value for key, value in self.f.attrs.items()}

    def read_adc(self, name):
        adc_group = self.f[name]
        bins = adc_group.attrs['bins']
        counts = np.array(adc_group['counts'])
        energies = np.array(adc_group['energies'])
        return bins, counts, energies

    def close(self):
        self.f.close()
