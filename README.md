Covid-19 Analysis
=================
Covid-19 Analysis is a simple script that generates a number of graphs based on data made available by the ECDC.

Usage
-----
Can be run from the commandline (CLI)
    
    usage: python3 -m covid19 [-h] countries [countries ...]

    Generate graphs based on COVID-19 data from ECDC

    positional arguments:
    countries   Countries for which graph's should be created

    optional arguments:
      -h, --help  show this help message and exit

Changelog
---------
v1.0.0
* Initial version

v1.1.0
* New version using Bokeh charts (replacing Matlplotlib)
* Structured to be used as a local package