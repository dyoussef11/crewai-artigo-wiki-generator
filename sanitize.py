# sanitize.py
import re
import sys

t = sys.argv[1] if len(sys.argv) > 1 else ""
c = re.sub(r"[^\w\s-]", "", t).strip()
c = re.sub(r"\s+", "_", c)
print(c[:50] if c else "artigo")