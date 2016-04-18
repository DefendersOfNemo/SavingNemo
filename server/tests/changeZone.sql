START TRANSACTION;

 UPDATE cnx_logger_properties SET zone="Mid-lower" WHERE zone="Lower-mid";

 
 UPDATE cnx_logger_properties SET zone="Mid-upper" WHERE zone="Upper-mid";

ROLLBACK;
 COMMIT;