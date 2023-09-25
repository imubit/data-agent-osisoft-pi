
[![Built Status](https://api.cirrus-ci.com/github/imubit/data-agent-osisoft-pi.svg?branch=main)](https://cirrus-ci.com/github/imubit/data-agent-osisoft-pi)
[![Coveralls](https://img.shields.io/coveralls/github/imubit/data-agent-osisoft-pi/main.svg)](https://coveralls.io/r/imubit/data-agent-osisoft-pi)
[![PyPI-Server](https://img.shields.io/pypi/v/data-agent-osisoft-pi.svg)](https://pypi.org/project/data-agent-osisoft-pi/)
[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)

# data-agent-osisoft-pi

> [Data Agent](https://github.com/imubit/data-agent) plugin for accessing Osisoft PI Historian.


## CLI Examples

Example of using [Data Agent](https://github.com/imubit/data-agent) CLI to access PI tags

```commandline
imagent exec create_connection --conn_name=pi --conn_type=osisoft-pi --enabled=True --server_name=DATA-ANALYSIS-W
imagent exec list_connections
imagent exec connection_info --conn_name=pi
imagent exec list_tags --conn_name=pi
imagent exec read_tag_values_period --conn_name=pi --tags="['sinusoid', 'sinusoidu']" --first_timestamp=*-100h --last_timestamp=*
imagent exec copy_period --src_conn=pi --tags="['SINUSOID', 'sinusoidu']" --dest_conn=csv --dest_group='sinus.csv' --first_timestamp=*-100h --last_timestamp=*
```
