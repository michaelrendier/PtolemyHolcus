"""
Strip the context primers + TODOs down to PROSE, for ingestion into a Monad
.bin. The maths/code are already in the code — remove fenced blocks, tables,
box-drawing, notation-dense lines, frontmatter, list/quote markers, links.
Keep: sentences of English describing the engineering, the conversation, the
war-corpus discussion.

Usage:  python3 corpus_strip.py [--war-only | --no-war]  > corpus.txt
"""
import os, re, sys, glob

HP = "/home/rendier/Projects/ThePlace/ContextPlease/claude/hist_prime"
HT = "/home/rendier/Projects/ThePlace/ContextPlease/claude/hist_todo"

# lines that are structure, not prose
_RULE      = re.compile(r'^[\s]*[=\-_*~#>|+.·•▪◦●○—–─-╿═-╬]{2,}[\s]*$')
_BOXCHARS  = re.compile(r'[─-╿═-╬]')
_FRONT     = re.compile(r'^---\s*$')
_FENCE     = re.compile(r'^\s*(```|~~~)')
_TABLEROW  = re.compile(r'^\s*\|.*\|\s*$')
_MDHEAD    = re.compile(r'^\s{0,3}#{1,6}\s+')
_LISTMARK  = re.compile(r'^\s*([-*+]|\d+[.)]|[a-zA-Z][.)])\s+')
_QUOTE     = re.compile(r'^\s*>\s?')
_MDLINK    = re.compile(r'\[([^\]]+)\]\([^)]+\)')
_INLINE    = re.compile(r'`([^`]*)`')
_EMPH      = re.compile(r'(\*\*|\*|__|_)(.*?)\1')
_HTMLTAG   = re.compile(r'<[^>]+>')
_URL       = re.compile(r'https?://\S+|\b[\w./-]+\.(?:py|md|txt|c|h|json|ipynb|sh)\b')
_KEYVAL    = re.compile(r'^\s*[A-Za-z_][\w .\-]{0,40}:\s')
# a line is "notation" if too many of its non-space chars are symbols/greek/math
_MATHSYM   = re.compile(r'[=+\-*/^_{}\\|<>~≈≠≤≥→←↦⊗⊕∘∑∏∫∂∇√∅ΓΣΠΩλσμπφθτξζψΔ½¼·×÷±∞∈∉⊂⊆⟨⟩⌊⌋]')
_ALNUM     = re.compile(r'[A-Za-z]')

def is_notation(line: str) -> bool:
    s = line.strip()
    if len(s) < 3:
        return True
    letters = len(_ALNUM.findall(s))
    symbols = len(_MATHSYM.findall(s))
    if letters == 0:
        return True
    return symbols > 0 and symbols / max(letters, 1) > 0.35

def strip_file(path: str) -> str:
    try:
        raw = open(path, encoding="utf-8", errors="replace").read()
    except Exception:
        return ""
    lines = raw.splitlines()
    out, in_fence, in_front = [], False, False
    # YAML frontmatter only if the very first non-blank line is ---
    i0 = next((i for i, l in enumerate(lines) if l.strip()), 0)
    if i0 < len(lines) and _FRONT.match(lines[i0]):
        in_front = True
        lines = lines[i0 + 1:]
    for ln in lines:
        if in_front:
            if _FRONT.match(ln):
                in_front = False
            continue
        if _FENCE.match(ln):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if _TABLEROW.match(ln):
            # keep the cell text, drop the pipes/dashes
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            cells = [c for c in cells if c and not set(c) <= set("-: ")]
            if cells:
                out.append(" . ".join(cells))
            continue
        if _RULE.match(ln):
            continue
        ln = _BOXCHARS.sub("", ln)
        ln = _MDHEAD.sub("", ln)
        ln = _QUOTE.sub("", ln)
        ln = _LISTMARK.sub("", ln)
        ln = _MDLINK.sub(r"\1", ln)
        ln = _INLINE.sub(r"\1", ln)
        ln = _EMPH.sub(r"\2", ln)
        ln = _HTMLTAG.sub(" ", ln)
        ln = _URL.sub(" ", ln)
        if _KEYVAL.match(ln):
            ln = ln.split(":", 1)[1]
        if not ln.strip():
            continue
        if is_notation(ln):
            continue
        out.append(ln.strip())
    text = "\n".join(out)
    # collapse whitespace, keep sentence boundaries
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text

def gather(want_war):
    files = []
    for root in (HP, HT):
        for ext in ("*.txt", "*.md", "*"):
            for p in glob.glob(os.path.join(root, "**", ext), recursive=True):
                if os.path.isfile(p) and not p.endswith((".json",)):
                    files.append(p)
    files = sorted(set(files))
    WAR = re.compile(r"war|caesar|gallic|de bello|julius|legion|campaign", re.I)
    picked, wc_total = [], 0
    for p in files:
        blob = strip_file(p)
        if not blob.strip():
            continue
        is_war = bool(WAR.search(os.path.basename(p))) or \
                 (len(WAR.findall(blob)) >= 3)
        if want_war is True and not is_war:
            continue
        if want_war is False and is_war:
            continue
        picked.append((p, blob, is_war))
        wc_total += len(blob.split())
    return picked, wc_total

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    want_war = True if mode == "--war-only" else (False if mode == "--no-war" else None)
    picked, wc = gather(want_war)
    for p, blob, is_war in picked:
        rel = os.path.relpath(p, "/home/rendier/Projects/ThePlace/ContextPlease/claude")
        sys.stderr.write(f"  {'[WAR] ' if is_war else '      '}{rel}  ({len(blob.split())} words)\n")
        print(blob)
    sys.stderr.write(f"\n  {len(picked)} files, {wc} prose words total"
                     f"{' (war subset)' if want_war else ''}\n")

if __name__ == "__main__":
    main()
