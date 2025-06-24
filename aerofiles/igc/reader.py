import datetime

from aerofiles.util.timezone import TimeZoneFix


class Reader:
    """
    A reader for the IGC flight log file format.

    skip_duplicates flag removes trailing duplicate time entries

    Example:

    .. sourcecode:: python

        >>> with open('track.igc', 'r') as f:
        ...     parsed = Reader(skip_duplicates=True).read(f)

    """

    def __init__(self, skip_duplicates=False):
        self.reader = None
        self.skip_duplicates = skip_duplicates

    def read(self, file_obj):
        """
        Read the specified file object and return a dictionary with the parsed data.

        :param file_obj: a Python file object

        """
        self.reader = LowLevelReader(file_obj)

        logger_id = [[], None]
        fix_records = [[], []]
        task = [[], {"waypoints": []}]
        dgps_records = [[], []]
        event_records = [[], []]
        satellite_records = [[], []]
        security_records = [[], []]
        header = [[], {}]
        fix_record_extensions = [[], []]
        k_record_extensions = [[], []]
        k_records = [[], []]
        comment_records = [[], []]

        for record_type, line, error in self.reader:

            if record_type == 'A':
                if error:
                    logger_id[0].append(error)
                else:
                    logger_id[1] = line
            elif record_type == 'B':
                if error:
                    if MissingRecordsError not in fix_records[0]:
                        fix_records[0].append(MissingRecordsError)
                else:

                    # add MissingExtensionsError when fix_record_extensions contains error
                    if len(fix_record_extensions[0]) > 0 and MissingExtensionsError not in fix_records[0]:
                        fix_records[0].append(MissingExtensionsError)

                    fix_record = LowLevelReader.process_B_record(
                        line, fix_record_extensions[1])

                    # To create "datetime" we need a date. Take it from header or previous fix:
                    if len(fix_records[1]) == 0:
                        date = header[1]["utc_date"]
                    else:
                        previous_fix = fix_records[1][-1]
                        date = previous_fix["datetime"].date()
                        time = previous_fix["datetime"].time()
                        # If time of next fix is _before_ last fix, we are now on next day
                        if fix_record["time"] < time:
                            date = date + datetime.timedelta(days=1)
                        if fix_record["time"] == time and self.skip_duplicates:
                            continue

                    fix_record["datetime"] = datetime.datetime.combine(
                        date, fix_record["time"]).replace(tzinfo=TimeZoneFix(0))
                    if "time_zone_offset" in header[1]:
                        timezone = TimeZoneFix(header[1]["time_zone_offset"])
                        fix_record["datetime_local"] = fix_record["datetime"].astimezone(
                            timezone)

                    fix_records[1].append(fix_record)
            elif record_type == 'C':
                task_item = line

                if error:
                    if MissingRecordsError not in task[0]:
                        task[0].append(MissingRecordsError)
                else:
                    if task_item['subtype'] == 'task_info':
                        del task_item['subtype']
                        task[1]['waypoints'] = []
                        task[1].update(task_item)
                    elif task_item['subtype'] == 'waypoint_info':
                        del task_item['subtype']
                        task[1]['waypoints'].append(task_item)

            elif record_type == 'D':
                if error:
                    if MissingRecordsError not in dgps_records[0]:
                        dgps_records[0].append(MissingRecordsError)
                else:
                    dgps_records[1].append(line)
            elif record_type == 'E':
                if error:
                    if MissingRecordsError not in event_records[0]:
                        event_records[0].append(MissingRecordsError)
                else:
                    event_records[1].append(line)
            elif record_type == 'F':
                if error:
                    if MissingRecordsError not in satellite_records[0]:
                        satellite_records[0].append(MissingRecordsError)
                else:
                    satellite_records[1].append(line)
            elif record_type == 'G':
                if error:
                    if MissingRecordsError not in security_records[0]:
                        security_records[0].append(MissingRecordsError)
                else:
                    security_records[1].append(line)
            elif record_type == 'H':
                header_item = line

                if error:
                    if MissingRecordsError not in header[0]:
                        header[0].append(MissingRecordsError(error))
                else:
                    del header_item['source']
                    header[1].update(header_item)
            elif record_type == 'I':
                if error:
                    fix_record_extensions[0].append(error)
                else:
                    fix_record_extensions[1] = line
            elif record_type == 'J':
                if error:
                    k_record_extensions[0].append(error)
                else:
                    k_record_extensions[1] = line
            elif record_type == 'K':
                if error:
                    if MissingRecordsError not in k_records[0]:
                        k_records[0].append(MissingRecordsError)
                else:

                    # add MissingExtensionsError when fix_record_extensions contains error
                    if len(k_record_extensions[0]) > 0 and MissingExtensionsError not in k_records[0]:
                        k_records[0].append(MissingExtensionsError)

                    k_record = LowLevelReader.process_K_record(
                        line, k_record_extensions[1])
                    k_records[1].append(k_record)
            elif record_type == 'L':
                if error:
                    if MissingRecordsError not in comment_records[0]:
                        comment_records[0].append(MissingRecordsError)
                else:
                    comment_records[1].append(line)

        return dict(logger_id=logger_id,                            # A record
                    fix_records=fix_records,                        # B records
                    task=task,                                      # C records
                    dgps_records=dgps_records,                      # D records
                    event_records=event_records,                    # E records
                    satellite_records=satellite_records,            # F records
                    security_records=security_records,              # G records
                    header=header,                                  # H records
                    fix_record_extensions=fix_record_extensions,    # I records
                    k_record_extensions=k_record_extensions,        # J records
                    k_records=k_records,                            # K records
                    comment_records=comment_records,                # L records
                    )


