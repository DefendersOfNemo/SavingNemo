CREATE DATABASE IF NOT EXISTS test;

USE test;

CREATE TABLE `cnx_logger_geographics` (                  
                          `geo_id` int(6) NOT NULL AUTO_INCREMENT,                 
                          `site` varchar(30) DEFAULT NULL,                       
                          `field_lat` decimal(18,12) DEFAULT NULL,                     
                          `field_long` decimal(18,12) DEFAULT NULL,                    
                          `location` varchar(30) DEFAULT NULL,                   
                          `state_province` varchar(30) DEFAULT NULL,                      
                          `country` varchar(30) DEFAULT NULL,                    
                          PRIMARY KEY (`geo_id`)                                    
						) ENGINE=InnoDB  DEFAULT CHARSET=utf8;  

CREATE TABLE `cnx_logger_biomimic_type` (                       
                   `biomimic_id` int(6) NOT NULL AUTO_INCREMENT,             
                   `biomimic_type` varchar(30) NOT NULL,                        
                   PRIMARY KEY (`biomimic_id`)                                                         
                 ) ENGINE=InnoDB  DEFAULT CHARSET=utf8;  
                 
CREATE TABLE `cnx_logger_properties` (                   
                         `prop_id` int(6) NOT NULL AUTO_INCREMENT,             
                         `zone` varchar(30) DEFAULT NULL,                       
                         `sub_zone` varchar(30) DEFAULT NULL,                    
                         `wave_exp` varchar(30) DEFAULT NULL,                   
                         PRIMARY KEY (`prop_id`)                                
                       ) ENGINE=InnoDB  DEFAULT CHARSET=utf8;  

CREATE TABLE `cnx_logger` (                                                                    
              `logger_id` int(6) NOT NULL AUTO_INCREMENT,                                                       
              `microsite_id` varchar(30) NOT NULL,                                                        
              `biomimic_id` int(6) NOT NULL,                                                              
              `geo_id` int(6) NOT NULL,                                                                   
              `prop_id` int(6) NOT NULL,                                                                  
              PRIMARY KEY (`logger_id`),                                                                         
              KEY `biomimic_id` (`biomimic_id`),                                                            
              KEY `geo_id` (`geo_id`),                                                                      
              KEY `prop_id` (`prop_id`),                                                                    
              CONSTRAINT `biomimicID` FOREIGN KEY (`biomimic_id`) REFERENCES `cnx_logger_biomimic_type` (`biomimic_id`),  
              CONSTRAINT `geoID` FOREIGN KEY (`geo_id`) REFERENCES `cnx_logger_geographics` (`geo_id`),       
              CONSTRAINT `propID` FOREIGN KEY (`prop_id`) REFERENCES `cnx_logger_properties` (`prop_id`)   
            ) ENGINE=InnoDB  DEFAULT CHARSET=utf8;

CREATE TABLE `cnx_logger_temperature` ( 
				 `logger_temp_id` int(6) NOT NULL AUTO_INCREMENT PRIMARY KEY, 
                 `logger_id` int(6) NOT NULL,                                                          
                 `Time_GMT` datetime NOT NULL,                                                      
                 `Temp_C` double(18, 12) NOT NULL,
         unique(`logger_id`,`Time_GMT`,`Temp_C`),                        
                 CONSTRAINT `loggerID` FOREIGN KEY (`logger_id`) REFERENCES `cnx_logger` (`logger_id`)  
               ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `cnx_logger_metadata` (
				 `microsite_id` varchar(30) NOT NULL,
				 `logger_count` int(11) NOT NULL,
				 `logger_MinDate` datetime NOT NULL,
				 `logger_MaxDate` datetime NOT NULL,
				 PRIMARY KEY (`microsite_id`)
				) ENGINE=InnoDB DEFAULT CHARSET=utf8;