.PHONY: resume watch clean

resume: resume.pdf resume.html

watch:
	ls *.md *.css | entr make resume

resume.html: resume.md resume.py
	python resume.py

resume.pdf: resume.html resume.css
	weasyprint resume.html resume.pdf

clean:
	rm -f resume.html resume.pdf
