all: index.html
	rm -rf docs.zip
	markdown README.md > index.html
	zip docs.zip index.html

index.html: README.md
	markdown $< > $@

README.md:
	cp ../README.md .

purge: clean
	rm -rf docs.zip

clean:
	rm -rf index.html
	rm -rf README.md
