CREATE TABLE IF NOT EXISTS highspot_app (
    endpoint_id INTEGER PRIMARY KEY,
    post_data TEXT,
    post_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE TRIGGER IF NOT EXISTS [UpdatePostTimestamp] 
    AFTER UPDATE
    ON highspot_app
    FOR EACH ROW
BEGIN
    UPDATE highspot_app SET post_timestamp=CURRENT_TIMESTAMP WHERE post_data=NEW.post_data;
END;