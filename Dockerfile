FROM httpd
RUN apt-get update && apt-get -y install perl && apt-get -y install libcgi-pm-perl
RUN mkdir /usr/local/apache2/htdocs/boogle-dice
COPY ./httpd.conf /usr/local/apache2/conf
COPY data/16-uppercase.txt /usr/local/apache2/htdocs/boogle-dice
COPY data/16-lowercase.txt /usr/local/apache2/htdocs/boogle-dice
COPY data/25-uppercase.txt /usr/local/apache2/htdocs/boogle-dice
COPY data/25-lowercase.txt /usr/local/apache2/htdocs/boogle-dice
COPY app/configure-boogle.html /usr/local/apache2/htdocs
COPY app/perl-boogle.cgi /usr/local/apache2/cgi-bin
