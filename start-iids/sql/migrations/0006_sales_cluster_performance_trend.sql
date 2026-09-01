-- Sales, cluster performance and trend intelligence.
-- Spec ref: sec. 20-21.

CREATE TABLE fact_product_sales (
    product_sales_id       BIGINT PRIMARY KEY,
    product_id             VARCHAR(128) NOT NULL REFERENCES dim_product(product_id),
    period_start           DATE NOT NULL,
    period_end             DATE NOT NULL,
    market_id              VARCHAR(64),
    sales_m2               NUMERIC(20,6),
    revenue_eur            NUMERIC(20,4),
    source_system          VARCHAR(64),
    ingestion_ts           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE fact_cluster_performance (
    cluster_perf_id        BIGINT PRIMARY KEY,
    cluster_id             INTEGER NOT NULL,
    cluster_version        VARCHAR(64) NOT NULL,
    period_start           DATE NOT NULL,
    period_end             DATE NOT NULL,
    product_count          INTEGER,
    sales_total_m2         NUMERIC(20,6),
    sales_m2_per_product   NUMERIC(20,6),
    trend_class            VARCHAR(16),
    FOREIGN KEY (cluster_id, cluster_version)
      REFERENCES dim_product_cluster(cluster_id, cluster_version),
    CHECK (trend_class IN ('GROWTH','STABLE','DECLINE','UNKNOWN'))
);

CREATE TABLE dim_trend (
    trend_id              VARCHAR(128) PRIMARY KEY,
    trend_category        VARCHAR(64) NOT NULL,
    trend_value           VARCHAR(255) NOT NULL,
    source_type           VARCHAR(32) NOT NULL,
    source_name           VARCHAR(255),
    period_start          DATE,
    period_end            DATE,
    signal_strength       NUMERIC(12,8),
    analyst_note          TEXT,
    source_reference      VARCHAR(512),
    CHECK (source_type IN ('HISTORICAL','CONTEMPORARY','SCENARIO','FORECAST'))
);
-- FORECAST rows must stay disabled (feature flag trend_forecast_rows=false) until
-- the ARIMA model is validated and approved — sec. 21.2, FUTURE.

CREATE TABLE bridge_cluster_trend (
    cluster_id          INTEGER NOT NULL,
    cluster_version     VARCHAR(64) NOT NULL,
    trend_id            VARCHAR(128) NOT NULL REFERENCES dim_trend(trend_id),
    alignment_score     NUMERIC(12,8),
    evidence_note       TEXT,
    PRIMARY KEY (cluster_id, cluster_version, trend_id),
    FOREIGN KEY (cluster_id, cluster_version)
      REFERENCES dim_product_cluster(cluster_id, cluster_version)
);
