.PHONY: setup test annotate push clean

setup:
	ln -sf ../../hooks/pre-commit .git/hooks/pre-commit
	@echo "✓ Pre-commit hook installed"

test:
	node test_annotations.js

annotate:
	python3 annotate.py

push: test
	rm -f ~/.ssh/sockets/git@github.com-22
	git push origin main

clean:
	rm -f data/batch_*.json data/tags_*.json data/notices_*.json data/warn_batch_*.json
	rm -rf __pycache__
