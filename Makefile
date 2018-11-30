# NAME: Clayton Chu, George Zhang
# EMAIL: claytonchu99@gmail.com, georgezhang@ucla.edu
# ID: 104906833, 504993197

default:
	rm -f lab3b
	echo '#!/bin/bash' > lab3b
	echo 'python lab3b.py $$1' >> lab3b
	chmod +x lab3b

dist:
	tar -czvf lab3b-504993197.tar.gz lab3b.py Makefile README

clean:
	rm -f lab3b *.tar.gz
