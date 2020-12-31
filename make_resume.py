from weasyprint import HTML, CSS
from markdown import markdown
from sys import argv

def create_pdf_from_html(path_to_html_resume: str) -> None:
    path_to_pdf: str = path_to_html_resume.split(".")[-2] + ".pdf"
    try:
        html = HTML(path_to_html_resume)
        css = CSS("resume.css")
        html.write_pdf(path_to_pdf,stylesheets=[css])
    except Exception as e:
        print(e)
        print("weasyprint failed, probably missing some plugins. You can use your web browser to view and print the new .html file")

def get_text_from_resume_in_html(path_to_resume: str) -> str:
    with open(path_to_resume, "r", encoding='utf8', errors='ignore') as f:
        text_from_resume = f.read()
    text_from_resume_in_html = markdown(text_from_resume, extensions = ['smarty'])
    return text_from_resume_in_html

def get_text_from_file(filename: str) -> str:
    with open(filename, "r", encoding='utf8', errors='ignore') as f:
        text_from_file = f.read()
    return text_from_file

def write_text_to_file(text: str, filename: str) -> None:
    with open(filename, "w", encoding='utf8', errors='ignore') as f:
        f.write(text)
    return

def create_html_from_resume(path_to_resume: str) -> str:
    text_from_resume_in_html: str = get_text_from_resume_in_html(path_to_resume)
    text_preamble: str = get_text_from_file("preamble.html")
    text_posteamble: str = get_text_from_file("postamble.html")
    text_total: str = text_preamble + "\n" + text_from_resume_in_html + "\n" + text_posteamble
    path_to_html: str = path_to_resume.split(".")[-2] + ".html"
    write_text_to_file(text_total,path_to_html)
    return path_to_html

def main(path_to_resume: str) -> None:
    path_to_html_resume: str = create_html_from_resume(path_to_resume)
    create_pdf_from_html(path_to_html_resume)
    
if __name__ == "__main__":
    number_of_args: int = len(argv)
    if number_of_args < 2:
        print("No filename provided, defaulting to 'resume.md'")
        path_to_resume = "resume.md"
    else:
        path_to_resume = argv[1]
        print(f"Creating a resume from '{path_to_resume}'")
    main(path_to_resume)

    
