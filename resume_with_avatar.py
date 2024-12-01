#!/usr/bin/env python3
import argparse
import base64
import itertools
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import markdown
import re

# you could replace "avatar.png" with your own avatar image
# or set avatar_path to your own image path
avatar_path = "avatar.png"

preamble = """\
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
{css}
</style>
</head>
<body>
<div id="resume">
    <div id="resume-header">
        <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 20px;">
            <h1 style="margin: 0; margin-left: -40px;">{title}</h1>
        </div>

        <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 20px;">
            <!-- the first long group -->
            <div style="flex-basis: 40%; text-align: left;">
                <ul style="list-style: none; padding: 0;">
                    {first_column}
                </ul>
            </div>


            <!-- the second short group -->
            <div style="flex-basis: 26%; text-align: left;">
                <ul style="list-style: none; padding: 0;">
                    {second_column}
                </ul>
            </div>

            <!-- the avatar -->
            <div style="flex-basis: 33%; text-align: right; align-self: flex-start;">
                {img}
            </div>
        </div>
    </div>
"""

postamble = """\
</div>
</body>
</html>
"""

CHROME_GUESSES_MACOS = (
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
)

# https://stackoverflow.com/a/40674915/409879
CHROME_GUESSES_WINDOWS = (
    # Windows 10
    os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
    os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
    os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
    # Windows 7
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    # Vista
    r"C:\Users\UserName\AppDataLocal\Google\Chrome",
    # XP
    r"C:\Documents and Settings\UserName\Local Settings\Application Data\Google\Chrome",
)

# https://unix.stackexchange.com/a/439956/20079
CHROME_GUESSES_LINUX = [
    "/".join((path, executable))
    for path, executable in itertools.product(
        (
            "/usr/local/sbin",
            "/usr/local/bin",
            "/usr/sbin",
            "/usr/bin",
            "/sbin",
            "/bin",
            "/opt/google/chrome",
        ),
        ("google-chrome", "chrome", "chromium", "chromium-browser"),
    )
]


