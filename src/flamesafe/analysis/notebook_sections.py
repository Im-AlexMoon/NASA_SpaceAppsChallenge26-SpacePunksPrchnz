"""Replace a bounded generated notebook section while preserving trailing cells."""


def replace_section(cells, section, added, *, legacy_end_token=None):
    """Return new cells; never truncate an unbounded or ambiguous existing section.

    Existing segmentation appendices predate END markers, so the caller can supply
    the unique final-cell token of that known legacy section. Unknown layouts fail
    closed instead of discarding later user content.
    """
    begin = f"<!-- FLAMESAFE:{section}:BEGIN -->"
    end = f"<!-- FLAMESAFE:{section}:END -->"
    starts = [i for i, c in enumerate(cells) if begin in c["source"]]
    if len(starts) > 1:
        raise ValueError(f"Multiple starts for {section}")
    if not starts:
        return [*cells, *added]
    start = starts[0]
    ends = [i for i in range(start, len(cells)) if end in cells[i]["source"]]
    if not ends and legacy_end_token:
        ends = [i for i in range(start, len(cells)) if legacy_end_token in cells[i]["source"]]
    if len(ends) != 1:
        raise ValueError(f"Cannot determine a unique safe end for {section}")
    stop = ends[0] + 1
    return [*cells[:start], *added, *cells[stop:]]