class LowLevelReader:
    """
    A low level reader for the IGC flight log file format.

    see http://carrier.csi.cam.ac.uk/forsterlewis/soaring/igc_file_format/igc_format_2008.html
    """

    def __init__(self, file_obj):
        self.file_obj = file_obj
        self.line_number = 0

    def __iter__(self):
        return self.next()

    def next(self):
        for line in self.file_obj:
            self.line_number += 1

            record_type = line[0]

            try:
                result = self.parse_line(
                    # skip empty lines
                    record_type, line) if line.strip() else None
                if result:
                    yield (record_type, result, None)
            except Exception as e:
                e.line_number = self.line_number
                yield (record_type, None, e)

    def parse_line(self, record_type, line):
        decoder = self.get_decoder_method(record_type)
        return decoder(line)

    def get_decoder_method(self, record_type):
        decoder = getattr(self, 'decode_%s_record' % record_type)
        if not decoder:
            raise ValueError('Unknown record type')

        return decoder

    @staticmethod
    def decode_A_record(line):
        id_addition = None if len(line) == 7 else line[7:].strip()
        return {
            'manufacturer': line[1:4],
            'id': line[4:7],
            'id_addition': id_addition
        }

    @staticmethod
    def decode_B_record(line):
        return {
            'time': LowLevelReader.decode_time(line[1:7]),
            'lat': LowLevelReader.decode_latitude(line[7:15]),
            'lon': LowLevelReader.decode_longitude(line[15:24]),
            'validity': line[24],
            'pressure_alt': int(line[25:30]),
            'gps_alt': int(line[30:35]),
            'start_index_extensions': 35,
            'extensions_string': line[35::].strip()
        }

    @staticmethod
    def process_B_record(decoded_b_record, fix_record_extensions):

        i = decoded_b_record['start_index_extensions']
        ext = decoded_b_record['extensions_string']

        b_record = decoded_b_record
        del b_record['start_index_extensions']
        del b_record['extensions_string']

        for extension in fix_record_extensions:
            start_byte, end_byte = extension['bytes']
            start_byte = start_byte - i - 1
            end_byte = end_byte - i - 1

            try:
                b_record.update(
                    {extension['extension_type']: int(
                        ext[start_byte:end_byte + 1])}
                )
            except ValueError:  # Some lines can be malformatted with unexpected string values. Skip these
                continue

        return b_record

    @staticmethod
    def decode_C_record(line):

        task_info = line[8].isdigit()

        if task_info:
            return {
                'subtype': 'task_info',
                'declaration_date': LowLevelReader.decode_date(line[1:7]),
                'declaration_time': LowLevelReader.decode_time(line[7:13]),
                'flight_date': LowLevelReader.decode_date(line[13:19]),
                'number': line[19:23],
                'num_turnpoints': int(line[23:25]),
                'description': line[25::].strip()
            }
        else:
            return {
                'subtype': 'waypoint_info',
                'latitude': LowLevelReader.decode_latitude(line[1:9]),
                'longitude': LowLevelReader.decode_longitude(line[9:18]),
                'description': line[18::].strip()
            }

    @staticmethod
    def decode_D_record(line):

        qualifier = line[1]
        if qualifier == '1':
            qualifier = 'GPS'
        elif qualifier == '2':
            qualifier = 'DGPS'
        else:
            raise ValueError('This qualifier is not possible')

        return {
            'qualifier': qualifier,
            'station_id': line[2:6]
        }

    @staticmethod
    def decode_E_record(line):
        return {
            'time': LowLevelReader.decode_time(line[1:7]),
            'tlc': line[7:10],
            'extension_string': line[10::].strip()

        }

    @staticmethod
    def decode_F_record(line):

        time_str = line[1:7]
        time = LowLevelReader.decode_time(time_str)

        # each satellite ID should have two digits
        if (len(line.strip()) - 7) % 2 != 0:
            raise ValueError('F record formatting is incorrect')

        satellites = []
        no_satellites = int((len(line.strip()) - 7) / 2)

        starting_byte = 7
        for satellite_index in range(no_satellites):
            satellites.append(line[starting_byte:starting_byte + 2])
            starting_byte += 2

        return {
            'time': time,
            'satellites': satellites
        }

    @staticmethod
    def decode_G_record(line):
        return line.strip()[1::]

    @staticmethod
    def decode_H_record(line):

        source = line[1]

        # three letter code
        tlc = line[2:5]

        colon = line.find(":", 5)
        if colon >= 0:
            # This is the long format
            long_name = line[5:colon].strip()
            if long_name == "":
                long_name = None
            line_value = line[colon + 1:].strip()
        else:
            long_name = None
            line_value = line[5:].strip()

        if tlc == 'DTE':
            value = LowLevelReader.decode_H_utc_date(line_value)
        elif tlc == 'FXA':
            value = LowLevelReader.decode_H_fix_accuracy(line_value)
        elif tlc == 'PLT':
            value = LowLevelReader.decode_H_pilot(line_value)
        elif tlc == 'CM2':
            value = LowLevelReader.decode_H_copilot(line_value)
        elif tlc == 'GTY':
            value = LowLevelReader.decode_H_glider_model(line_value)
        elif tlc == 'GID':
            value = LowLevelReader.decode_H_glider_registration(line_value)
        elif tlc == 'DTM':
            value = LowLevelReader.decode_H_gps_datum(line_value)
        elif tlc == 'RFW':
            value = LowLevelReader.decode_H_firmware_revision(line_value)
        elif tlc == 'RHW':
            value = LowLevelReader.decode_H_hardware_revision(line_value)
        elif tlc == 'FTY':
            value = LowLevelReader.decode_H_manufacturer_model(line_value)
        elif tlc == 'GPS':
            value = LowLevelReader.decode_H_gps_receiver(line_value)
        elif tlc == 'PRS':
            value = LowLevelReader.decode_H_pressure_sensor(line_value)
        elif tlc == 'CID':
            value = LowLevelReader.decode_H_competition_id(line_value)
        elif tlc == 'CCL':
            value = LowLevelReader.decode_H_competition_class(line_value)
        elif tlc == 'TZN':
            value = LowLevelReader.decode_H_time_zone_offset(line_value)
        elif tlc == 'MOP':
            value = LowLevelReader.decode_H_mop_sensor(line_value)
        elif tlc == 'SIT':
            value = LowLevelReader.decode_H_site(line_value)
        elif tlc == 'TZO':
            value = LowLevelReader.decode_H_time_zone_offset(line_value)
        elif tlc == 'UNT':
            value = LowLevelReader.decode_H_units_of_measure(line_value)
        elif tlc == 'FRS':
            value = LowLevelReader.decode_H_security(line_value)
        elif tlc == 'ALG':
            value = LowLevelReader.decode_H_gnss_alt(line_value)
        elif tlc == 'ALP':
            value = LowLevelReader.decode_H_pressure_alt(line_value)
        else:
            raise ValueError('Invalid h-record "%s"' % tlc)

        value.update({'source': source})

        return value

    @staticmethod
    def decode_H_utc_date(value):
        date_str = value[:6]
        return {'utc_date': LowLevelReader.decode_date(date_str)}

    @staticmethod
    def decode_H_fix_accuracy(value):
        fix_accuracy = value
        return {'fix_accuracy': None} if fix_accuracy == '' else {'fix_accuracy': int(fix_accuracy)}

    @staticmethod
    def decode_H_pilot(value):
        pilot = value
        return {'pilot': None} if pilot == '' else {'pilot': pilot}

    @staticmethod
    def decode_H_copilot(value):
        second_pilot = value
        return {'copilot': None} if second_pilot == '' else {'copilot': second_pilot}

    @staticmethod
    def decode_H_glider_model(value):
        glider_model = value
        return {'glider_model': None} if glider_model == '' else {'glider_model': glider_model}

    @staticmethod
    def decode_H_glider_registration(value):
        glider_registration = value
        if glider_registration == '':
            return {'glider_registration': None}
        else:
            return {'glider_registration': glider_registration}

    @staticmethod
    def decode_H_gps_datum(value):
        gps_datum = value
        return {'gps_datum': None} if gps_datum == '' else {'gps_datum': gps_datum}

    @staticmethod
    def decode_H_firmware_revision(value):
        firmware_revision = value
        return {'firmware_revision': None} if firmware_revision == '' else {'firmware_revision': firmware_revision}

    @staticmethod
    def decode_H_security(security):
        return {'security': None} if security == '' else {'security': security}

    @staticmethod
    def decode_H_hardware_revision(value):
        hardware_revision = value
        return {'hardware_revision': None} if hardware_revision == '' else {'hardware_revision': hardware_revision}

    @staticmethod
    def decode_H_manufacturer_model(value):
        manufacturer = None
        model = None
        manufacturer_model = value.split(',')
        if manufacturer_model[0] != '':
            manufacturer = manufacturer_model[0].strip()
        if len(manufacturer_model) == 2 and manufacturer_model[1].lstrip() != '':
            model = manufacturer_model[1].strip()
        return {'logger_manufacturer': manufacturer,
                'logger_model': model}

    @staticmethod
    def decode_H_gps_receiver(value):
        gps_sensor = value.split(',')
        manufacturer = None
        model = None
        channels = None
        max_alt = None
        for detail_index, detail in enumerate(reversed(gps_sensor)):
            if len(gps_sensor) == 1 or (len(gps_sensor) == 2 and gps_sensor[1].strip() == ''):
                manufacturer = detail.strip()
            elif len(gps_sensor) == 3:
                if detail_index == 0:
                    max_alt = detail.strip()
                elif detail_index == 1:
                    channels = detail.strip()
                else:  # detail_index == 2
                    manufacturer = detail.strip()
            elif len(gps_sensor) == 4:
                if detail_index == 0:
                    max_alt = detail.strip()
                elif detail_index == 1:
                    channels = detail.strip()
                elif detail_index == 2:
                    model = detail.strip()
                else:  # detail_index == 3
                    manufacturer = detail.strip()
            else:
                raise NotImplementedError

        # stripping of ch from '12ch'
        if channels is not None:
            # Special case for SkyBean SkyDrop/Strato vario wrongly
            # specifying channels as "cm"
            if manufacturer == 'Quectel' and model == 'L80' and channels == '22cm':
                channels = 22
            elif manufacturer == 'u-blox' and model == 'NEO-M8Q' and channels == '22cm':
                channels = 72
            else:
                if channels.endswith('ch') or channels.endswith('Ch') or channels.endswith('CH'):
                    channels = int(channels[:-2])
                else:
                    channels = int(channels)

        # stripping of max from 'max10000m'
        if max_alt is not None and max_alt.startswith('max'):
            max_alt = max_alt[3::]

        # separate unit from value
        if max_alt is not None and max_alt.endswith('m'):
            max_alt_value = int(max_alt[:-1])
            max_alt_unit = 'm'
        elif max_alt is not None and max_alt.endswith('ft'):
            max_alt_value = int(max_alt[:-2])
            max_alt_unit = 'ft'
        elif max_alt is not None:
            max_alt_value = int(max_alt)
            max_alt_unit = 'm'
        else:
            max_alt_value = None
            max_alt_unit = None

        return {
            'gps_manufacturer': manufacturer,
            'gps_model': model,
            'gps_channels': channels,
            'gps_max_alt': {
                'value': max_alt_value,
                'unit': max_alt_unit
            }
        }

    @staticmethod
    def decode_H_pressure_sensor(value):

        manufacturer = None
        model = None
        max_alt = None

        # some IGC files use colon, others don't
        pressure_sensor = value.split(',')

        if len(pressure_sensor) == 1:
            manufacturer = pressure_sensor[0].strip(
            ) if pressure_sensor[0] != '' else None
        elif len(pressure_sensor) == 2:
            manufacturer_model = pressure_sensor[0].strip().split(
                ' ') if pressure_sensor[0] != '' else None

            if len(manufacturer_model) == 2:
                manufacturer = manufacturer_model[0]
                model = manufacturer_model[1]
            else:
                manufacturer = manufacturer_model[0]

            max_alt = pressure_sensor[1].strip(
            ) if pressure_sensor[1] != '' else None
        elif len(pressure_sensor) == 3:
            manufacturer = pressure_sensor[0].strip(
            ) if pressure_sensor[0] != '' else None
            model = pressure_sensor[1].strip(
            ) if pressure_sensor[1] != '' else None
            max_alt = pressure_sensor[2].strip(
            ) if pressure_sensor[2] != '' else None

        # stripping of max from 'max10000m'
        if max_alt is not None and max_alt.startswith('max'):
            max_alt = max_alt[3::]

        # separate unit from value
        if max_alt is not None and max_alt.endswith('m'):
            max_alt_value = int(max_alt[:-1])
            max_alt_unit = 'm'
        elif max_alt is not None and max_alt.endswith('ft'):
            max_alt_value = int(max_alt[:-2])
            max_alt_unit = 'ft'
        elif max_alt is not None:
            max_alt_value = int(max_alt)
            max_alt_unit = 'm'
        else:
            max_alt_value = None
            max_alt_unit = None

        return {
            'pressure_sensor_manufacturer': manufacturer,
            'pressure_sensor_model': model,
            'pressure_sensor_max_alt': {
                'value': max_alt_value,
                'unit': max_alt_unit
            }
        }

    @staticmethod
    def decode_H_competition_id(value):
        competition_id = value
        return {'competition_id': None} if competition_id == '' else {'competition_id': competition_id}

    @staticmethod
    def decode_H_competition_class(value):
        competition_class = value
        return {'competition_class': None} if competition_class == '' else {'competition_class': competition_class}

    @staticmethod
    def decode_H_time_zone_offset(value):
        return {'time_zone_offset': float(value)}

    @staticmethod
    def decode_H_mop_sensor(value):
        return {'mop_sensor': value}

    @staticmethod
    def decode_H_site(value):
        return {'site': value}

    @staticmethod
    def decode_H_units_of_measure(value):
        return {'units_of_measure': value.split(',')}

    @staticmethod
    def decode_H_gnss_alt(value):
        if value == "WGS84 ELLIPSOID":
            value = "ELL"          # Fix for LXNAV recorders
        if value not in ["ELL", "GEO", "NKM", "NIL"]:
            raise ValueError('Invalid HFALG value "%s"' % value)
        return {'gnss_altitude': value}

    @staticmethod
    def decode_H_pressure_alt(value):
        if value not in ["ISA", "MSL", "NKM", "NIL"]:
            raise ValueError('Invalid HFALP value "%s"' % value)
        return {'pressure_altitude': value}

    @staticmethod
    def decode_I_record(line):
        return LowLevelReader.decode_extension_record(line)

    @staticmethod
    def decode_J_record(line):
        return LowLevelReader.decode_extension_record(line)

    @staticmethod
    def decode_K_record(line):
        return {
            'time': LowLevelReader.decode_time(line[1:7]),
            'value_string': line.strip()[7::],
            'start_index': 7
        }

    @staticmethod
    def process_K_record(decoded_k_record, k_record_extensions):

        i = decoded_k_record['start_index']
        t = decoded_k_record['time']
        val = decoded_k_record['value_string']

        k_record = {'time': t}
        for extension in k_record_extensions:

            start_byte, end_byte = extension['bytes']
            start_byte -= i
            end_byte -= i

            k_record[extension['extension_type']] = val[start_byte:end_byte]

        return k_record

    @staticmethod
    def decode_L_record(line):
        return {
            'source': line[1:4],
            'comment': line[4::].strip()
        }

    @staticmethod
    def decode_date(date_str):

        if len(date_str) != 6:
            raise ValueError('Date string does not have correct length')
        elif date_str == '000000':
            return None

        return datetime.datetime.strptime(date_str, "%d%m%y").date()

    @staticmethod
    def decode_time(time_str):

        if len(time_str) != 6:
            raise ValueError('Time string does not have correct size')

        return datetime.datetime.strptime(time_str, "%H%M%S").time()

    @staticmethod
    def decode_extension_record(line):
        """
        Decode an IGC file extension record (I-record).

        Args:
            line: The I-record line from an IGC file

        Returns:
            List of extension definitions with 'bytes' and 'extension_type' keys

        Raises:
            ValueError: If the record format is invalid
        """
        line = line.strip()
        extension_count = int(line[1:3])
        extensions = []
        position = 3

        for _ in range(extension_count):
            # Extract numeric characters for byte positions
            numeric_start = position
            while position < len(line) and line[position].isdigit():
                position += 1

            numeric_section = line[numeric_start:position]
            if not numeric_section:
                raise ValueError("Missing byte positions in extension record")

            # Split numeric section in half for start/end bytes
            midpoint = len(numeric_section) // 2
            start_byte = int(numeric_section[:midpoint])
            end_byte = int(numeric_section[midpoint:])

            # Extract three-letter code
            if position + 3 > len(line):
                raise ValueError("Incomplete extension record: missing TLC")

            tlc = line[position:position + 3]
            position += 3

            extensions.append({
                'bytes': (start_byte, end_byte),
                'extension_type': tlc
            })

        if position != len(line):
            raise ValueError('I record contains incorrect number of digits')

        return extensions

    @staticmethod
    def decode_latitude(lat_string):

        d = int(lat_string[0:2])
        m = float(lat_string[2:7]) / 1000
        ordinal = lat_string[7]

        latitude = d + m / 60.

        if not (0. <= latitude <= 90):
            raise ValueError('Latitude format is invalid')

        if ordinal == 'S':
            latitude = -latitude

        return latitude

    @staticmethod
    def decode_longitude(lon_string):

        d = float(lon_string[0:3])
        m = float(lon_string[3:8]) / 1000
        ordinal = lon_string[8]

        longitude = d + m / 60.

        if not (0. <= longitude <= 180):
            raise ValueError('Longitude format is invalid')

        if ordinal == 'W':
            longitude = -longitude

        return longitude


class MissingRecordsError(Exception):
    pass


class MissingExtensionsError(Exception):
    pass
