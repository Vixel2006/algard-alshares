import difflib


def generate_diff(original: str, patched: str, context: int = 3) -> str:
    original_lines = original.splitlines(keepends=True)
    patched_lines = patched.splitlines(keepends=True)

    diff = difflib.unified_diff(
        original_lines,
        patched_lines,
        fromfile="original",
        tofile="patched",
        lineterm="",
        n=context,
    )

    return "".join(diff)
