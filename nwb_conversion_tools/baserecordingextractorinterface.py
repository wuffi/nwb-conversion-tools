"""Authors: Cody Baker and Ben Dichter."""
import spikeextractors as se
from pynwb.device import Device
from pynwb.ecephys import ElectrodeGroup, ElectricalSeries

from .basedatainterface import BaseDataInterface
from .utils import get_base_schema, get_schema_from_method_signature, \
    get_schema_from_hdmf_class


class BaseRecordingExtractorInterface(BaseDataInterface):
    RX = None

    @classmethod
    def get_input_schema(cls):
        return get_schema_from_method_signature(cls.RX)

    def __init__(self, **input_args):
        super().__init__(**input_args)
        self.recording_extractor = self.RX(**input_args)

    def get_metadata_schema(self):
        metadata_schema = get_base_schema()

        # ideally most of this be automatically determined from pynwb docvals
        metadata_schema['properties'].update(
            Device=get_schema_from_hdmf_class(Device),
            ElectrodeGroup=get_schema_from_hdmf_class(ElectrodeGroup),
            ElectricalSeries=get_schema_from_hdmf_class(ElectricalSeries)
        )
        required_fields = ['Device', 'ElectrodeGroup', 'ElectricalSeries']
        metadata_schema['required'] += required_fields

        return metadata_schema

    def convert_data(self, nwbfile, metadata_dict: None, stub_test=False):
        if stub_test:
            num_frames = 100
            test_ids = self.recording_extractor.get_channel_ids()
            end_frame = min([num_frames, self.recording_extractor.get_num_frames()])

            stub_recording_extractor = se.SubRecordingExtractor(self.recording_extractor,
                                                                channel_ids=test_ids,
                                                                start_frame=0,
                                                                end_frame=end_frame)
        else:
            stub_recording_extractor = self.recording_extractor

        if metadata_dict is not None and 'Ecephys' in metadata_dict and 'subset_channels' in metadata_dict['Ecephys']:
            recording_extractor = se.SubRecordingExtractor(stub_recording_extractor,
                                                           channel_ids=metadata_dict['Ecephys']['subset_channels'])
        else:
            recording_extractor = stub_recording_extractor

        se.NwbRecordingExtractor.write_recording(recording_extractor,
                                                 nwbfile=nwbfile,
                                                 metadata=metadata_dict)
