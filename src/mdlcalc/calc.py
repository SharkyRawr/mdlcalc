import re

QUANT_BYTES = {
    "F32": 26.00 / 7,
    "F16": 13.00 / 7,
    "Q8_0": 6.70 / 7,
    "Q6_K": 5.15 / 7,
    "Q5_K_M": 4.45 / 7,
    "Q5_K_S": 4.33 / 7,
    "Q5_1": 4.70 / 7,
    "Q5_0": 4.30 / 7,
    "Q4_K_M": 3.80 / 7,
    "Q4_K_S": 3.56 / 7,
    "Q4_1": 3.90 / 7,
    "Q4_0": 3.50 / 7,
    "Q3_K_L": 3.35 / 7,
    "Q3_K_M": 3.06 / 7,
    "Q3_K_S": 2.75 / 7,
    "Q2_K": 2.67 / 7,
}

# Numeric type IDs from the llama.cpp quantization table
_QUANT_BY_ID = {
    0: "F32",
    1: "F16",
    2: "Q4_0",
    3: "Q4_1",
    7: "Q8_0",
    8: "Q5_0",
    9: "Q5_1",
    10: "Q2_K",
    11: "Q3_K_S",
    12: "Q3_K_M",
    13: "Q3_K_L",
    14: "Q4_K_S",
    15: "Q4_K_M",
    16: "Q5_K_S",
    17: "Q5_K_M",
    18: "Q6_K",
}

# Short aliases for user convenience
_QUANT_ALIASES = {
    "Q3_K": "Q3_K_M",
    "Q4_K": "Q4_K_M",
    "Q5_K": "Q5_K_M",
}

DEFAULT_QUANT = "Q4_K_M"

OVERHEAD = 1.2

_UNIT_MULTIPLIER = {"M": 1e-3, "B": 1.0, "T": 1e3}

# Compiled regexes — one-time cost at import
_RE_PARAMS = re.compile(r"(\d+(?:\.\d+)?)\s*([MmBbTt])\b")
_RE_QUANT_NAME = re.compile(r"[QqFf]\d+(?:_\w+)?")
_RE_QUANT_ID = re.compile(r"^(\d{1,2})$")
_RE_PARAM_TRAILING = re.compile(
    r"(\d+(?:\.\d+)?)\s*([MmBbTt])\b\s*[-_]?\s*([QqFf]\d+(?:_\w+)?|\d{1,2})"
)


def model_memory_gb(params_billions: float, quant: str) -> tuple[float, float]:
    """Return (bare_gb, overhead_gb) for given param count and quantization."""
    bare = params_billions * QUANT_BYTES[quant]
    return bare, bare * OVERHEAD


# Precompute sorted lists — avoid repeated sorting at call time
_ALL_QUANTS = sorted(QUANT_BYTES, key=lambda q: QUANT_BYTES[q], reverse=True)

_PREFIX_QUANTS: dict[str, list[str]] = {}
for _q in QUANT_BYTES:
    for _end in range(1, len(_q)):
        _prefix = _q[:_end].upper()
        _PREFIX_QUANTS.setdefault(_prefix, []).append(_q)
for _v in _PREFIX_QUANTS.values():
    _v.sort()


def resolve_quant(name: str) -> list[str]:
    """Resolve a quantization name, numeric ID, or prefix to list of canonical names.

    Returns a list. Empty list means no match.
    - Exact:  "Q4_K_M" → ["Q4_K_M"]
    - Alias:  "Q4_K"   → ["Q4_K_M"]
    - Prefix: "Q4"     → ["Q4_0", "Q4_1", "Q4_K_S", "Q4_K_M"]
    - ID:     "15"     → ["Q4_K_M"]
    """
    # Numeric ID → single result
    if name.isdigit():
        q = _QUANT_BY_ID.get(int(name))
        return [q] if q else []
    # Alias → single result
    if name in _QUANT_ALIASES:
        return [_QUANT_ALIASES[name]]
    # Exact match → single result
    if name in QUANT_BYTES:
        return [name]
    # Precomputed prefix lookup
    return _PREFIX_QUANTS.get(name.upper(), [])


def resolve_all() -> list[str]:
    """Return all quantization names sorted by bytes-per-param descending."""
    return _ALL_QUANTS


def parse_input(tokens: list[str]) -> tuple[float | None, str | None, str]:
    """Fuzzy-parse tokens to extract (params_b, quantization, unit).

    Handles formats like:
        ["45B-Q4_K_M"]     → (45.0, "Q4_K_M", "B")
        ["45B-15"]         → (45.0, "Q4_K_M", "B")   (numeric type ID)
        ["7B", "Q4_0"]     → (7.0, "Q4_0", "B")
        ["qwen3.5", "0.8B"] → (0.8, None, "B")
        ["700M"]           → (0.7, None, "M")
        ["1T"]             → (1000.0, None, "T")
    """
    params_b: float | None = None
    unit: str = "B"
    quant: str | None = None

    for token in tokens:
        if m := _RE_PARAM_TRAILING.search(token):
            u = m.group(2).upper()
            params_b = float(m.group(1)) * _UNIT_MULTIPLIER[u]
            unit = u
            quant = m.group(3).upper()
        elif m := _RE_PARAMS.search(token):
            u = m.group(2).upper()
            params_b = float(m.group(1)) * _UNIT_MULTIPLIER[u]
            unit = u
        if quant is None:
            if m := _RE_QUANT_NAME.search(token):
                quant = m.group(0).upper()
            elif m := _RE_QUANT_ID.match(token):
                quant = m.group(1)

    return params_b, quant, unit
