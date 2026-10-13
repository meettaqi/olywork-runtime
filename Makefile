.PHONY: test compile

test:
	python -m pytest tests -q

compile:
	python -m compileall -q olywork_runtime
