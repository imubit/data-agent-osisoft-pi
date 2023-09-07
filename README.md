<!-- These are examples of badges you might want to add to your README:
     please update the URLs accordingly

[![Built Status](https://api.cirrus-ci.com/github/<USER>/daconnect-osisoft-pi.svg?branch=main)](https://cirrus-ci.com/github/<USER>/daconnect-osisoft-pi)
[![ReadTheDocs](https://readthedocs.org/projects/daconnect-osisoft-pi/badge/?version=latest)](https://daconnect-osisoft-pi.readthedocs.io/en/stable/)
[![Coveralls](https://img.shields.io/coveralls/github/<USER>/daconnect-osisoft-pi/main.svg)](https://coveralls.io/r/<USER>/daconnect-osisoft-pi)
[![PyPI-Server](https://img.shields.io/pypi/v/daconnect-osisoft-pi.svg)](https://pypi.org/project/daconnect-osisoft-pi/)
[![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/daconnect-osisoft-pi.svg)](https://anaconda.org/conda-forge/daconnect-osisoft-pi)
[![Monthly Downloads](https://pepy.tech/badge/daconnect-osisoft-pi/month)](https://pepy.tech/project/daconnect-osisoft-pi)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/daconnect-osisoft-pi)
-->

[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)

# daconnect-osisoft-pi

> Add a short description here!

A longer description of your project goes here...


<!-- pyscaffold-notes -->

## Note

This project has been set up using PyScaffold 4.3.1. For details and usage
information on PyScaffold see https://pyscaffold.org/.


## CLI Examples

```commandline
imagent exec create_connection --conn_name=pi --conn_type=osisoft-pi --enabled=True --server_name=DATA-ANALYSIS-W
imagent exec list_connections
imagent exec connection_info --conn_name=pi
imagent exec list_tags --conn_name=pi
imagent exec read_tag_values_period --conn_name=pi --tags="['sinusoid', 'sinusoidu']" --first_timestamp=*-100h --last_timestamp=*
imagent exec copy_period --src_conn=pi --tags="['SINUSOID', 'sinusoidu']" --dest_conn=csv --dest_group='sinus.csv' --first_timestamp=*-100h --last_timestamp=*
```
