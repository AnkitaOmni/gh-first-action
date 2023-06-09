SHOW PROCESSLIST;

SHOW VARIABLES
WHERE
    VARIABLE_NAME = 'event_scheduler';

SELECT
    *
FROM
    information_schema.EVENTS;

SET
    GLOBAL event_scheduler = ON;

SET
    GLOBAL event_scheduler = OFF;

SHOW EVENTS
FROM
    OMNICOMP_BECH_Dishant;

CREATE TABLE Demo (
    id INT PRIMARY KEY AUTO_INCREMENT,
    message VARCHAR(255) NOT NULL,
    created_on DATETIME NOT NULL
);

CREATE EVENT IF NOT EXISTS one_time_event ON SCHEDULE AT CURRENT_TIMESTAMP DO
INSERT INTO
    Demo(message, created_on)
VALUES
    ('Test MySQL Event 1', NOW());

CREATE EVENT one_time_event ON SCHEDULE AT CURRENT_TIMESTAMP + INTERVAL 1 MINUTE ON COMPLETION PRESERVE DO
INSERT INTO
    Demo(message, created_at)
VALUES
    ('Test MySQL Event 2', NOW());

CREATE EVENT IF NOT EXISTS reurring_event ON SCHEDULE EVERY 1 MINUTE STARTS CURRENT_TIMESTAMP ENDS CURRENT_TIMESTAMP + INTERVAL 1 HOUR DO
INSERT INTO
    Demo (message, created_on)
VALUES
    ('RecurringTimeEvent', NOW());