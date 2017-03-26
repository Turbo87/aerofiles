import datetime


class Reader:
    """
    A reader for the IGC flight log file format.

    see http://carrier.csi.cam.ac.uk/forsterlewis/soaring/igc_file_format/igc_format_2008.html
    """

    def __init__(self):
        self.reader = None

    def read(self, fp):

        self.reader = LowLevelReader(fp)

        logger_id = None
        task = None
        fix_record_extensions = None
        k_record_extensions = None
        header = {}
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
                fix_records.append(line['value'])  # todo
            elif line_type == 'C':
                task = line['value']  # todo
            elif line_type == 'D':
                dgps_records.append(line['value'])  # todo
            elif line_type == 'E':
                event_records.append(line['value'])  # todo
            elif line_type == 'F':
                satellite_records.append(line['value'])  # todo
            elif line_type == 'G':
                security_records.append(line['value'])  # todo
            elif line_type == 'H':
                header.update(line['value'])
            elif line_type == 'I':
                fix_record_extensions = line['value']  # todo
            elif line_type == 'J':
                k_record_extensions = line['value']  # todo
            elif line_type == 'K':
                k_records.append(line['value'])  # todo
            elif line_type == 'L':
                comment_records.append(line['value'])  # todo

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
        decoder = self.get_decoder_method(record_type)

        return decoder(line)

    def get_decoder_method(self, record_type):
        decoder = getattr(self, 'decode_{}_record'.format(record_type))
        if not decoder:
            raise ValueError('Unknown record type')

        return decoder

    @staticmethod
    def decode_A_record(line):
        id_addition = None if len(line) == 7 else line[7:].strip()
        value = {
            'manufacturer': line[0:3],
            'id': line[3:6],
            'id-addition': id_addition
        }
        return {'type': 'A', 'value': value}

    @staticmethod
    def decode_B_record(line):
        # todo
        value = None
        return {'type': 'B', 'value': value}

    @staticmethod
    def decode_C_record(line):
        # todo
        value = None
        return {'type': 'C', 'value': value}

    @staticmethod
    def decode_D_record(line):
        # todo
        value = None
        return {'type': 'D', 'value': value}

    @staticmethod
    def decode_E_record(line):
        # todo
        value = None
        return {'type': 'E', 'value': value}

    @staticmethod
    def decode_F_record(line):
        # todo
        value = None
        return {'type': 'F', 'value': value}

    @staticmethod
    def decode_G_record(line):
        # todo
        value = None
        return {'type': 'G', 'value': value}

    @staticmethod
    def decode_H_record(line):

        source = line[1]

        # three letter code
        tlc = line[2:5]

        if tlc == 'DTE':
            value = LowLevelReader.decode_H_utc_date(line)
        elif tlc == 'FXA':
            value = LowLevelReader.decode_H_fix_accuracy(line)
        elif tlc == 'PLT':
            value = LowLevelReader.decode_H_pilot(line)
        elif tlc == 'CM2':
            value = LowLevelReader.decode_H_second_pilot(line)
        elif tlc == 'GTY':
            value = LowLevelReader.decode_H_glider_model(line)
        elif tlc == 'GID':
            value = LowLevelReader.decode_H_glider_registration(line)
        elif tlc == 'DTM':
            value = LowLevelReader.decode_H_gps_datum(line)
        elif tlc == 'RFW':
            value = LowLevelReader.decode_H_firmware_revision(line)
        elif tlc == 'RHW':
            value = LowLevelReader.decode_H_hardware_revision(line)
        elif tlc == 'FTY':
            value = LowLevelReader.decode_H_manufacturer_model(line)
        elif tlc == 'GPS':
            value = LowLevelReader.decode_H_gps_sensor(line)
        elif tlc == 'PRS':
            value = LowLevelReader.decode_H_pressure_sensor(line)
        elif tlc == 'CID':
            value = LowLevelReader.decode_H_competition_id(line)
        elif tlc == 'CCL':
            value = LowLevelReader.decode_H_competition_class(line)
        else:
            raise ValueError('Invalid h-record')

        return {'type': 'H', 'value': value}

    @staticmethod
    def decode_H_utc_date(line):
        dd = int(line[5:7])
        mm = int(line[7:9])
        yy = int(line[9:11])

        current_year_yyyy = datetime.date.today().year
        current_year_yy = current_year_yyyy % 100
        current_century = current_year_yyyy - current_year_yy
        yyyy = current_century + yy if yy < current_year_yy else current_century - 100 + yy

        return {'utc_date': datetime.date(yyyy, mm, dd)}

    @staticmethod
    def decode_H_fix_accuracy(line):
        fix_accuracy = line[5:].strip()
        return {'fix_accuracy': None} if fix_accuracy == '' else {'fix_accuracy': int(fix_accuracy)}

    @staticmethod
    def decode_H_pilot(line):
        pilot = line[11:].strip()
        return {'pilot': None} if pilot == '' else {'pilot': pilot}

    @staticmethod
    def decode_H_second_pilot(line):
        second_pilot = line[11:].strip()
        return {'second_pilot': None} if second_pilot == '' else {'second_pilot': second_pilot}

    @staticmethod
    def decode_H_glider_model(line):
        glider_model = line[16:].strip()
        return {'glider_model': None} if glider_model == '' else {'glider_model': glider_model}

    @staticmethod
    def decode_H_glider_registration(line):
        glider_registration = line[14:].strip()
        if glider_registration == '':
            return {'glider_registration': None}
        else:
            return {'glider_registration': glider_registration}

    @staticmethod
    def decode_H_gps_datum(line):
        gps_datum = line[17:].strip()
        return {'gps_datum': None} if gps_datum == '' else {'gps_datum': gps_datum}

    @staticmethod
    def decode_H_firmware_revision(line):
        firmware_revision = line[21:].strip()
        return {'firmware_revision': None} if firmware_revision == '' else {'firmware_revision': firmware_revision}

    @staticmethod
    def decode_H_hardware_revision(line):
        hardware_revision = line[21:].strip()
        return {'hardware_revision': None} if hardware_revision == '' else {'hardware_revision': hardware_revision}

    @staticmethod
    def decode_H_manufacturer_model(line):
        manufacturer = None
        model = None
        manufacturer_model = line[12:].strip().split(',')
        if manufacturer_model[0] != '':
            manufacturer = manufacturer_model[0]
        if len(manufacturer_model) == 2 and manufacturer_model[1].lstrip() != '':
            model = manufacturer_model[1]
        return {'manufacturer': manufacturer,
                'model': model}

    @staticmethod
    def decode_H_gps_sensor(line):

        # can contain string in maxalt? (YX.igc)
        # HFGPS:uBLOX_TIM-LP,16,max9000m

        manufacturer = None
        model = None
        channels = None
        max_alt = None

        # some IGC files use colon, others don't
        if line[5] == ':':
            gps_sensor = line[6:].lstrip().split(',')
        else:
            gps_sensor = line[5:].split(',')

        if len(gps_sensor) >= 1:
            manufacturer = gps_sensor[0] if gps_sensor[0] != '' else None
        if len(gps_sensor) >= 2:
            model = gps_sensor[1] if gps_sensor[1] != '' else None
        if len(gps_sensor) >= 3:
            channels = int(gps_sensor[2]) if gps_sensor[2] != '' else None
        if len(gps_sensor) == 4:
            max_alt = int(gps_sensor[3]) if gps_sensor[3] != '' else None

        return {'manufacturer': manufacturer,
                'model': model,
                'channels': channels,
                'max_alt': max_alt}

    @staticmethod
    def decode_H_pressure_sensor(line):

        # check whether pressure has same colon problem as gps_sensor

        # can contain string inside max alt? (YX.igc)
        # HFPRSPRESSALTSENSOR:INTERSEMA,MS5534A,max8000m

        manufacturer = None
        model = None
        max_alt = None

        # some IGC files use colon, others don't
        if line[19] == ':':
            pressure_sensor = line[20:].strip().split(',')
        else:
            pressure_sensor = line[19:].split(',')

        if len(pressure_sensor) >= 1:
            manufacturer = pressure_sensor[0] if pressure_sensor[0] != '' else None
        if len(pressure_sensor) >= 2:
            model = pressure_sensor[1] if pressure_sensor[1] != '' else None
        if len(pressure_sensor) == 3:
            max_alt = pressure_sensor[2] if pressure_sensor[2] != '' else None

        return {'manufacturer': manufacturer,
                'model': model,
                'max_alt': max_alt}

    @staticmethod
    def decode_H_competition_id(line):
        competition_id = line[19:].strip()
        return {'competition_id': None} if competition_id == '' else {'competition_id': competition_id}

    @staticmethod
    def decode_H_competition_class(line):
        competition_class = line[22:].strip()
        return {'competition_class': None} if competition_class == '' else {'competition_class': competition_class}

    @staticmethod
    def decode_I_record(line):
        # todo
        value = None
        return {'type': 'I', 'value': value}

    @staticmethod
    def decode_J_record(line):
        # todo
        value = None
        return {'type': 'J', 'value': value}

    @staticmethod
    def decode_K_record(line):
        # todo
        value = None
        return {'type': 'K', 'value': value}

    @staticmethod
    def decode_L_record(line):
        # todo
        value = None
        return {'type': 'L', 'value': value}


class InvalidIGCFileError(Exception):
    pass
