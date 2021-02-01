from typing import List

import markdown

preamble = """
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<link rel="stylesheet" type="text/css" href="resume.css">
</head>
<body>
<div id="resume">
"""

postamble = """
</div>
</body>
</html>
"""


def title(mdlines: List[str]) -> str:
    """
    Return the contents of the first markdown heading in mdlines, which we
    assume to be the title of the document.
    """
    for line in mdlines:
        if line[0] == "#":
            return line.strip("#").strip()
    raise ValueError("Cannot find any lines that look like markdown headings")


def make_html(mdlines: List[str]) -> str:
    """
    Compile mdlines to HTML and prepend/append preamble/postamble.
    """
    return "".join(
        (
            preamble.format(title=title(mdlines)),
            markdown.markdown("".join(mdlines), extensions=["smarty"]),
            postamble,
        )
    )


if __name__ == "__main__":
    with open("resume.md") as mdfp:
        mdlines = mdfp.readlines()
    with open("resume.html", "w") as htmlfp:
        htmlfp.write(make_html(mdlines))
