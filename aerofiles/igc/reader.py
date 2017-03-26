class Reader:
    """
    A reader for the IGC flight log file format.

    see http://carrier.csi.cam.ac.uk/forsterlewis/soaring/igc_file_format/igc_format_2008.html
    """

    def __init__(self):
        self.reader = None

    def read(self, fp):

        self.reader = LowLevelReader(fp)

        logger_id, task, header, fix_record_extensions, k_record_extensions = (None,) * 5

        fix_records = []
        dgps_records = []
        event_records = []
        satellite_records = []
        security_records = []
        k_records = []
        comment_records = []

        for line, error in self.reader:

            if error:
                raise InvalidIGCFileError

            line_type = line['type']

            if line_type == 'A':
                logger_id = line['value']
            elif line_type == 'B':
                fix_records.append(line['value'])
            elif line_type == 'C':
                task = line['value']
            elif line_type == 'D':
                dgps_records.append(line['value'])
            elif line_type == 'E':
                event_records.append(line['value'])
            elif line_type == 'F':
                satellite_records.append(line['value'])
            elif line_type == 'G':
                security_records.append(line['value'])
            elif line_type == 'H':
                header = line['value']
            elif line_type == 'I':
                fix_record_extensions = line['value']
            elif line_type == 'J':
                k_record_extensions = line['value']
            elif line_type == 'K':
                k_records.append(line['value'])
            elif line_type == 'L':
                comment_records.append(line['value'])

        return dict(logger_id=logger_id,                            # A record
                    fix_records=fix_records,                        # B records
                    task=task,                                      # C records
                    dgps_records=dgps_records,                      # D records
                    event_records=event_records,                    # E records
                    satellite_records=satellite_records,            # F records
                    security_records=security_records,              # G records
                    header=header,                                  # H records
                    fix_record_extensions=fix_record_extensions,    # I record
                    k_record_extensions=k_record_extensions,        # J record
                    k_records=k_records,                            # K records
                    comment_records=comment_records,                # L records
                    )


class LowLevelReader:
    """
    A low level reader for the IGC flight log file format.

    see http://carrier.csi.cam.ac.uk/forsterlewis/soaring/igc_file_format/igc_format_2008.html
    """

    def __init__(self, fp):
        self.fp = fp
        self.line_number = 0

    def __iter__(self):
        return self.next()

    def next(self):
        for line in self.fp:
            self.line_number += 1

            try:
                result = self.parse_line(line)
                if result:
                    yield (result, None)

            except Exception as e:
                e.line_number = self.line_number
                yield (None, e)

    def parse_line(self, line):

        record_type = line[0]
        record_value = line[1::]
        decoder_name = self.get_decoder_method(record_type)
        decoder = getattr(self, decoder_name)

        return decoder(record_value)

    def get_decoder_method(self, record_type):
        decoder = getattr(self, 'decode_{}_record'.format(record_type))
        if not decoder:
            raise ValueError('Unknown record type')

    @staticmethod
    def decode_A_record(record_value):
        id_addition = None if len(record_value) == 6 else record_value[6:]
        value = {
            'manufacturer': record_value[0:3],
            'id': record_value[3:6],
            'id-addition': id_addition
        }
        return {'type': 'A', 'value': value}

    @staticmethod
    def decode_B_record(record_value):
        # todo
        value = None
        return {'type': 'B', 'value': value}

    def decode_C_record(self, record_value):
        # todo
        value = None
        return {'type': 'C', 'value': value}

    def decode_D_record(self, record_value):
        # todo
        value = None
        return {'type': 'D', 'value': value}

    def decode_E_record(self, record_value):
        # todo
        value = None
        return {'type': 'E', 'value': value}

    def decode_F_record(self, record_value):
        # todo
        value = None
        return {'type': 'F', 'value': value}

    def decode_G_record(self, record_value):
        # todo
        value = None
        return {'type': 'G', 'value': value}

    def decode_H_record(self, record_value):
        # todo
        value = None
        return {'type': 'H', 'value': value}

    def decode_I_record(self, record_value):
        # todo
        value = None
        return {'type': 'I', 'value': value}

    def decode_J_record(self, record_value):
        # todo
        value = None
        return {'type': 'J', 'value': value}

    def decode_K_record(self, record_value):
        # todo
        value = None
        return {'type': 'K', 'value': value}

    def decode_L_record(self, record_value):
        # todo
        value = None
        return {'type': 'L', 'value': value}


class InvalidIGCFileError(Exception):
    pass
