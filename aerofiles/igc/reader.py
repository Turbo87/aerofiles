class Reader:
    """
    A reader for the IGC flight log file format.

    see http://carrier.csi.cam.ac.uk/forsterlewis/soaring/igc_file_format/igc_format_2008.html
    """

    def __init__(self):
        pass

    def read(self, fp):
        logger_id, fix_records, task, dgps_records, event_records, satellite_records, security_records, header,\
            fix_record_extensions, k_record_extensions, k_records, comment_records = (None,) * 12

        for line in fp:

            if line.startswith('A'):
                logger_id = self.decode_a_record(line)
            elif line.startswith('B'):
                if fix_records is None:
                    fix_records = []
                fix_records.append(self.decode_b_record(line))
            elif line.startswith('C'):
                if task is None:
                    task = self.decode_c_record(line, first_line=True)
                else:
                    array_key, value = self.decode_c_record(line)
                    task[array_key].append(value)
            elif line.startswith('D'):
                if dgps_records is None:
                    dgps_records = []
                dgps_records.append(self.decode_d_record(line))
            elif line.startswith('E'):
                if event_records is None:
                    event_records = []
                event_records.append(self.decode_e_record(line))
            elif line.startswith('F'):
                if satellite_records is None:
                    satellite_records = []
                satellite_records.append(self.decode_f_record(line))
            elif line.startswith('G'):
                if security_records is None:
                    security_records = []
                security_records.append(self.decode_g_record(line))
            elif line.startswith('H'):
                if header is None:
                    header = self.decode_h_record(line, first_line=True)
                else:
                    key, value = self.decode_h_record(line)
                    header[key] = value
            elif line.startswith('I'):
                fix_record_extensions = self.decode_i_record(line)
            elif line.startswith('J'):
                k_record_extensions = self.decode_j_record(line)
            elif line.startswith('K'):
                if k_records is None:
                    k_records = []
                k_records.append(self.decode_k_record(line))
            elif line.startswith('L'):
                if comment_records is None:
                    comment_records = []
                comment_records.append(self.decode_k_record(line))

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

    def decode_a_record(self, line):
        pass

    def decode_b_record(self, line):
        pass

    def decode_c_record(self, line, first_line=False):
        if first_line:
            task = {
                'id': None,
                'description': None,
                'utc_date_declaration': None,
                'utc_time_declaration': None,
                'local_date_intended_flight': None,
                'no_turnpoints': None,
                'content': []
            }

            # todo: implement extraction of task information from first line

            return task
        else:
            pass

    def decode_d_record(self, line):
        pass

    def decode_e_record(self, line):
        pass

    def decode_f_record(self, line):
        pass

    def decode_g_record(self, line):
        pass

    def decode_h_record(self, line, first_line=False):
        if first_line:
            header = {
                'utc_date': None,
                'fix_accuracy': None,
                'pilot': None,
                'second_pilot': None,
                'glider_model': None,
                'glider_registration': None,
                'gps_datum': None,
                'firmware_revision': None,
                'hardware_revision': None,
                'manufacturer_model': None,
                'pressure_sensor': None,
                'competition_id': None,
                'competition_class': None,
            }

            # todo: implement extraction of header information from first line

            return header
        else:
            pass

    def decode_i_record(self, line):
        pass

    def decode_j_record(self, line):
        pass

    def decode_k_record(self, line):
        pass

    def decode_l_record(self, line):
        pass