def get_avatar_base64(image_path: str) -> str:
    """
    Read the avatar image and return it as a base64 string.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def guess_chrome_path() -> str:
    if sys.platform == "darwin":
        guesses = CHROME_GUESSES_MACOS
    elif sys.platform == "win32":
        guesses = CHROME_GUESSES_WINDOWS
    else:
        guesses = CHROME_GUESSES_LINUX
    for guess in guesses:
        if os.path.exists(guess):
            logging.info("Found Chrome or Chromium at " + guess)
            return guess
    raise ValueError("Could not find Chrome. Please set CHROME_PATH.")


def title(md: str) -> str:
    """
    Return the contents of the first markdown heading in md, which we
    assume to be the title of the document.
    """
    for line in md.splitlines():
        if re.match("^#[^#]", line):  # starts with exactly one '#'
            return line.lstrip("#").strip()
    raise ValueError(
        "Cannot find any lines that look like markdown h1 headings to use as the title"
    )


def extract_header(md: str) -> str:
    items = []
    for line in md.splitlines():
        if line.startswith("## "):  # Stop processing at the first "## "
            break
        if line.startswith("- "):  # Collect lines starting with "- "
            items.append(line)
    return "\n".join(items)


def split_by_length(header: str) -> str:
    """
    Split the header lines into two groups based on line lengths (excluding parentheses and their content).
    If the number of lines is odd, the longer group has one extra line.

    Args:
        header (str): The multiline string from extract_header.

    Returns:
        str: Two groups formatted as a single string.
    """

    # Helper function to calculate line length excluding parentheses content
    def line_length(line: str) -> int:
        clean_line = re.sub(r"\(.*?\)", "", line)  # Remove parentheses and their content
        return len(clean_line.strip())

    # Split the input header into lines
    lines = header.splitlines()

    # Sort lines by their effective length in descending order
    sorted_lines = sorted(lines, key=line_length, reverse=True)

    # Determine the split point
    split_index = (len(sorted_lines) + 1) // 2  # Longer group gets the extra line if odd

    # Divide into two groups
    longer_group = "\n".join(sorted_lines[:split_index])
    shorter_group = "\n".join(sorted_lines[split_index:])

    # Combine groups into the final output
    return longer_group, shorter_group


# find the first line that starts with "## ", and return it and all rest lines of the text
def extract_main_section(md: str) -> str:
    for i, line in enumerate(md.splitlines()):
        if line.startswith("## "):
            return "\n".join(md.splitlines()[i:])


def make_html(md: str, prefix: str = "resume", avatar_path: str = avatar_path) -> str:
    """
    Compile md to HTML and prepend/append preamble/postamble.

    Insert <prefix>.css if it exists.
    """
    try:
        with open(prefix + ".css") as cssfp:
            css = cssfp.read()
    except FileNotFoundError:
        print(prefix + ".css not found. Output will by unstyled.")
        css = ""

    avatar_base64 = get_avatar_base64(avatar_path)
    avatar_html = f'<img src="data:image/png;base64,{avatar_base64}" alt="Avatar">'
    longer_group, shorter_group = split_by_length(extract_header(md))
    first_column = markdown.markdown(longer_group, extensions=["smarty", "abbr"])[4:-5]
    second_column = markdown.markdown(shorter_group, extensions=["smarty", "abbr"])[4:-5]

    return "".join(
        (
            preamble.format(title=title(md), css=css, img=avatar_html, first_column=first_column,
                            second_column=second_column),
            markdown.markdown(extract_main_section(md), extensions=["smarty", "abbr"]),
            postamble,
        )
    )


def write_pdf(html: str, prefix: str = "resume", chrome: str = "") -> None:
    """
    Write html to prefix.pdf
    """
    chrome = chrome or guess_chrome_path()
    html64 = base64.b64encode(html.encode("utf-8"))
    options = [
        "--no-sandbox",
        "--headless",
        "--print-to-pdf-no-header",
        # Keep both versions of this option for backwards compatibility
        # https://developer.chrome.com/docs/chromium/new-headless.
        "--no-pdf-header-footer",
        "--enable-logging=stderr",
        "--log-level=2",
        "--in-process-gpu",
        "--disable-gpu",
    ]

    # Ideally we'd use tempfile.TemporaryDirectory here. We can't because
    # attempts to delete the tmpdir fail on Windows because Chrome creates a
    # file the python process does not have permission to delete. See
    # https://github.com/puppeteer/puppeteer/issues/2778,
    # https://github.com/puppeteer/puppeteer/issues/298, and
    # https://bugs.python.org/issue26660. If we ever drop Python 3.9 support we
    # can use TemporaryDirectory with ignore_cleanup_errors=True as a context
    # manager.
    tmpdir = tempfile.mkdtemp(prefix="resume.md_")
    options.append(f"--crash-dumps-dir={tmpdir}")
    options.append(f"--user-data-dir={tmpdir}")

    try:
        subprocess.run(
            [
                chrome,
                *options,
                f"--print-to-pdf={prefix}.pdf",
                "data:text/html;base64," + html64.decode("utf-8"),
            ],
            check=True,
        )
        logging.info(f"Wrote {prefix}.pdf")
    except subprocess.CalledProcessError as exc:
        if exc.returncode == -6:
            logging.warning(
                "Chrome died with <Signals.SIGABRT: 6> "
                f"but you may find {prefix}.pdf was created successfully."
            )
        else:
            raise exc
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
        if os.path.isdir(tmpdir):
            logging.debug(f"Could not delete {tmpdir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file",
        help="markdown input file [resume.md]",
        default="resume.md",
        nargs="?",
    )
    parser.add_argument(
        "--no-html",
        help="Do not write html output",
        action="store_true",
    )
    parser.add_argument(
        "--no-pdf",
        help="Do not write pdf output",
        action="store_true",
    )
    parser.add_argument(
        "--chrome-path",
        help="Path to Chrome or Chromium executable",
    )
    parser.add_argument(
        "--avatar",
        help="Path to avatar image",
        default="avatar.png",
    )
    parser.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    if args.quiet:
        logging.basicConfig(level=logging.WARN, format="%(message)s")
    elif args.debug:
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    else:
        logging.basicConfig(level=logging.INFO, format="%(message)s")

    prefix, _ = os.path.splitext(os.path.abspath(args.file))

    with open(args.file, encoding="utf-8") as mdfp:
        md = mdfp.read()
    html = make_html(md, prefix=prefix)

    if not args.no_html:
        with open(prefix + ".html", "w", encoding="utf-8") as htmlfp:
            htmlfp.write(html)
            logging.info(f"Wrote {htmlfp.name}")

    if not args.no_pdf:
        write_pdf(html, prefix=prefix, chrome=args.chrome_path)
