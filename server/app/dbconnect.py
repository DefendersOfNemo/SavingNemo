import MySQLdb
import datetime

class DbConnect(object):
    """ Db Class"""
    
    def __init__(self, config):
        self.connection = MySQLdb.connect(
                            host=config['MYSQL_HOST'], \
                            port=config['MYSQL_PORT'], \
                            user=config['MYSQL_USER'], \
                            passwd=config['MYSQL_PASSWORD'], \
                            db=config['MYSQL_DB'])
        
    def getBiomimicTypes(self):
        """Fetches all Logger Biomimic Types"""
        cursor = self.connection.cursor()
        query = ("SELECT biomimic_type FROM `cnx_logger_biomimic_type`")
        cursor.execute(query)
        result = cursor.fetchall()
        result = list(result)
        final_result = [[row[0], row[0]] for row in result]
        cursor.close()
        return final_result

    def getCountry(self, biomimic_type):
        """Fetches all countries for given Logger Biomimic"""
        cursor = self.connection.cursor()
        query = ("SELECT DISTINCT geo.country FROM `cnx_logger` logger "
                 "INNER JOIN `cnx_logger_biomimic_type` bio ON bio.`biomimic_id`=logger.`biomimic_id` "
                 "INNER JOIN `cnx_logger_geographics` geo ON geo.`geo_id`=logger.`geo_id` "
                 "WHERE bio.`biomimic_type`=\'%s\'") % biomimic_type
        cursor.execute(query)
        result = cursor.fetchall()
        result = set(result)
        final_result = [[row[0], row[0]] for row in result]
        cursor.close()
        return final_result

    def getState(self, country):
        """Fetches Distinct states given logger country""" 
        # TODO: """Fetches Distinct states given logger type and logger country""" 
        cursor = self.connection.cursor()
        query = ("SELECT DISTINCT geo.state_province FROM `cnx_logger` logger "
                 "INNER JOIN `cnx_logger_biomimic_type` bio ON  bio.`biomimic_id`=logger.`biomimic_id` "
                 "INNER JOIN `cnx_logger_geographics` geo ON geo.`geo_id`=logger.`geo_id` "
                 "WHERE geo.`country`=\'%s\'") % country
        cursor.execute(query)
        result = cursor.fetchall()
        result = set(result)
        final_result = [[row[0], row[0]] for row in result]
        cursor.close()
        return final_result

    def getLocation(self, state_province):
        """Fetches Distinct locations given logger type and logger country"""
        cursor = self.connection.cursor()
        query = ("SELECT DISTINCT geo.location FROM `cnx_logger` logger "
                 "INNER JOIN `cnx_logger_biomimic_type` bio ON  bio.`biomimic_id`=logger.`biomimic_id` "
                 "INNER JOIN `cnx_logger_geographics` geo ON geo.`geo_id`=logger.`geo_id` "
                 "WHERE geo.`state_province`=\'%s\'") % state_province
        cursor.execute(query)
        result = cursor.fetchall()
        result = set(result)
        final_result = [[row[0], row[0]] for row in result]
        cursor.close()
        return final_result

    def getZone(self, biomimic_type):
        """Fetches Distinct Zones given logger biomimic type"""
        cursor = self.connection.cursor()
        query = ("SELECT DISTINCT prop.zone FROM `cnx_logger` logger "
                 "INNER JOIN `cnx_logger_biomimic_type` bio ON bio.`biomimic_id`=logger.`biomimic_id` "
                 "INNER JOIN `cnx_logger_properties` prop ON prop.`prop_id`=logger.`prop_id` "
                 "WHERE bio.biomimic_type=\'%s\'") % biomimic_type
        cursor.execute(query)
        result = cursor.fetchall()
        result = set(result)
        final_result = [[row[0], row[0]] for row in result]
        cursor.close()
        return final_result

    def getSubZone(self, value):
        """Fetches Distinct Subzones given logger biomimic type"""
        biomimic_type, zone_type = value.split("_")
        cursor = self.connection.cursor()
        if zone_type == "All":
            query = ("SELECT DISTINCT prop.sub_zone FROM `cnx_logger` logger "
                     "INNER JOIN `cnx_logger_biomimic_type` bio ON bio.`biomimic_id`=logger.`biomimic_id` "
                     "INNER JOIN `cnx_logger_properties` prop ON prop.`prop_id`=logger.`prop_id` "
                     "WHERE bio.biomimic_type=\'%s\'") % biomimic_type
        else:
            query = ("SELECT DISTINCT prop.sub_zone FROM `cnx_logger` logger "
                     "INNER JOIN `cnx_logger_biomimic_type` bio ON bio.`biomimic_id`=logger.`biomimic_id` "
                     "INNER JOIN `cnx_logger_properties` prop ON prop.`prop_id`=logger.`prop_id` "
                     "WHERE bio.biomimic_type=\'%s\' AND prop.zone=\'%s\'") % (biomimic_type, zone_type)
        cursor.execute(query)
        result = cursor.fetchall()
        result = set(result)
        final_result = [[row[0], row[0]] for row in result]
        cursor.close()
        return final_result

    def getWaveExp(self, biomimic_type):
        """Fetches Distinct Wave Exp given logger biomimic type"""
        cursor = self.connection.cursor()
        query = ("SELECT DISTINCT prop.wave_exp FROM `cnx_logger` logger "
                 "INNER JOIN `cnx_logger_biomimic_type` bio ON bio.`biomimic_id`=logger.`biomimic_id` "
                 "INNER JOIN `cnx_logger_properties` prop ON prop.`prop_id`=logger.`prop_id` "
                 "WHERE bio.biomimic_type=\'%s\'") % biomimic_type
        cursor.execute(query)
        result = cursor.fetchall()
        result = list(result)
        final_result = set()
        for row in result:
            if row[0] is None:
                final_result.add(("None", "None"))
            else:
                final_result.add((row[0], row[0]))        
        cursor.close()
        return final_result

    def getQueryResultsPreview(self, queryDict):
        """Fetches records form tables based on user query"""
        cursor = self.connection.cursor()
        output_type = queryDict.get("output_type")
        analysis_type = queryDict.get("analysis_type")
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
        query = ("SELECT %s, %s "
                    "FROM `cnx_logger` logger "
                    "INNER JOIN `cnx_logger_biomimic_type` biotype ON biotype.`biomimic_id` = logger.`biomimic_id` "
                    "INNER JOIN `cnx_logger_geographics` geo ON geo.`geo_id` = logger.`geo_id` "
                    "INNER JOIN `cnx_logger_properties` prop ON prop.`prop_id` = logger.`prop_id` "
                    "INNER JOIN `cnx_logger_temperature` temp ON temp.`logger_id` = logger.`logger_id` ") % (date_field, temp_field)
        where_condition = self.buildWhereCondition(queryDict)
        print(query + where_condition)
        cursor.execute(query + where_condition + " LIMIT 10 ")
        results = cursor.fetchall()
        results = list(results)
        final_result = [[result[0], round(result[1], 3)] for result in results]
        cursor.close()
        return final_result, query + where_condition

    def getQueryRawResults(self, db_query):
        """Fetches records form tables based on user query"""
        cursor = self.connection.cursor()
        cursor.execute(db_query)
        results = cursor.fetchall()
        results = list(results)
        final_result = [[result[0], result[1]] for result in results]
        cursor.close()
        return final_result
    
    def buildWhereCondition(self, queryDict):
        """Builds the where_condition for the Select Query"""
        analysis_type = queryDict.get("analysis_type")
        where = (" WHERE biotype.`biomimic_type`=\'%s\' AND geo.`country`=\'%s\' AND geo.`state_province`= \'%s\' AND geo.`location`=\'%s\'") % \
                (queryDict.get('biomimic_type'), queryDict.get('country'), \
                    queryDict.get('state_province'), queryDict.get('location'))
        if queryDict.get('zone') != "All":
            where += " AND prop.`zone`=\'%s\'" % (queryDict.get('zone'))
        if queryDict.get('sub_zone') != "All" :
            where += " AND prop.`sub_zone`=\'%s\'" % (queryDict.get('sub_zone'))
        if queryDict.get('wave_exp') != "All":
            if (queryDict.get('wave_exp') == 'None'): 
                where += " and prop.wave_exp is Null"
            else:
                where += " AND prop.`wave_exp`=\'%s\' " % (queryDict.get('wave_exp'))
        where += " AND cast(temp.Time_GMT as date) >= \'"+queryDict.get('start_date')+"\' AND cast(temp.Time_GMT as date) <= \'"+queryDict.get('end_date')+"\'"
        if analysis_type == "Daily":
            where += " GROUP BY cast(temp.Time_GMT as date)"
        elif analysis_type == "Monthly":
            where += " GROUP BY YEAR(temp.Time_GMT), MONTHNAME(temp.Time_GMT)"
        elif analysis_type == "Yearly":
            where += " GROUP BY YEAR(temp.Time_GMT)"
        else:
            pass
        return where

    def parseLoggerType(self, dataList, count):
        """Parse new Logger Type"""
        parsedRecord = dict()
        if (len(dataList) != 11):
            return None, 'L'
        else:
            if (self.isNotFloat(dataList[2]) or self.isNotFloat(dataList[3])):
                return None, 'F'
            else:
                if (dataList[0] == "None" or dataList[0] == ""):
                    return None, 'B'
                else:
                    parsedRecord['microsite_id'] = str(dataList[0]).upper()
                    parsedRecord['site'] = (dataList[1]).upper()
                    parsedRecord['field_lat'] = dataList[2]
                    parsedRecord['field_lon'] = dataList[3]
                    parsedRecord['location'] = dataList[4].capitalize()
                    parsedRecord['state_province'] = dataList[5].capitalize()
                    parsedRecord['country'] = dataList[6].capitalize()
                    parsedRecord['biomimic_type'] = dataList[7].capitalize()
                    parsedRecord['zone'] = dataList[8].capitalize()
                    parsedRecord['sub_zone'] = dataList[9].capitalize()
                    parsedRecord['wave_exp'] = None if (dataList[10] == "N/A") else dataList[10].capitalize()
                    parsedRecord['count'] = count
        return parsedRecord, ''        

    def isNotFloat(self, value):
        '''check whether value is float'''
        try:
            float(value)
            return False
        except ValueError:
            return True

    def insertLoggerType(self, records):
        """Inserts new Logger Type in DB"""
        cursor = self.connection.cursor()
        corruptRecords = ''
        properCounter = 0
        corruptCounter = 0
        corruptIndicator = False
        for record in records:
            isDuplicateMicrositeId = self.checkForDuplicate(cursor, record.get("microsite_id"))
            
            if not isDuplicateMicrositeId:

                geo_id = self.fetchExistingGeoId(cursor, record)                
                if (geo_id == None):
                    geo_id, corruptIndicator = self.insertGeoData(cursor, record)
                else:
                    geo_id = geo_id[0]
                if corruptIndicator:
                    self.connection.rollback()
                    corruptRecords += str(record.get('count')) + ',' + 'C' + ';'
                    corruptCounter += 1
                    continue
                
                prop_id = self.fetchExistingPropId(cursor, record)                
                if (prop_id == None):
                    prop_id, corruptIndicator = self.insertPropertiesData(cursor, record)
                else:
                    prop_id = prop_id[0]
                if corruptIndicator:
                    self.connection.rollback()
                    corruptRecords += str(record.get('count')) + ',' + 'C' + ';'
                    corruptCounter += 1
                    continue

                biomimic_id = self.fetchExistingBioId(cursor, record.get('biomimic_type'))
                if (biomimic_id == None):
                    biomimic_id, corruptIndicator = self.insertBiomimicTypeData(cursor, record.get('biomimic_type'))
                else:
                    biomimic_id = biomimic_id[0]
                if corruptIndicator:
                    self.connection.rollback()
                    corruptRecords += str(record.get('count')) + ',' + 'C' + ';'
                    corruptCounter += 1
                    continue

                logger_id, corruptIndicator = self.insertMicrositeData(cursor, record.get('microsite_id'), biomimic_id, geo_id, prop_id)
                if corruptIndicator:
                    self.connection.rollback()
                    corruptRecords += str(record.get('count')) + ',' + 'C' + ';'
                    corruptCounter += 1
                    continue
                else:
                    self.connection.commit() 
                    properCounter += 1
            else:
                corruptRecords += str(record.get('count')) + ',' + 'D' + ';'
                corruptCounter += 1 
        cursor.close()
        return properCounter, corruptCounter, corruptRecords
    
    def fetchExistingBioId(self, cursor, biomimic_type):
        """Check for Existing Biomimic Type Data"""
        query = ("SELECT `biomimic_id` from `cnx_logger_biomimic_type` WHERE `biomimic_type`=\'%s\'") % biomimic_type
        cursor.execute(query)
        result = cursor.fetchone()
        return result

    def insertBiomimicTypeData(self, cursor, biomimic_type):
        """Insert new Biomimic Type Data in DB"""
        corrupt = False
        query = ("INSERT INTO `cnx_logger_biomimic_type` (`biomimic_type`) VALUES (\'%s\')") % biomimic_type
        try:
            res = cursor.execute(query)
        except mysql.s.Error:
            res = 0
        if res == 1:
            pass
        else:
            corrupt = True
        return cursor.lastrowid, corrupt

    def fetchExistingGeoId(self, cursor, record):
        """Check for Existing GeoLocation Data"""
        query = ("SELECT `geo_id` from `cnx_logger_geographics` WHERE `site`=%s and `field_lat`=%s and `field_long`=%s and `location`=%s and `state_province`=%s and `country`=%s")        
        cursor.execute(query, (record.get("site"), record.get("field_lat"), record.get("field_lon"), record.get("location"), record.get("state_province"), record.get("country")))
        result = cursor.fetchone()
        return result

    def insertGeoData(self, cursor, record):
        """Insert new Geolocation Data in DB"""
        corrupt = False
        query = ("INSERT INTO `cnx_logger_geographics` (`site`, `field_lat`, `field_long`, `location`, `state_province`, `country`) VALUES (%s, %s, %s, %s, %s, %s)")
        try:
            res = cursor.execute(query, (record.get("site"), record.get("field_lat"), record.get("field_lon"), record.get("location"), record.get("state_province"), record.get("country")))
        except mysql.connector.Error:
            res = 0
        if res == 1:
            pass
        else:            
            corrupt = True
        return cursor.lastrowid, corrupt

    def fetchExistingPropId(self, cursor, record):
        """Check for Existing Properties Data"""
        if record.get('wave_exp') is None:
            query = ("SELECT `prop_id` from `cnx_logger_properties` WHERE `zone`=%s and `sub_zone`=%s and `wave_exp` IS NULL")
            cursor.execute(query, (record.get("zone"), record.get("sub_zone")))
        else:
            query = ("SELECT `prop_id` from `cnx_logger_properties` WHERE `zone`=%s and `sub_zone`=%s and `wave_exp`=%s")
            cursor.execute(query, (record.get("zone"), record.get("sub_zone"), record.get("wave_exp")))
        result = cursor.fetchone()
        return result

    def insertPropertiesData(self, cursor, record):
        """Insert new Properties Data in DB"""
        corrupt = False
        if record.get('wave_exp') is None:
            query = ("INSERT INTO `cnx_logger_properties` (`zone`, `sub_zone`, `wave_exp`) VALUES (%s, %s, NULL)")
            try:    
                res = cursor.execute(query, (record.get("zone"), record.get("sub_zone")))
            except mysql.connector.Error:
                res = 0
        else:
            query = ("INSERT INTO `cnx_logger_properties` (`zone`, `sub_zone`, `wave_exp`) VALUES (%s, %s, %s)")  
            try:  
                res = cursor.execute(query, (record.get("zone"), record.get("sub_zone"), record.get("wave_exp")))
            except mysql.connector.Error:
                res = 0
        
        if res == 1:
            pass
        else:
            corrupt = True
        return cursor.lastrowid, corrupt

    def insertMicrositeData(self, cursor, microsite_id, biomimic_id, geo_id, prop_id):
        """Insert new Microsite Id Data in DB"""
        corrupt = False
        query = ("INSERT INTO `cnx_logger` (`microsite_id`, `biomimic_id`, `geo_id`, `prop_id`) VALUES (%s, %s, %s, %s)")
        try:
            res = cursor.execute(query, (microsite_id, biomimic_id, geo_id, prop_id))
        except mysql.connector.Error:
                res = 0
        if res == 1:
            pass
        else:
            corrupt = True
        return cursor.lastrowid, corrupt

    def checkForDuplicate(self, cursor, microsite_id):
        """Check for Duplicate Microsite Id in DB"""
        query = ("SELECT `logger_id` FROM `cnx_logger` WHERE `microsite_id`=\'%s\'") % microsite_id
        cursor.execute(query)
        results = cursor.fetchall()
        results = list(results)
        return len(results) > 0

    def parseLoggerTemp(self, dataList, count):
        """Parse new Logger Temperature Data"""
        parsedRecord = dict()
        cursor = self.connection.cursor()
        if (len(dataList) != 2):
            return None, 'L'
        else:
            if (self.isNotFloat(dataList[1])):
                return None, 'F'
            else:
                if (dataList[0] == "None" or dataList[0] == ""):
                    return None, 'B'
                else:
                    #handle datetime error
                    try:
                        parsedRecord['Time_GMT'] = datetime.datetime.strptime(dataList[0],'%m/%d/%Y %H:%M')
                    except ValueError:
                        try:
                            parsedRecord['Time_GMT'] = datetime.datetime.strptime(dataList[0],'%m/%d/%y %H:%M')
                        except ValueError:
                            return None, 'FT'
                    parsedRecord['Temp_C'] = dataList[1] 
                    parsedRecord['count'] = count            
        return parsedRecord, ''


    def insertLoggerTemp(self, records,logger_id):
        """Inserts new Logger Type in DB"""
        cursor = self.connection.cursor()
        corruptRecords = ''
        properCounter = 0
        corruptCounter = 0
        corruptIndicator = False        
        query = ("INSERT INTO `cnx_logger_temperature` (`logger_id`, `Time_GMT`, `Temp_C`) VALUES (%s, %s, %s)")
        for record in records:
            #handle duplicate entry problem while inserting data
            try:
                res = cursor.execute(query,(logger_id, record.get("Time_GMT"),record.get("Temp_C")))
            except MySQLdb.DatabaseError as err:
                res = 0
            if res == 1:
                self.connection.commit()
                properCounter+=1
            else:
                self.connection.rollback()
                corruptCounter+=1
                corruptRecords = corruptRecords + str(record.get("count")) + ',' + 'D' + ';'
        cursor.close()
        return properCounter, corruptCounter, corruptRecords

    def FindMicrositeId(self, id):
        '''Fecth logger_id according to microsite_id'''
        cursor = self.connection.cursor()
        query = '''SELECT `logger_id` as 'logger_id' FROM `cnx_logger` WHERE microsite_id=''' + "\'"+ id +"\'"
        cursor.execute(query)
        results = cursor.fetchall()
        results = list(results)
        if len(results) == 0:
            return None
        else:
            return results[0]

    def close(self):
        self.connection.close()




