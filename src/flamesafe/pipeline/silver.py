"""bronze -> silver. Task DE-07.

One parser per source-table family (registry pattern). Each parser must:
  * keep original column names in metadata, emit snake_case typed columns;
  * convert missing tokens (configs/pipeline.yaml) to NULL + <col>__flag;
  * annotate units explicitly (column suffix: _kpa, _k, _cm_s, _xo2 ...);
  * attach provenance columns: psi_id, source_file, source_sha256, source_row.
"""
