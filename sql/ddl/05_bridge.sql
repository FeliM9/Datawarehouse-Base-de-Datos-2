CREATE TABLE dw.bridge_adjudicacion_rubro (
	bridge_adjudicacion_rubro_id bigserial NOT NULL,
	fact_adjudicacion_id int8 NOT NULL,
	rubro_id int4 NOT NULL,
	CONSTRAINT bridge_adjudicacion_rubro_pkey PRIMARY KEY (bridge_adjudicacion_rubro_id),
	CONSTRAINT uq_adjudicacion_rubro UNIQUE (fact_adjudicacion_id, rubro_id)
);


-- dw.bridge_adjudicacion_rubro foreign keys

ALTER TABLE dw.bridge_adjudicacion_rubro ADD CONSTRAINT bridge_adjudicacion_rubro_fact_adjudicacion_id_fkey FOREIGN KEY (fact_adjudicacion_id) REFERENCES dw.fact_adjudicacion(fact_adjudicacion_id);
ALTER TABLE dw.bridge_adjudicacion_rubro ADD CONSTRAINT bridge_adjudicacion_rubro_rubro_id_fkey FOREIGN KEY (rubro_id) REFERENCES dw.dim_rubro(rubro_id);