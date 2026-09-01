-- Product Design workflow (phases A-F) and Design -> Process Requirements bridge.
-- Spec ref: sec. 22-23.

CREATE TABLE fact_design_project (
    design_project_id        VARCHAR(128) PRIMARY KEY,
    project_name             VARCHAR(255) NOT NULL,
    brief_date               DATE,
    use_destination           VARCHAR(64),
    target_market            VARCHAR(255),
    positioning              TEXT,
    production_constraints   TEXT,
    timeline_notes           TEXT,
    project_status           VARCHAR(32) NOT NULL,
    coordinator              VARCHAR(255),
    created_at               TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE fact_design_option (
    design_option_id          VARCHAR(128) PRIMARY KEY,
    design_project_id         VARCHAR(128) NOT NULL REFERENCES fact_design_project(design_project_id),
    option_code               VARCHAR(32),
    reference_cluster_id      INTEGER,
    reference_cluster_version VARCHAR(64),
    format_mm                 VARCHAR(64),
    thickness_mm              NUMERIC(12,4),
    slip_class                VARCHAR(64),
    surface_effect            VARCHAR(128),
    colour_palette            VARCHAR(512),
    data_rationale            TEXT,
    created_at                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reference_cluster_id, reference_cluster_version)
       REFERENCES dim_product_cluster(cluster_id, cluster_version)
);

CREATE TABLE fact_prototype (
    prototype_id             VARCHAR(128) PRIMARY KEY,
    design_option_id         VARCHAR(128) NOT NULL REFERENCES fact_design_option(design_option_id),
    prototype_version        INTEGER NOT NULL,
    body_colourant           VARCHAR(255),
    pad                      VARCHAR(255),
    glaze                    VARCHAR(255),
    granules                 VARCHAR(255),
    surface_application      VARCHAR(512),
    graphic_file_reference   VARCHAR(512),
    firing_curve_reference   VARCHAR(512),
    created_at               TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (design_option_id, prototype_version)
);

CREATE TABLE fact_design_decision (
    decision_id              BIGINT PRIMARY KEY,
    design_option_id         VARCHAR(128) NOT NULL REFERENCES fact_design_option(design_option_id),
    decision_ts              TIMESTAMP NOT NULL,
    technical_status         VARCHAR(32),
    trend_alignment          NUMERIC(12,8),
    target_alignment         NUMERIC(12,8),
    decision_code            VARCHAR(32) NOT NULL,
    decision_reason          TEXT NOT NULL,
    decided_by               VARCHAR(255),
    CHECK (decision_code IN ('GO','ITERATE','STOP','HOLD_QUEUE','NEXT_CYCLE'))
);

-- Design event log for phase-change audit (sec. 22.6). No PK constraint is
-- prescribed by the spec beyond an append-only event stream.
CREATE TABLE audit_design_event (
    design_event_id          BIGINT PRIMARY KEY,
    design_project_id        VARCHAR(128) NOT NULL REFERENCES fact_design_project(design_project_id),
    stage                    VARCHAR(8) NOT NULL,
    event_ts                 TIMESTAMP NOT NULL,
    actor                    VARCHAR(255),
    input_reference          VARCHAR(512),
    output_reference         VARCHAR(512),
    notes                    TEXT,
    CHECK (stage IN ('A','B','C','D','E','F'))
);

CREATE TABLE bridge_design_process_requirement (
    design_option_id       VARCHAR(128) NOT NULL REFERENCES fact_design_option(design_option_id),
    process_id             VARCHAR(64) NOT NULL REFERENCES dim_process(process_id),
    requirement_code       VARCHAR(128) NOT NULL,
    required_value_num     NUMERIC(24,8),
    required_value_text    VARCHAR(255),
    unit                   VARCHAR(32),
    tolerance_min          NUMERIC(24,8),
    tolerance_max          NUMERIC(24,8),
    source                 VARCHAR(255),
    PRIMARY KEY (design_option_id, process_id, requirement_code)
);
