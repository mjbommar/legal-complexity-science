# Create directory structure
mkdir -p data/input
mkdir -p data/pickle
mkdir -p data/output

# Download input ZIP files
wget -O data/input/1994.zip http://uscode.house.gov/download/annualhistoricalarchives/XHTML/1994.zip
wget -O data/input/1995.zip http://uscode.house.gov/download/annualhistoricalarchives/XHTML/1995.zip
wget -O data/input/1996.zip http://uscode.house.gov/download/annualhistoricalarchives/XHTML/1996.zip
wget -O data/input/1997.zip http://uscode.house.gov/download/annualhistoricalarchives/XHTML/1997.zip
wget -O data/input/1998.zip http://uscode.house.gov/download/annualhistoricalarchives/XHTML/1998.zip
wget -O data/input/1999.zip http://uscode.house.gov/download/annualhistoricalarchives/XHTML/1999.zip
wget -O data/input/2000.zip http://uscode.house.gov/download/annualhistoricalarchives/XHTML/2000.zip
wget -O data/input/2001.zip http://uscode.house.gov/download/annualhistoricalarchives/XHTML/2001.zip
wget -O data/input/2002.zip http://uscode.house.gov/download/annualhistoricalarchives/XHTML/2002.zip
wget -O data/input/2003.zip http://uscode.house.gov/download/annualhistoricalarchives/XHTML/2003.zip
wget -O data/input/2004.zip http://uscode.house.gov/download/annualhistoricalarchives/XHTML/2004.zip
wget -O data/input/2005.zip http://uscode.house.gov/download/annualhistoricalarchives/XHTML/2005.zip
wget -O data/input/2006.zip http://uscode.house.gov/download/annualhistoricalarchives/XHTML/2006.zip
wget -O data/input/2007.zip http://uscode.house.gov/download/annualhistoricalarchives/XHTML/2007.zip
wget -O data/input/2008.zip http://uscode.house.gov/download/annualhistoricalarchives/XHTML/2008.zip
wget -O data/input/2009.zip http://uscode.house.gov/download/annualhistoricalarchives/XHTML/2009.zip
wget -O data/input/2010.zip http://uscode.house.gov/download/annualhistoricalarchives/XHTML/2010.zip
wget -O data/input/2011.zip http://uscode.house.gov/download/annualhistoricalarchives/XHTML/2011.zip
wget -O data/input/2012.zip http://uscode.house.gov/download/annualhistoricalarchives/XHTML/2012.zip
wget -O data/input/2013.zip http://uscode.house.gov/download/annualhistoricalarchives/XHTML/2013.zip
wget -O data/input/2014.zip http://uscode.house.gov/download/annualhistoricalarchives/XHTML/2014.zip

# Setup virtual environment
virtualenv env
./env/bin/pip install -r python-requirements.txt
