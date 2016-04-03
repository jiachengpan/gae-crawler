test:
	./test_runner.py ~/tools/google_appengine .

clean:
	find . -name "*.pyc" | xargs rm
