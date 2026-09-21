#!/usr/bin/env python3
"""Build appendix.pdf (the download on the project page) from the Overleaf source.

    python3 tools/build_appendix_pdf.py

Needs:  brew install tectonic mupdf-tools
Reads:  paper_overleaf/   (git-ignored: it holds the de-anonymised source -- never commit it)
Writes: appendix.pdf      (anonymous; safe to publish) -- and refreshes the "N pages . X MB" note
        between the <!--pdf-info--> markers in index.html

What it does, all inside a throw-away copy (paper_overleaf/ itself is never modified):
  1. normalises the figure PDFs          (Tectonic's PDF backend rejects some Keynote/macOS exports
                                          that Overleaf's pdfTeX accepts)
  2. applies the small text fixes below  (each is skipped once the source no longer needs it)
  3. runs the full paper once, only to learn where the main paper's numbering stops and to get
     the numbers of the main-paper tables/sections the appendix refers to
  4. compiles tools/appendix_only.tex: title + "Appendix", Anonymous Authors, appendices in the
     order main.tex lists them, numbering continued from the paper, its own reference list
  5. refuses to publish if the PDF contains "??", dropped characters, or any author /
     affiliation name from main.tex
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "paper_overleaf"
TEMPLATE = ROOT / "tools" / "appendix_only.tex"
OUT = ROOT / "appendix.pdf"

MAIN_PAPER = " of the main paper"
# (file, text in the Overleaf source, replacement). Typos are better fixed on Overleaf -- after that
# the entry simply no longer matches. The last two make references into the main paper readable
# in a stand-alone document ("Table II of the main paper"); "M-" labels are the main paper's.
FIXES = [
    ("appendices/F_Experiments.tex", r"\subsection{Keyfrema Refinement}", r"\subsection{Keyframe Refinement}"),
    ("appendices/F_Experiments.tex", r"in Tables.~\ref", r"in Tables~\ref"),
    ("appendices/A_module_details.tex", "yields the corrected handr pose", "yields the corrected hand pose"),
    ("appendices/A_module_details.tex", "Collsion-aware", "Collision-aware"),
    ("appendices/A_module_details.tex", "determines that no collision-free path. ", "determines that no collision-free path exists. "),
    ("appendices/A_module_details.tex", "\\texttt{interactive manipulation}; or  \\texttt{pushing}\n", "\\texttt{interactive manipulation} or \\texttt{pushing};\n"),
    ("appendices/B_geometry_physics_gap.tex", r"p(a \mid o,s)", r"p(a \mid o,g)"),
    ("appendices/D_refinement_baselines.tex", r"v). \textit{Object-only}", r"v) \textit{Object-only}"),
    ("appendices/H_Sim2Real.tex", "we compare it with two commonly used", "We compare it with three commonly used"),
    ("tables/safety_table_corrected.tex", "across seeds for baselines;", "across seeds for baselines."),
    ("references.bib", "author={Team, Gemini}", "author={{Gemini Team}}"),      # otherwise printed as "G. Team"
    ("appendices/H_Sim2Real.tex", r"Sec.~\ref{sec:sim2real}", r"Sec.~\ref*{M-sec:sim2real_eval}" + MAIN_PAPER),
    ("appendices/H_Sim2Real.tex", r"Table~\ref{tab:real_world_task_success}", r"Table~\ref*{M-tab:real_world_task_success}" + MAIN_PAPER),
]


def run(cmd, cwd, what):
    proc = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if proc.returncode != 0:
        lines = [l for l in proc.stdout.splitlines() if not l.startswith("note: downloading")]
        sys.exit(f"\n{what} failed:\n  " + "\n  ".join(lines[-25:]) + f"\n\n(build directory kept: {cwd})")
    return proc.stdout


def uncommented(text):
    return "\n".join(re.sub(r"(?<!\\)%.*", "", line) for line in text.splitlines())


def roman(n):
    out = ""
    for value, numeral in [(10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]:
        while n >= value:
            out, n = out + numeral, n - value
    return out


def main():
    for tool in ("tectonic", "mutool"):
        if not shutil.which(tool):
            sys.exit(f"'{tool}' not found -- install with:  brew install tectonic mupdf-tools")
    if not (SRC / "main.tex").is_file():
        sys.exit(f"{SRC}/main.tex not found -- download the Overleaf project into paper_overleaf/ first")

    build = Path(tempfile.mkdtemp(prefix="appendix_build_"))
    shutil.copytree(SRC, build, dirs_exist_ok=True, ignore=shutil.ignore_patterns("Rebuttal", ".DS_Store", "*.zip"))

    # 1. figure PDFs -> plain, uncompressed-xref PDFs
    for pdf in sorted((build / "images").glob("*.pdf")):
        run(["mutool", "clean", "-g", pdf.name, pdf.name + ".tmp"], pdf.parent, f"mutool clean {pdf.name}")
        (pdf.parent / (pdf.name + ".tmp")).replace(pdf)

    # 2. text fixes
    print("Text fixes (edit the FIXES list in this script; fix typos on Overleaf to retire them):")
    for rel, old, new in FIXES:
        path = build / rel
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        n = text.count(old)
        if n:
            path.write_text(text.replace(old, new), encoding="utf-8")
        shown = " ".join(old.split())
        print(f"  [{'applied x' + str(n) if n else 'not needed'}]  {rel}: {shown[:60]}")

    # 3. full paper -> main.aux (labels + the counters where the appendix starts)
    main_tex = (build / "main.tex").read_text(encoding="utf-8")
    inputs = re.findall(r"^[ \t]*(\\input\{appendices/[^}]+\})", uncommented(main_tex), flags=re.M)
    if not inputs:
        sys.exit(r"main.tex has no uncommented \input{appendices/...} lines")
    probe = (r"\makeatletter\immediate\write\@auxout{\string\gdef\string\MAINPAPERCOUNTERS"
             r"{\arabic{figure},\arabic{table},\arabic{equation}}}\makeatother" + "\n")
    (build / "main.tex").write_text(main_tex.replace(inputs[0], probe + inputs[0], 1), encoding="utf-8")
    print("Compiling the full paper once (numbering only) ...")
    (build / "out_main").mkdir()
    run(["tectonic", "-X", "compile", "main.tex", "--outfmt", "aux", "--outdir", "out_main"], build, "compiling main.tex")
    aux = (build / "out_main" / "main.aux").read_text(encoding="utf-8", errors="replace")
    (build / "main.aux").write_text(aux, encoding="utf-8")
    counters = re.search(r"\\gdef\s*\\MAINPAPERCOUNTERS\s*\{(\d+),(\d+),(\d+)\}", aux)
    if not counters:
        sys.exit(f"could not read the main paper's counters from main.aux (build directory kept: {build})")
    figures, tables, equations = map(int, counters.groups())
    print(f"  main paper ends at Fig. {figures}, Table {roman(tables)}, Eq. ({equations})"
          f"  ->  appendix starts at Fig. {figures + 1}, Table {roman(tables + 1)}, Eq. ({equations + 1})")

    # 4. the appendix on its own
    tex = TEMPLATE.read_text(encoding="utf-8")
    for key, value in {"@@FIGURES@@": figures, "@@TABLES@@": tables, "@@TABLES_ROMAN@@": roman(tables),
                       "@@EQUATIONS@@": equations, "@@APPENDIX_INPUTS@@": "\n".join(inputs)}.items():
        tex = tex.replace(key, str(value))
    (build / "appendix.tex").write_text(tex, encoding="utf-8")
    print("Compiling the appendix:", ", ".join(i[len("\\input{appendices/"):-1] for i in inputs), "...")
    (build / "out").mkdir()
    log = run(["tectonic", "-X", "compile", "appendix.tex", "--keep-logs", "--outdir", "out"], build, "compiling the appendix")
    pdf = build / "out" / "appendix.pdf"

    # 5. safety net before anything is published
    text = subprocess.run(["mutool", "draw", "-q", "-F", "txt", str(pdf)], stdout=subprocess.PIPE, text=True).stdout
    info = subprocess.run(["mutool", "show", str(pdf), "trailer/Info"], stdout=subprocess.PIPE, text=True).stdout
    problems = []
    if "??" in text:
        problems.append('unresolved reference ("??") on: ' + "; ".join(l.strip()[:70] for l in text.splitlines() if "??" in l)[:300])
    tex_log = (build / "out" / "appendix.log").read_text(encoding="utf-8", errors="replace")
    undefined = sorted(set(re.findall(r"(?:Reference|Citation) `([^']+)' .*undefined", log + tex_log)))
    if undefined:
        problems.append("undefined references/citations: " + ", ".join(undefined))
    dropped = sorted(set(re.findall(r"Missing character: There is no (\S+)", tex_log)))
    if dropped:                                         # a Unicode character the fonts cannot print (see appendix_only.tex)
        problems.append("characters silently dropped from the text: " + " ".join(dropped)
                        + r"  -> add a \newunicodechar line for each in tools/appendix_only.tex")
    author_block = re.search(r"\\else\s*\\author\{(.*?)\\fi", main_tex, flags=re.S)
    if author_block:                                    # names and affiliations of the de-anonymised \author block
        block = re.sub(r"\$[^$]*\$", " ", author_block.group(1))
        people = re.sub(r"\\thanks\{.*", "", block, flags=re.S)
        names = [" ".join(n.split()) for n in re.split(r",|\\\\", re.sub(r"[%{}]", " ", people))]
        names += [" ".join(a.split()) for a in re.findall(r"\\thanks\{\s*([A-Z][A-Za-z ]+(?:University|Institute)[A-Za-z ]*)\}", block)]
        haystack = " ".join((text + " " + info).split()).lower()
        leaked = [n for n in names if len(n) > 5 and n.lower() in haystack]
        if leaked:
            problems.append("AUTHOR / AFFILIATION NAMES IN THE PDF: " + ", ".join(leaked))
    if problems:
        sys.exit("\nNot publishing -- the PDF has problems:\n  - " + "\n  - ".join(problems) + f"\n(build directory kept: {build})")

    shutil.copyfile(pdf, OUT)
    pages = re.search(r"Pages:\s*(\d+)", subprocess.run(["mutool", "info", str(OUT)], stdout=subprocess.PIPE, text=True).stdout)
    pages, size = (pages.group(1) if pages else "?"), f"{OUT.stat().st_size / 1e6:.1f} MB"
    print(f"\nWrote {OUT.relative_to(ROOT)}: {pages} pages, {size}"
          "  (no '??', no dropped characters, no author names, metadata author = Anonymous Authors)")

    # keep the "N pages . X MB" note next to the download buttons on the page in step
    index = ROOT / "index.html"
    html = index.read_text(encoding="utf-8")
    note = re.compile(r"(<!--pdf-info-->).*?(<!--/pdf-info-->)", flags=re.S)
    if note.search(html):
        updated = note.sub(lambda m: f"{m.group(1)}{pages} pages &middot; {size}{m.group(2)}", html)
        if updated != html:
            index.write_text(updated, encoding="utf-8")
            print(f"Updated the note in index.html -> {pages} pages, {size}")
    else:
        print("(index.html has no <!--pdf-info--> marker; page count / size note not updated)")
    shutil.rmtree(build, ignore_errors=True)


if __name__ == "__main__":
    main()
