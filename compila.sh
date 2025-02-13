#!/bin/sh
# Compila o documento LaTeX e gera as referências bibliográficas

pdflatex pre-projeto.tex
bibtex pre-projeto
pdflatex pre-projeto.tex
pdflatex pre-projeto.tex
latexmk -c
open pre-projeto.pdf