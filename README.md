
[![Built Status](https://api.cirrus-ci.com/github/imubit/data-agent-osisoft-pi.svg?branch=main)](https://cirrus-ci.com/github/imubit/data-agent-osisoft-pi)
[![PyPI-Server](https://img.shields.io/pypi/v/data-agent-osisoft-pi.svg)](https://pypi.org/project/data-agent-osisoft-pi/)
[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)

# data-agent-osisoft-pi

> [Data Agent](https://github.com/imubit/data-agent) plugin for accessing Osisoft PI Historian.


## CLI Examples

Example of using [Data Agent](https://github.com/imubit/data-agent) CLI to access PI tags

```commandline
dagent exec create_connection --conn_name=pi --conn_type=osisoft-pi --enabled=True --server_name=DATA-SERVER
dagent exec list_connections
dagent exec connection_info --conn_name=pi
dagent exec list_tags --conn_name=pi
dagent exec read_tag_values_period --conn_name=pi --tags="['sinusoid', 'sinusoidu']" --first_timestamp=*-100h --last_timestamp=*
dagent exec copy_period --src_conn=pi --tags="['SINUSOID', 'sinusoidu']" --dest_conn=csv --dest_group='sinus.csv' --first_timestamp=*-100h --last_timestamp=*
```


## Troubleshooting

### OSIsoft.AF.PI.PITimeoutException when reading historical data

Increase the SDK data access timeout settings on the client machine. There are two timeouts for the SDK, a connection timeout and a data access timeout. The connection timeout default is 10 seconds.  The data access timeout is 60 seconds. Data access timeouts are the most likely cause of the error.
* Launch AboutPI-SDK.exe.
* Navigate to the Connections tab.
* Select the PI Data Archive in question.
* Increase the Data Access Timeout and Connection Timeout to 120 seconds or more.
