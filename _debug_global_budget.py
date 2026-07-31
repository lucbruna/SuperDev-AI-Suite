import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from SuperDev.code.understanding.prompt_builder import (
    PromptBuilder,
    _block_overhead,
    _truncate_to_budget as _t,
)
from SuperDev.code.understanding.context_builder import estimate_tokens

big = "\n".join(f"def fn_{i}(arg): return {i}" for i in range(200))

b = PromptBuilder(max_tokens=30)
# replicate the build loop manually
files = [("a.py", big), ("b.py", big)]


def assemble(remaining_files):
    parts = ["T"]
    for path, content in remaining_files:
        parts.append(f"### FILE: {path}\n```\n{content}\n```")
    return "\n\n".join(parts)


print("estimate_tokens('T') =", estimate_tokens("T"))
print("overhead a.py =", _block_overhead("a.py"))
print("overhead b.py =", _block_overhead("b.py"))
print("tokens(assemble([a,b])) =", estimate_tokens(assemble(files)))

# iteration 1: path = b.py
path, content = files[-1]
remaining = 30 - estimate_tokens(assemble(files[:-1]))
print("iter1 path:", path, "remaining:", remaining, "> overhead?", remaining > _block_overhead(path))

# pop b.py
files.pop()

# iteration 2: path = a.py
path, content = files[-1]
remaining = 30 - estimate_tokens(assemble(files[:-1]))
print("iter2 path:", path, "remaining:", remaining, "> overhead?", remaining > _block_overhead(path))
target = max(1, r