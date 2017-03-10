

import os

from . import buffer
from . import detector
from . import file

date_format = '%Y-%m-%dT%H:%M:%S'


class Data:
    def __init__(self, buffer_file, output_file):
        self.buffer_file = buffer_file
        self.output_file = output_file
        self.run_information = {}
        self.adc = detector.DetectorArray(32, 4096)

    def load_data(self):
        if os.path.isfile(self.output_file):
            self.read_data()
        else:
            print('reading from buffer...this may take some time')
            self.read_buffer()
            self.convert_data()

    def read_buffer(self):
        with buffer.Buffer(self.buffer_file) as b:
            desc, info = b.process_buffer()
            self._get_start_information(desc, info)
            desc, info = b.process_buffer()
            while desc.type != buffer.Type.FOOTER:
                self._get_events(desc, info)
                desc, info = b.process_buffer()
            self._get_end_information(desc, info)

    def _get_start_information(self, desc, info):
        self.run_information['run_number'] = desc.run
        self.run_information['title'] = info.title
        self.run_information['start_time'] = info.date

    def _get_end_information(self, desc, info):
        assert self.run_information['run_number'] == desc.run
        assert self.run_information['title'] == info.title
        self.run_information['end_time'] = info.date

    def _get_events(self, desc, info):
        assert desc.events == len(info)
        for event in info:
            if event is not None and event != 0 and event.valid:
                self.adc.add_event(event.channel, event.value)

    def convert_data(self):
        self.adc.convert_detectors()
        start, end = (self.run_information['start_time'],
                      self.run_information['end_time'])
        self.run_information['run_time'] = (end - start).seconds
        self.run_information['start_time'] = start.strftime(date_format)
        self.run_information['end_time'] = end.strftime(date_format)

    def save_data(self):
        print('writing to {}...'.format(self.output_file))
        f = file.File(self.output_file, 'w')
        f.save_attributes(self.run_information)
        for adc in self.adc:
            f.save_adc(adc.name, adc.channels, adc.counts, adc.energies)
        f.close()

    def read_data(self):
        print('reading from {}...'.format(self.output_file))
        f = file.File(self.output_file, 'r')
        self.run_information = f.read_attributes()
        for adc in self.adc:
            adc.channels, adc.counts, adc.energies = f.read_adc(adc.name)
        f.close()
