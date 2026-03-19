import pytest

from mdlcalc.calc import (
    QUANT_BYTES,
    model_memory_gb,
    parse_input,
    resolve_all,
    resolve_quant,
)


class TestParseInput:
    @pytest.mark.parametrize(
        "raw, expected_params, expected_quant, expected_unit",
        [
            (["45B-Q4_K_M"], 45.0, "Q4_K_M", "B"),
            (["7B", "Q8_0"], 7.0, "Q8_0", "B"),
            (["qwen3.5", "0.8B"], 0.8, None, "B"),
            (["13b-q4_0"], 13.0, "Q4_0", "B"),
            (["Llama-3", "70B", "Q6_K"], 70.0, "Q6_K", "B"),
            (["0.5B"], 0.5, None, "B"),
            (["720b", "q2_k"], 720.0, "Q2_K", "B"),
            (["700M"], 0.7, None, "M"),
            (["1T"], 1000.0, None, "T"),
            (["1.5T", "Q4_K_M"], 1500.0, "Q4_K_M", "T"),
            # Numeric type IDs
            (["7B", "15"], 7.0, "15", "B"),
            (["45B-2"], 45.0, "2", "B"),
            (["13B", "18"], 13.0, "18", "B"),
            # Prefix quant
            (["7B", "Q4"], 7.0, "Q4", "B"),
            (["13B-Q3"], 13.0, "Q3", "B"),
        ],
    )
    def test_parse(self, raw, expected_params, expected_quant, expected_unit):
        params, quant, unit = parse_input(raw)
        assert params == pytest.approx(expected_params)
        assert quant == expected_quant
        assert unit == expected_unit

    def test_no_params(self):
        params, quant, unit = parse_input(["qwen3.5", "Q4_K_M"])
        assert params is None
        assert quant == "Q4_K_M"
        assert unit == "B"


class TestResolveQuant:
    def test_numeric_id(self):
        assert resolve_quant("15") == ["Q4_K_M"]
        assert resolve_quant("0") == ["F32"]
        assert resolve_quant("18") == ["Q6_K"]
        assert resolve_quant("1") == ["F16"]

    def test_aliases(self):
        assert resolve_quant("Q3_K") == ["Q3_K_M"]
        assert resolve_quant("Q4_K") == ["Q4_K_M"]
        assert resolve_quant("Q5_K") == ["Q5_K_M"]

    def test_direct_name(self):
        assert resolve_quant("Q4_K_M") == ["Q4_K_M"]
        assert resolve_quant("F16") == ["F16"]

    def test_prefix_expands(self):
        assert resolve_quant("Q4") == ["Q4_0", "Q4_1", "Q4_K_M", "Q4_K_S"]
        assert resolve_quant("Q3") == ["Q3_K_L", "Q3_K_M", "Q3_K_S"]
        assert resolve_quant("Q5") == ["Q5_0", "Q5_1", "Q5_K_M", "Q5_K_S"]
        assert resolve_quant("Q2") == ["Q2_K"]
        assert resolve_quant("Q6") == ["Q6_K"]
        assert resolve_quant("Q8") == ["Q8_0"]
        assert resolve_quant("F") == ["F16", "F32"]

    def test_unknown(self):
        assert resolve_quant("Q99_X") == []
        assert resolve_quant("99") == []


class TestResolveAll:
    def test_returns_all(self):
        all_quants = resolve_all()
        assert len(all_quants) == len(QUANT_BYTES)
        assert set(all_quants) == set(QUANT_BYTES.keys())

    def test_sorted_descending(self):
        all_quants = resolve_all()
        sizes = [QUANT_BYTES[q] for q in all_quants]
        assert sizes == sorted(sizes, reverse=True)


class TestModelMemory:
    def test_7b_q4_k_m(self):
        bare, overhead = model_memory_gb(7.0, "Q4_K_M")
        assert bare == pytest.approx(3.80, abs=0.01)
        assert overhead == pytest.approx(4.56, abs=0.01)

    def test_7b_f16(self):
        bare, overhead = model_memory_gb(7.0, "F16")
        assert bare == pytest.approx(13.0, abs=0.01)
        assert overhead == pytest.approx(15.6, abs=0.01)

    def test_all_quants_covered(self):
        for q in QUANT_BYTES:
            bare, overhead = model_memory_gb(1.0, q)
            assert bare == pytest.approx(QUANT_BYTES[q])
            assert overhead == pytest.approx(bare * 1.2)
