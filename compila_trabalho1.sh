#!/bin/sh
# Compila o documento LaTeX e gera as referências bibliográficas

pdflatex trabalho1_mpc.tex
bibtex trabalho1_mpc
pdflatex trabalho1_mpc.tex
pdflatex trabalho1_mpc.tex
latexmk -c
open trabalho1_mpc.pdf