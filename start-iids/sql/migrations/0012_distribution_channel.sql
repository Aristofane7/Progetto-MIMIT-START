-- Distribution channel dimension (issue #8 follow-up, ADR-022).
-- Spec anchor: Piano di Sviluppo (Allegato 4) OR7.5 names Gresmalt's own
-- distribution split as B2C (business-to-consumer) / B2B (business-to-business)
-- ("Il calcolo del Customer Rating (CR) potrebbe risultare complesso per la
-- diversa tipologia di cientela di Gresmalt: B2C e B2B... Verranno creati due
-- indicatori distinti (B2C-CR e B2B-CR)"). `fact_product_sales` had no channel
-- attribute at all — this was a genuine schema gap, not a hidden field.

CREATE TABLE dim_distribution_channel (
    channel_id      VARCHAR(32) PRIMARY KEY,
    channel_name    VARCHAR(128) NOT NULL,
    channel_type    VARCHAR(16) NOT NULL,
    CHECK (channel_type IN ('B2B', 'B2C'))
);

-- The 2 real channel types the Piano itself names for Gresmalt (OR7.5) —
-- not a fabricated taxonomy. Real per-channel sales volumes remain an
-- external blocker (same class as P0-03/P0-04, see ADR-022): this table is
-- reference data (like the unit library or the 22 RP6.8 clusters), ready to
-- receive real sales rows once available.
INSERT INTO dim_distribution_channel (channel_id, channel_name, channel_type) VALUES
    ('B2B', 'Business-to-Business', 'B2B'),
    ('B2C', 'Business-to-Consumer', 'B2C');

ALTER TABLE fact_product_sales ADD COLUMN channel_id VARCHAR(32)
    REFERENCES dim_distribution_channel(channel_id);
