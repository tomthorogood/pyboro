test:
	cp tests/* .
	python lexicon.py

clean:
	rm lexicon.py
	rm test_input.txt
