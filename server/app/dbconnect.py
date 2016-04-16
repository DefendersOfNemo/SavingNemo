"""
    dbconnect.py
    ~~~~~~~~~~~~~~

    This file contains all the necessary database related methods for query and uploads.

    :copyright: (c) 2016 by Abhijeet Sharma, Jiayi Wu.
    :license: The MIT License (MIT), see LICENSE for more details.
"""

from datetime import datetime
import MySQLdb


class DbConnect(object):
    """Class which includes database connection, insertion and updation methods"""
    def __init__(self, config):
        self.connection = MySQLdb.connect(
            host=config['MYSQL_HOST'], \
            port=config['MYSQL_PORT'], \
            user=config['MYSQL_USER'], \
            passwd=config['MYSQL_PASSWORD'], \
            db=config['MYSQL_DB'])    
    def fetch_biomimic_types(self):
        """Fetches all Logger Biomimic Types"""
        cursor = self.connection.cursor()
        query = ("SELECT biomimic_type FROM `cnx_logger_biomimic_type`")
        cursor.execute(query)
        result = cursor.fetchall()
        result = list(result)
        final_result = [[row[0], row[0]] for row in result]
        cursor.close()
        return final_result

    def fetch_distinct_countries_and_zones(self, query_dict):
        """Fetches all countries for selected biomimic type"""
        cursor = self.connection.cursor()
        query = """SELECT DISTINCT geo.country
                   FROM `cnx_logger` log
                   INNER JOIN `cnx_logger_biomimic_type` biotype
                   ON biotype.`biomimic_id`=log.`biomimic_id`
                   INNER JOIN `cnx_logger_geographics` geo
                   ON geo.`geo_id`=log.`geo_id`
                   WHERE biotype.`biomimic_type`=\'%s\'""" % query_dict['biomimic_type']
        cursor.execute(query + " ORDER BY 1 ASC")
        result = cursor.fetchall()
        country_list = [row[0] for row in result]
        query = """SELECT DISTINCT prop.zone FROM `cnx_logger` log
                   INNER JOIN `cnx_logger_biomimic_type` biotype
                   ON biotype.`biomimic_id`=log.`biomimic_id`
                   INNER JOIN `cnx_logger_properties` prop
                   ON prop.`prop_id`=log.`prop_id`
                   WHERE biotype.biomimic_type=\'%s\'""" % query_dict['biomimic_type']
        cursor.execute(query + " ORDER BY 1 ASC")
        result = cursor.fetchall()
        zone_list = [row[0] for row in result]
        cursor.close()
        final_result = {"country": country_list, "zone": zone_list}
        count_records, min_date, max_date = self.fetch_metadata(query_dict)
        return final_result, count_records, min_date, max_date

    def fetch_distinct_states(self, query_dict):
        """Fetches Distinct states for selected biomimic type and country"""
        cursor = self.connection.cursor()
        query = """SELECT DISTINCT geo.state_province
                   FROM `cnx_logger` log
                   INNER JOIN `cnx_logger_biomimic_type` biotype
                   ON biotype.`biomimic_id`=log.`biomimic_id`
                   INNER JOIN `cnx_logger_geographics` geo
                   ON geo.`geo_id`=log.`geo_id` """
        where_condition = self.build_where_condition(query_dict)
        cursor.execute(query + where_condition + " ORDER BY 1 ASC")
        result = cursor.fetchall()
        final_result = [row[0] for row in result]
        cursor.close()
        count_records, min_date, max_date = self.fetch_metadata(query_dict)
        return final_result, count_records, min_date, max_date

    def fetch_distinct_locations(self, query_dict):
        """ Fetches Distinct locations for selected biomimic type, country
            and state_province"""
        cursor = self.connection.cursor()
        query = """SELECT DISTINCT geo.location
                   FROM `cnx_logger` log
                   INNER JOIN `cnx_logger_biomimic_type` biotype
                   ON  biotype.`biomimic_id`=log.`biomimic_id`
                   INNER JOIN `cnx_logger_geographics` geo
                   ON geo.`geo_id`=log.`geo_id` """
        where_condition = self.build_where_condition(query_dict)
        cursor.execute(query + where_condition + " ORDER BY 1 ASC")
        result = cursor.fetchall()
        final_result = [row[0] for row in result]
        cursor.close()
        count_records, min_date, max_date = self.fetch_metadata(query_dict)
        return final_result, count_records, min_date, max_date

    def fetch_distinct_sub_zones(self, query_dict):
        """ Fetches Distinct Subzones for selected biomimic type, country,
            state_province, location and zones"""
        cursor = self.connection.cursor()
        query = """SELECT DISTINCT prop.sub_zone
                   FROM `cnx_logger` log
                   INNER JOIN `cnx_logger_biomimic_type` biotype
                   ON biotype.`biomimic_id`=log.`biomimic_id`
                   INNER JOIN `cnx_logger_geographics` geo
                   ON geo.`geo_id`=log.`geo_id`
                   INNER JOIN `cnx_logger_properties` prop
                   ON prop.`prop_id`=log.`prop_id` """
        where_condition = self.build_where_condition(query_dict)
        cursor.execute(query + where_condition + " ORDER BY 1 ASC")
        result = cursor.fetchall()
        final_result = ['N/A' if row[0] is None else row[0] for row in result]
        cursor.close()
        count_records, min_date, max_date = self.fetch_metadata(query_dict)
        return final_result, count_records, min_date, max_date

    def fetch_distinct_wave_exposures(self, query_dict):
        """Fetches Distinct Wave Exp for selected biomimic type, country,
            state_province, location, zones and sub_zones"""
        cursor = self.connection.cursor()
        query = """SELECT DISTINCT prop.wave_exp FROM `cnx_logger` log
                   INNER JOIN `cnx_logger_biomimic_type` biotype
                   ON biotype.`biomimic_id`=log.`biomimic_id`
                   INNER JOIN `cnx_logger_geographics` geo
                   ON geo.`geo_id`=log.`geo_id`
                   INNER JOIN `cnx_logger_properties` prop
                   ON prop.`prop_id`=log.`prop_id`"""
        where_condition = self.build_where_condition(query_dict)
        cursor.execute(query + where_condition + " ORDER BY 1 ASC")
        result = cursor.fetchall()
        final_result = ['N/A' if row[0] is None else row[0] for row in result]
        cursor.close()
        count_records, min_date, max_date = self.fetch_metadata(query_dict)
        return final_result, count_records, min_date, max_date

    def fetch_metadata(self, query_dict):
        """Fetches metadata from tables based on user query"""
        cursor = self.connection.cursor()
        query = """ SELECT SUM(meta.logger_count),
                          MIN(meta.logger_min_date),
                          MAX(meta.logger_max_date)
                    FROM `cnx_logger_metadata` meta
                    WHERE meta.`logger_id` IN (
                        SELECT log.`logger_id`
                        FROM `cnx_logger` log
                        INNER JOIN `cnx_logger_biomimic_type` biotype
                        ON biotype.`biomimic_id` = log.`biomimic_id`
                        INNER JOIN `cnx_logger_geographics` geo
                        ON geo.`geo_id` = log.`geo_id`
                        INNER JOIN `cnx_logger_properties` prop
                        ON prop.`prop_id` = log.`prop_id` """
        where_condition = self.build_where_condition(query_dict)
        cursor.execute(query + where_condition + ")")
        results = cursor.fetchone()
        cursor.close()
        results = list(results)
        if results[0] is not None:
            results[0] = "{:,}".format(results[0])
        return results


    def get_query_results_preview(self, query_dict):
        """Fetches records from tables based on user query"""
        cursor = self.connection.cursor()
        output_type = query_dict.get("output_type")
        analysis_type = query_dict.get("analysis_type")
        temp_field = ""

        if output_type == "Min":                            # Min
            temp_field = "MIN(temp.Temp_C)"
        elif output_type == "Max":                          # Max
            temp_field = "MAX(temp.Temp_C)"
        elif output_type == "Average":                      # Average
            temp_field = "AVG(temp.Temp_C)"
        else:                                               # Raw
            temp_field = "temp.Temp_C"

        if analysis_type == "Daily":                        # Daily
            date_field = "DATE_FORMAT(temp.Time_GMT, '%m/%d/%Y')"
        elif analysis_type == "Monthly":                    # Monthly
            date_field = "CONCAT_WS(', ', MONTHNAME(temp.Time_GMT), YEAR(temp.Time_GMT))"
        elif analysis_type == "Yearly":                     # Yearly
            date_field = "YEAR(temp.Time_GMT)"
        else:                                               # Raw, no change
            date_field = "temp.Time_GMT"
        query = """SELECT %s, %s
                   FROM `cnx_logger` log
                   INNER JOIN `cnx_logger_biomimic_type` biotype
                   ON biotype.`biomimic_id` = log.`biomimic_id`
                   INNER JOIN `cnx_logger_geographics` geo
                   ON geo.`geo_id` = log.`geo_id`
                   INNER JOIN `cnx_logger_properties` prop
                   ON prop.`prop_id` = log.`prop_id`
                   INNER JOIN `cnx_logger_temperature` temp
                   ON temp.`logger_id` = log.`logger_id` """ % (date_field, temp_field)
        where_condition = self.build_where_condition(query_dict)
        cursor.execute(query + where_condition + " LIMIT 10 ")
        results = cursor.fetchall()
        results = list(results)
        final_result = [[result[0], round(result[1], 4)] for result in results]
        cursor.close()
        return final_result, query + where_condition

    def get_query_raw_results(self, db_query):
        """Fetches records form tables based on user query"""
        cursor = self.connection.cursor()
        cursor.execute(db_query)
        results = cursor.fetchall()
        results = list(results)
        final_result = [[result[0], round(result[1], 4)] for result in results]
        cursor.close()
        return final_result

    def build_where_condition(self, query_dict):
        """Builds the where_condition for the Select Query"""
        analysis_type = query_dict.get("analysis_type")
        where = (" WHERE biotype.`biomimic_type`=\'%s\'") % query_dict['biomimic_type']
        if query_dict.get('country') is not None:
            where += " AND geo.`country`=\'%s\'" % (query_dict['country'])
        if query_dict.get('state_province') is not None:
            where += " AND geo.`state_province`=\'%s\'" % (query_dict['state_province'])
        if query_dict.get('location') is not None:
            where += " AND geo.`location`=\'%s\'" % (query_dict['location'])
        if (query_dict.get('zone') is not None) and (query_dict.get('zone') != 'All'):
            where += " AND prop.`zone`=\'%s\'" % (query_dict.get('zone'))
        if (query_dict.get('sub_zone') is not None) and (query_dict.get('sub_zone') != 'All'):
            if query_dict.get('sub_zone') == 'N/A':
                where += " AND prop.sub_zone is Null"
            else:
                where += " AND prop.`sub_zone`=\'%s\'" % (query_dict.get('sub_zone'))
        if (query_dict.get('wave_exp') is not None) and (query_dict.get('wave_exp') != 'All'):
            if query_dict.get('wave_exp') == 'N/A':
                where += " AND prop.wave_exp is Null"
            else:
                where += " AND prop.`wave_exp`=\'%s\' " % (query_dict.get('wave_exp'))
        if (query_dict.get('start_date') is not None) and (query_dict.get('end_date') is not None):
            where += """ AND cast(temp.Time_GMT as date) >= \'%s\'
                         AND cast(temp.Time_GMT as date) <= \'%s\'""" % \
                         (query_dict.get('start_date'), query_dict.get('end_date'))
        if analysis_type == "Daily":
            where += " GROUP BY cast(temp.Time_GMT as date)"
        elif analysis_type == "Monthly":
            where += """ GROUP BY YEAR(temp.Time_GMT), MONTHNAME(temp.Time_GMT)
                         ORDER BY YEAR(temp.Time_GMT), MONTH(temp.Time_GMT) ASC"""
        elif analysis_type == "Yearly":
            where += " GROUP BY YEAR(temp.Time_GMT)"
        else:
            pass
        return where

    def parse_logger_type(self, data_list):
        """Parse new Logger Type"""
        parsed_record = dict()
        error = False
        if (len(data_list) != 11) or (self.is_not_float(data_list[2])) or \
           (self.is_not_float(data_list[3])) or (data_list[0] == "None") or \
           (data_list[0] == ""):
            error = True
        else:
            parsed_record['microsite_id'] = str(data_list[0]).upper()
            parsed_record['site'] = (data_list[1]).upper()
            parsed_record['field_lat'] = data_list[2]
            parsed_record['field_lon'] = data_list[3]
            parsed_record['location'] = data_list[4]
            parsed_record['state_province'] = data_list[5]
            parsed_record['country'] = data_list[6]
            parsed_record['biomimic_type'] = data_list[7].capitalize()
            parsed_record['zone'] = data_list[8].capitalize()
            parsed_record['sub_zone'] = None if (data_list[9] == "N/A") \
                                            else data_list[9].capitalize()
            parsed_record['wave_exp'] = None if (data_list[10] == "N/A") \
                                            else data_list[10].capitalize()
        return parsed_record, error

    def is_not_float(self, value):
        '''check whether value is float'''
        try:
            float(value)
            return False
        except ValueError:
            return True

    def insert_logger_type(self, records):
        """Inserts new Logger Type in DB"""
        cursor = self.connection.cursor()
        proper_counter = 0
        corrupt_indicator = False
        for record in records:
            duplicate_microsite_id = self.check_for_duplicate(cursor, record.get("microsite_id"))
            if not duplicate_microsite_id:
                geo_id = self.fetch_existing_geo_id(cursor, record)
                if geo_id is None:
                    geo_id, corrupt_indicator = self.insert_geo_data(cursor, record)
                else:
                    geo_id = geo_id[0]
                if corrupt_indicator:
                    self.connection.rollback()
                    continue
                prop_id = self.fetch_existing_prop_id(cursor, record)
                if prop_id is None:
                    prop_id, corrupt_indicator = self.insert_properties_data(cursor, record)
                else:
                    prop_id = prop_id[0]
                if corrupt_indicator:
                    self.connection.rollback()
                    continue
                biomimic_id = self.fetch_existing_bio_id(cursor, record.get('biomimic_type'))
                if biomimic_id is None:
                    biomimic_id, corrupt_indicator = \
                        self.insert_biomimic_type_data(cursor, record.get('biomimic_type'))
                else:
                    biomimic_id = biomimic_id[0]
                if corrupt_indicator:
                    self.connection.rollback()
                    continue
                corrupt_indicator = \
                    self.insert_microsite_data(cursor, record.get('microsite_id'), \
                                             biomimic_id, geo_id, prop_id)
                if corrupt_indicator:
                    self.connection.rollback()
                    continue
                else:
                    self.connection.commit()
                    proper_counter += 1
        cursor.close()
        return proper_counter

    def fetch_existing_bio_id(self, cursor, biomimic_type):
        """Check for Existing Biomimic Type Data"""
        query = """SELECT `biomimic_id`
                   FROM `cnx_logger_biomimic_type`
                   WHERE `biomimic_type`=%s"""
        cursor.execute(query, (biomimic_type,))
        result = cursor.fetchone()
        return result

    def insert_biomimic_type_data(self, cursor, biomimic_type):
        """Insert new Biomimic Type Data in DB"""
        corrupt = False
        query = """ INSERT INTO `cnx_logger_biomimic_type` (`biomimic_type`)
                    VALUES (%s)"""
        try:
            res = cursor.execute(query, (biomimic_type,))
        except MySQLdb.Error:
            res = 0
        if res == 1:
            pass
        else:
            corrupt = True
        return cursor.lastrowid, corrupt

    def fetch_existing_geo_id(self, cursor, record):
        """Check for Existing GeoLocation Data"""
        query = """SELECT `geo_id`
                   FROM `cnx_logger_geographics`
                   WHERE `site`=%s AND `field_lat`=%s AND `field_long`=%s
                   AND `location`=%s AND `state_province`=%s AND `country`=%s"""
        cursor.execute(query, (record.get("site"), record.get("field_lat"), \
                               record.get("field_lon"), record.get("location"), \
                               record.get("state_province"), record.get("country")))
        result = cursor.fetchone()
        return result

    def insert_geo_data(self, cursor, record):
        """Insert new Geolocation Data in DB"""
        corrupt = False
        query = """INSERT INTO `cnx_logger_geographics`
                   (`site`, `field_lat`, `field_long`, `location`, `state_province`, `country`)
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        try:
            res = cursor.execute(query, (record.get("site"), \
                                         record.get("field_lat"), \
                                         record.get("field_lon"), \
                                         record.get("location"), \
                                         record.get("state_province"), \
                                         record.get("country")))
        except MySQLdb.Error:
            res = 0
        if res == 1:
            pass
        else:
            corrupt = True
        return cursor.lastrowid, corrupt

    def fetch_existing_prop_id(self, cursor, record):
        """Check for Existing Properties Data"""
        query = "SELECT `prop_id` from `cnx_logger_properties`"
        where = " WHERE `zone`=\'%s\'" % (record.get("zone"))
        if record.get('sub_zone') is not None:
            where += " AND `sub_zone`=\'%s\'" % (record.get('sub_zone'))
        if record.get('wave_exp') is not None:
            where += " AND `wave_exp`=\'%s\'" % (record.get('wave_exp'))
        cursor.execute(query + where)
        result = cursor.fetchone()
        return result

    def insert_properties_data(self, cursor, record):
        """Insert new Properties Data in DB"""
        corrupt = False
        values = " VALUES (\'%s\'" % record.get("zone")
        if record.get('sub_zone') is None:
            values += ", NULL"
        else:
            values += ", \'%s\'" % record.get("sub_zone")
        if record.get('wave_exp') is None:
            values += ", NULL"
        else:
            values += ", \'%s\'" % record.get("wave_exp")
        values += ")"
        query = """INSERT INTO `cnx_logger_properties`
                   (`zone`, `sub_zone`, `wave_exp`)""" + values
        try:
            res = cursor.execute(query)
        except MySQLdb.Error:
            res = 0
        if res == 1:
            pass
        else:
            corrupt = True
        return cursor.lastrowid, corrupt

    def insert_microsite_data(self, cursor, microsite_id, biomimic_id, geo_id, prop_id):
        """Insert new Microsite Id Data in DB"""
        corrupt = False
        query = """INSERT INTO `cnx_logger` (`microsite_id`, `biomimic_id`, `geo_id`, `prop_id`)
                   VALUES (%s, %s, %s, %s)"""
        try:
            res = cursor.execute(query, (microsite_id, biomimic_id, geo_id, prop_id))
        except MySQLdb.Error:
            res = 0
        if res == 1:
            pass
        else:
            corrupt = True
        return corrupt

    def check_for_duplicate(self, cursor, microsite_id):
        """Check for Duplicate Microsite Id in DB"""
        query = """SELECT `logger_id`
                   FROM `cnx_logger`
                   WHERE `microsite_id`=%s"""
        cursor.execute(query, (microsite_id,))
        results = cursor.fetchall()
        results = list(results)
        return len(results) > 0

    def parse_logger_temp(self, data_list):
        """Parse new Logger Temperature Data"""
        parsed_record = dict()
        error = False
        if (len(data_list) != 2) or \
           (self.is_not_float(data_list[1])) or \
           (data_list[0] == "None") or \
           (data_list[0] == ""):
            error = True
        else:
            # handle datetime error
            try:
                parsed_record['Time_GMT'] = datetime.strptime(data_list[0], '%m/%d/%Y %H:%M')
            except ValueError:
                try:
                    parsed_record['Time_GMT'] = datetime.strptime(data_list[0], '%m/%d/%y %H:%M')
                except ValueError:
                    error = True
        if not error:
            parsed_record['Temp_C'] = data_list[1]
        return parsed_record, error

    def insert_logger_temp(self, records, logger_id):
        """Inserts new Logger Temperature in DB"""
        # records is a list of dict
        cursor = self.connection.cursor()
        proper_counter = 0
        query = """INSERT IGNORE INTO `cnx_logger_temperature` (`logger_id`, `Time_GMT`, `Temp_C`)
                   VALUES (%s, %s, %s)"""
        values = [(logger_id, record.get("Time_GMT"), record.get("Temp_C")) for record in records]
        try:
            # duplicate entries are ignored while inserting data
            cursor.executemany(query, values)
            self.connection.commit()
            proper_counter = cursor.rowcount
        except MySQLdb.DatabaseError:
            self.connection.rollback()
        cursor.close()
        self.update_summary_table(logger_id)
        return proper_counter

    def find_microsite_id(self, microsite_id):
        """Fetch logger_id according to microsite_id"""
        cursor = self.connection.cursor()
        query = """SELECT `logger_id` as 'logger_id' FROM `cnx_logger` WHERE microsite_id=%s"""
        cursor.execute(query, (microsite_id,))
        results = cursor.fetchone()
        cursor.close()
        if results is None:
            return None
        else:
            return results[0]

    def update_summary_table(self, logger_id):
        """This method updates the summary table with count, min and max dates
           of the microsite id of the temperature records inserted"""
        cursor = self.connection.cursor()
        select_query = ("""SELECT COUNT(*), MIN(Time_GMT), MAX(Time_GMT)
                            FROM cnx_logger_temperature WHERE logger_id=%s""")
        cursor.execute(select_query, (logger_id,))
        select_results = cursor.fetchone()
        cursor.close()
        if select_results is not None:
            cursor = self.connection.cursor()
            try:
                update_query = """INSERT INTO `cnx_logger_metadata`
                                  (logger_id, logger_count, logger_min_date, logger_max_date)
                                  VALUES (%s, %s, %s, %s)
                                  ON DUPLICATE KEY UPDATE
                                    logger_count = VALUES(logger_count),
                                    logger_min_date = VALUES(logger_min_date),
                                    logger_max_date = VALUES(logger_max_date)"""
                cursor.execute(update_query, (logger_id, select_results[0], \
                                              select_results[1], select_results[2]))
                self.connection.commit()
                cursor.close()
            except MySQLdb.DatabaseError:
                self.connection.rollback()

    def close(self):
        """closes the Database Connection"""
        self.connection.close()
