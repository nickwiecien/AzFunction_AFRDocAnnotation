CREATE TABLE DELIVERY_DOC_DETAILS (
ID int IDENTITY(1,1)
, FILENAME VARCHAR(256)
, ANNOTATED_FILENAME VARCHAR(256)
, TANK_NUMBER VARCHAR(256)
, ANNOTATED_TANK_NUMBER VARCHAR(256)
, END_GALLONS VARCHAR(256)
, ANNOTATED_END_GALLONS VARCHAR(256)
, REQUESTED_DELIVERY_DATE VARCHAR(256)
, ANNOTATED_REQUESTED_DELIVERY_DATE VARCHAR(256)
, ACTUAL_DELIVERY_DATE VARCHAR(256)
, ANNOTATED_ACTUAL_DELIVERY_DATE VARCHAR(256)
, VALIDATED BIT) 