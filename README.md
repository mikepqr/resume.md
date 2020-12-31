# resume.md

![Resume](resume.png)


Write your resume in
[Markdown](https://raw.githubusercontent.com/mikepqr/resume.md/main/resume.md),
style it with [CSS](resume.css), output to [HTML](resume.html) and
[PDF](resume.pdf).


## Instructions

 1. Clone this repository

 2. Install the dependencies:
    <pre>
    pip install <a href="https://python-markdown.github.io/">markdown</a> <a href="https://weasyprint.org/">weasyprint</a>
    </pre>

 3. Edit [resume.md](resume.md) (the placeholder text is taken with thanks from the 
    [JSON Resume Project](https://jsonresume.org/themes/))

 4. Run `make resume` to build resume.html and resume.pdf.

## Customization

Edit [resume.css](resume.css) to change the appearance of your resume. The
default style is extremely generic, which is perhaps what you want in a resume,
but CSS gives you a lot of flexibility. See, e.g. [The Tech Resume
Inside-Out](https://www.thetechinterview.com/) for good advice about what a
resume should look like (and what it should say).

Because the source is plain markdown and python-markdown is a very bare bones
markdown compiler, elements cannot be tagged with ids or classes in the markdown
source. If you need more control over the HTML, take a look at
[kramdown](https://kramdown.gettalong.org/syntax.html). I chose not to use it
for this project to avoid a non-python dependency.

Change the appearance of the PDF version (without affecting the HTML version) by
adding rules under the `@media print` CSS selector. 

Change the margins and paper size of the PDF version by editing the [`@page` CSS
rule](https://developer.mozilla.org/en-US/docs/Web/CSS/%40page/size).

If you make a resume.css that you like, please submit a pull request. I'd be
happy to collect these.

## Tips

Run `make watch` while you are working on your resume to rebuild it whenever
resume.md or resume.css change (requires
[entr](http://eradman.com/entrproject/)).

The simplest way to maintain multiple versions of your resume is to comment bits
of text in or out based on the audience. This can be done with standard HTML
comment syntax (e.g. `<!-- Skills: Microsoft Word -->`) but beware that
commented out text will be included in the HTML source that you are presumably
going to put online or share.

An alternative is to keep snippets of Markdown (or CSS) in separate files, and
collect them into a single file for each version of your resume using a
templating tool, makefile or shell script.

Use, e.g. `git tag` to record which version of the resume you sent to which
person.

Use `git diff --word-diff` to make `git diff` more legible (this applies any
time you run git diff on natural language).

## Windows users

Windows cannot use "make" by default, so you cannot take advantage of the makefile or the cool "make watch" command above. However, a basic python script is provided to allow you to produce your resume from the commandline.

- NOTE: If you want to print to pdf, you will need to follow the special windows instructions for installing weasyprint as noted here: https://weasyprint.readthedocs.io/en/latest/install.html#windows. A few notes:
   - You should be installing markdown and weasyprint to a virtual environment, but the extra weasyprint dependencies will be installed on a global basis.
   - If you opt not to bother installing the weasyprint dependencies, the script will still run and provide you with a html version of your beautiful resume. You can then print that using the "Microsoft print to pdf" option available in most browsers.

### Instructions:
1. Follow steps 1-3 under "Instructions" above.
2. If you are using a virtual environment, make sure to activate it, then run the following from the command line:
   <pre>
   python make_resume.py path_to_my_resume.md
   </pre>