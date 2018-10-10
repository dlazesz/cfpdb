
INPUT=confdata.INFO
#INPUT=~/cvswork/admin/CLconf.INFO

#LOCALDIR=/home/joker/public_html/cfpdb

REMOTEDIR=???
#REMOTEDIR=sass@users.itk.ppke.hu:public_html

all: txt2xml db deploy

txt2xml:
	cat $(INPUT) | ./txt2xml.pl

db:
	rm -f cfp.db
	./cfpdb_create.pl
	for i in conf.*.xml ; do ./cfpdb_insert.pl -f $$i ; done
	./cfpdb_select.pl > cfps.xml

deploy:
	scp -p cfps.xml cfps.dtd cfps_plain.xsl.xml $(REMOTEDIR)

