"""DE-07: silver framework (coercion, specs, provenance) and family parsers on synthetic bronze files."""

from __future__ import annotations

import hashlib
import json

import pandas as pd
import pytest

from flamesafe.pipeline import silver
from flamesafe.pipeline import silver_parsers as sp
from flamesafe.pipeline.silver import Col, Issues, apply_spec, coerce, split_table


# ----------------------------------------------------------------------------- coercion
def test_float_tokens_become_null_plus_flag_never_zero():
    vals, flags = coerce(["0.21", "RAMP", "#DIV/0!", "", None, "–", 3], Col("x", "x", "float"))
    assert vals == [0.21, None, None, None, None, None, 3.0]
    assert flags == [None, "RAMP", "#DIV/0!", None, None, "–", None]


def test_bool_category_id_and_date():
    assert coerce(["Yes", "no", "flash"], Col("a", "a", "bool_yesno"))[0] == [True, False, None]
    v, f = coerce(["SE", "FT", "-"], Col("b", "b", "category", {"se": "self_extinguished", "ft": "flow_terminated"}))
    assert v == ["self_extinguished", "flow_terminated", None] and f == [None, None, "-"]
    assert coerce(["21088 B1", "21088a1"], Col("c", "c", "id"))[0] == ["21088B1", "21088A1"]
    v, f = coerce(["3/5/2009", "10/24/09", "bad"], Col("d", "d", "date", date_formats=("%m/%d/%Y", "%m/%d/%y")))
    assert v[0] == pd.Timestamp("2009-03-05") and v[1] == pd.Timestamp("2009-10-24") and v[2] is None and f[2] == "bad"


def test_int_rejects_non_integer():
    v, f = coerce(["3", "3.0", "3.5"], Col("n", "n", "int"))
    assert v == [3, 3, None] and f == [None, None, "3.5"]


# ----------------------------------------------------------------------------- specs
def test_apply_spec_missing_column_is_error_and_extra_is_warning():
    issues = Issues()
    df, colmap = apply_spec([["1", "x", ""]], ["  XO2  before test", "Other", "Empty"], [2],
                            [Col("XO2 before test", "xo2"), Col("Absent", "absent")], "t", issues)
    assert list(df.columns) == ["source_row", "xo2", "other"] and df.loc[0, "source_row"] == 2  # empty extra dropped
    assert colmap["xo2"] == "XO2 before test"
    assert sorted(i["level"] for i in issues.items) == ["error", "warning"]
    assert issues.n_errors == 1


def test_regex_source_matches_header_with_lost_subscript():
    issues = Issues()
    df, _ = apply_spec([["0.21", "0.3"]], ["O initial ambient composition; mole fraction",
                                           "CO initial ambient composition; mole fraction"], [2],
                       [Col(r"re:^O\S* initial ambient composition", "x_o2", "float"),
                        Col(r"re:^CO\S* initial ambient composition", "x_co2", "float")], "t", issues)
    assert issues.n_errors == 0 and df.loc[0, "x_o2"] == 0.21 and df.loc[0, "x_co2"] == 0.3


def test_split_table_drops_blank_rows_and_keeps_physical_numbers():
    rows = [["h1", "h2"], ["1", "2"], ["", ""], ["3", "4"], [None, None]]
    header, body, nums, blank = split_table(rows, 1)
    assert header == ["h1", "h2"] and nums == [2, 4] and blank == 2


# ----------------------------------------------------------------------------- figure points (PSI-117 layout)
def test_figure_points_blocks_roles_and_row_labels():
    rows = [["C7", "Do", "Dext_HF", "", "P (atm)", "Dext_CF_EXPT", "", "P (atm)", "Dext_CF_ErrorBar+"],
            ["Expt", "3.91", "3.28", "", "0.5", "1.89", "", "0.5", "2.29"],
            ["", "3.55", "2.79", "", "1", "1.7", "", "1", "2.0"],
            ["Sim", "2", "1.9", "", "", "", "", "", ""]]
    pts = pd.DataFrame(sp.figure_points(rows, "f"))
    b1 = pts[pts.block == 1]
    assert b1.role.tolist() == ["experiment", "experiment", "model"]
    assert b1.source_row.tolist() == [2, 3, 4]
    assert set(pts[pts.block == 2].role) == {"experiment"} and set(pts[pts.block == 3].role) == {"error_bar"}


# ----------------------------------------------------------------------------- family parser end-to-end (FLEX)
def _bronze(tmp_path, psi_id, name, content: bytes):
    d = tmp_path / "bronze" / "files" / psi_id
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_bytes(content)
    (d / f"{name}.meta.json").write_text(json.dumps({"sha256": hashlib.sha256(content).hexdigest(), "http_status": 200}))


def test_flex_parser_end_to_end(tmp_path, monkeypatch):
    monkeypatch.setenv("FLAMESAFE_DATA_DIR", str(tmp_path))
    header = ("FLEX Test #,FLEX Identifier,Test Date,Test GMT,Fuel,Ambient pressure; mmHg,"
              "O initial ambient composition; mole fraction,N initial ambient composition; mole fraction,"
              "CO initial ambient composition; mole fraction,He initial ambient composition; mole fraction,"
              "Droplet initial diameter; mm,Visible flame extinction diameter; mm,Burning rate; mm,Burn time; s,Test end\n")
    body = "1,20CAL08,3/5/2009,17:22:03,Methanol,757.7,0.21,0.79,0,0,1.69,0.89,0.52,~6,Disruption\n" \
           "2,20CAL10,10/24/09,19:20:06,Heptane,0,0.21,0.49,0.3,0,–,–,0.6,3.1,Extinction\n,,,,,,,,,,,,,,\n"
    _bronze(tmp_path, "PSI-69", "PSI-69_Experimental table_FLEX.csv", (header + body).encode("cp1252"))
    issues = Issues()
    df, meta = sp.parse_psi69(issues)["psi69__flex_droplets"]
    assert len(df) == 2 and meta["blank_rows_dropped"] == 1 and meta["encoding"] == "cp1252"
    assert df.x_co2.tolist() == [0.0, 0.3] and df.fuel.tolist() == ["methanol", "heptane"]
    assert df.loc[1, "d0_mm__flag"] == "–" and pd.isna(df.loc[1, "d0_mm"])
    assert df.loc[0, "burn_time_s__flag"] == "~6" and df.test_end.tolist() == ["disruption", "extinction"]
    assert {"psi_id", "source_file", "source_sha256", "source_row"} <= set(df.columns) and df.source_row.tolist() == [2, 3]
    assert any("pressure <= 0" in i["issue"] for i in issues.items)


def test_missing_bronze_file_is_reported_by_runner(tmp_path, monkeypatch):
    monkeypatch.setenv("FLAMESAFE_DATA_DIR", str(tmp_path))
    rep = silver.run(only=["psi69_flex"], out_dir=tmp_path / "silver" / "tables")
    assert rep["n_errors"] == 1 and "bronze file missing" in rep["issues"][0]["issue"]


@pytest.mark.integration
def test_real_bronze_parses_without_errors():
    rep = silver.run(out_dir=None)
    assert rep["n_errors"] == 0
    t = rep["tables"]
    assert t["psi159__normal_flames"]["rows"] == 179 and t["psi159__inverse_flames"]["rows"] == 154
    assert t["psi10__normal_flames"]["rows"] == 207 and t["psi69__flex_droplets"]["rows"] == 274
