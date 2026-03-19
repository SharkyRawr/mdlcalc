import click

from mdlcalc.calc import (
    DEFAULT_QUANT,
    OVERHEAD,
    QUANT_BYTES,
    model_memory_gb,
    parse_input,
    resolve_all,
    resolve_quant,
)


def _fmt(n: float) -> str:
    """Human-friendly number formatting."""
    if n >= 100:
        return f"{n:.0f}"
    return f"{n:.1f}"


def _fmt_params(params_b: float, unit: str) -> str:
    """Format parameter count back in the user's preferred unit."""
    if unit == "T":
        return f"{params_b / 1e3:.1f}T"
    if unit == "M":
        return f"{params_b * 1e3:.0f}M"
    return f"{_fmt(params_b)}B"


def _print_table(params_b: float, unit: str, quants: list[str]) -> None:
    """Print a table of memory estimates for multiple quantization levels."""
    # Find longest quant name for alignment
    width = max(len(q) for q in quants)
    for q in quants:
        bare, overhead = model_memory_gb(params_b, q)
        click.echo(
            f"  {q:>{width}s}: {_fmt(bare):>8s} GB  ({_fmt(overhead):>7s} GB w/ overhead)"
        )


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("inputs", nargs=-1, required=True)
@click.option("-v", "--verbose", is_flag=True, help="Show all quantization levels.")
def cli(inputs: tuple[str, ...], verbose: bool):
    """Calculate approximate memory to run LLM inference.

    \b
    Examples:
      mdlcalc 45B-Q4_K_M
      mdlcalc 7B Q4              (shows all Q4 variants)
      mdlcalc 7B 15              (numeric type ID)
      mdlcalc 7B -v              (show all quant levels)
      mdlcalc 700M
      mdlcalc 1T
    """
    params_b, quant_raw, unit = parse_input(list(inputs))

    if params_b is None:
        raise click.UsageError(
            "Could not find parameter count. Use formats like: 7B, 0.8B, 45B, 700M, 1T"
        )

    label = _fmt_params(params_b, unit)

    if verbose:
        quants = resolve_all()
        click.echo(f"{label} - all quantization levels:")
        _print_table(params_b, unit, quants)
        return

    if quant_raw:
        quants = resolve_quant(quant_raw)
        if not quants:
            valid = ", ".join(sorted(QUANT_BYTES.keys()))
            raise click.BadParameter(
                f"Unknown quantization '{quant_raw}'. "
                f"Valid types: {valid}\n"
                f"Or use numeric IDs 0-18."
            )
    else:
        quants = [DEFAULT_QUANT]

    if len(quants) == 1:
        bare, overhead = model_memory_gb(params_b, quants[0])
        click.echo(
            f"{label} @ {quants[0]}: "
            f"{_fmt(bare)} GB ({_fmt(overhead)} GB with {OVERHEAD}x overhead)"
        )
    else:
        click.echo(f"{label} @ {quant_raw}:")
        _print_table(params_b, unit, quants)
