# Minimal makefile for Sphinx documentation
#

# https://github.com/deepcharles/ruptures/pull/26

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    =
SPHINXBUILD   = python3 -msphinx
SPHINXPROJ    = ssp
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

ssp:
	touch source/ssp/temp.rst
	rm source/ssp/*.rst
	sphinx-apidoc -E -M -d 2 -f ../src/ssp/ -o source/ssp/
	cd source/ssp/ && sed -i 's/ package//g' *.rst
	cd source/ssp/ && sed -i 's/Submodules//g' *.rst
	cd source/ssp/ && sed -i 's/Subpackages//g' *.rst
	@make clean
	@make html
	git add -f build/
	git add .
