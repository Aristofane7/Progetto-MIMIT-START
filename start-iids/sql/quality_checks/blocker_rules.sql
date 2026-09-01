-- Data quality BLOCKER checks. Spec ref: sec. 29.3.
-- Each query below returns the rows that VIOLATE a blocker rule — i.e. rows that
-- must prevent a calc_run from reaching status='SUCCESS' until resolved. These
-- are reference diagnostic queries (run by the QA/audit job, sec. 54 Agent A10),
-- not triggers — a calc_run must never fail silently (sec. 49).

-- 1. Functional unit mismatch between current run and its declared baseline.
-- BLOCKER: "FU current != baseline"
SELECT r.calc_run_id, r.baseline_id, b.functional_unit AS baseline_fu
FROM audit_calc_run r
JOIN dim_baseline b ON b.baseline_id = r.baseline_id
WHERE r.status = 'RUNNING'
  -- the caller supplies the run's own functional unit for comparison; this
  -- reference query flags any run whose baseline record does not resolve.
  AND b.functional_unit IS NULL;

-- 2. Coefficient set mismatch between current run and its baseline.
-- BLOCKER: "coefficient set current != baseline"
-- COALESCE(...,'') keeps the comparison NULL-safe and portable (no dialect-specific
-- IS DISTINCT FROM), since audit_calc_run.coefficient_set_id is nullable.
SELECT r.calc_run_id, r.coefficient_set_id, b.coefficient_set_id AS baseline_coefficient_set_id
FROM audit_calc_run r
JOIN dim_baseline b ON b.baseline_id = r.baseline_id
WHERE COALESCE(r.coefficient_set_id, '') != COALESCE(b.coefficient_set_id, '');

-- 3. Missing primary key on a core fact row (example: production lot without a lot_id).
-- BLOCKER: "primary key mancante"
SELECT *
FROM fact_production_lot
WHERE lot_id IS NULL OR TRIM(lot_id) = '';

-- 4. Coefficient placeholder not approved.
-- BLOCKER: "coefficient placeholder non approvato"
SELECT c.coefficient_id, c.coefficient_set_id, s.status
FROM dim_coefficient c
JOIN dim_coefficient_set s ON s.coefficient_set_id = c.coefficient_set_id
WHERE s.status != 'APPROVED';

-- 5. Baseline absent for a run that requires comparability.
-- BLOCKER: "baseline assente"
SELECT r.calc_run_id
FROM audit_calc_run r
WHERE r.baseline_id IS NULL AND r.engine IN ('EEA', 'TEI', 'EFA', 'ECOFA', 'SFA');

-- 6. Referential integrity: a lot referencing a non-existent product.
-- BLOCKER: implied by "referential integrity 100%" (Stage 1 DoD, sec. 53).
SELECT l.lot_id, l.product_id
FROM fact_production_lot l
LEFT JOIN dim_product p ON p.product_id = l.product_id
WHERE p.product_id IS NULL;

-- 7. Unknown/unrecognized canonical unit on a process observation.
-- BLOCKER: "unit conversion unknown"
SELECT o.observation_id, o.variable_code, o.canonical_unit
FROM fact_process_observation o
JOIN dim_variable v ON v.variable_code = o.variable_code
WHERE o.canonical_unit IS NULL
   OR (v.canonical_unit IS NOT NULL AND o.canonical_unit != v.canonical_unit);
