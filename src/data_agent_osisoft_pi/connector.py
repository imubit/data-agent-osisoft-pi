# Some references:
# https://github.com/mucoucah/PI_Python/blob/master/PIthon.py
# https://pisquare.osisoft.com/s/question/0D51I00004UHq9cSAD/python-36-and-afsdk-example-pithon
# https://github.com/FernandoRodriguezP/OSIsoftPy/blob/master/OSIsoftPy.py
# https://stackoverflow.com/questions/73263178/extract-pi-osisoft-monthly-interval-in-python
# https://github.com/Hugovdberg/PIconnect
# https://github.com/nielsvth/PIconnect/network

import logging
import sys
from datetime import datetime
from typing import Union

import clr
import numpy as np
import pandas as pd
from data_agent.abstract_connector import (
    AbstractConnector,
    SupportedOperation,
    active_connection,
)

# from data_agent.groups_aware_connector import GroupsAwareConnector
from data_agent.exceptions import TargetConnectionError

sys.path.append(r"C:\Program Files (x86)\PIPC\AF\PublicAssemblies\4.0")
clr.AddReference("OSIsoft.AFSDK")


# from OSIsoft.AF import * # noqa: E402
# from OSIsoft.AF.Asset import * # noqa: E402
# from OSIsoft.AF.UnitsOfMeasure import * # noqa: E402
from OSIsoft.AF.Data import AFBoundaryType  # noqa: E402
from OSIsoft.AF.PI import (  # noqa: E402
    PIPoint,
    PIPointType,
    PIServers,
    PITimeoutException,
)
from OSIsoft.AF.Time import AFTime, AFTimeRange, AFTimeSpan  # noqa: E402

# from System import TimeSpan # noqa: E402
from System.Collections.Generic import List  # noqa: E402

# from System.Net import NetworkCredential # noqa: E402

log = logging.getLogger(f"ia_plugin.{__name__}")


def _get_from_dict(dataDict, mapList):
    if mapList == [""]:
        return dataDict

    for k in mapList:
        dataDict = dataDict[k]
    return dataDict


def timestamp_to_datetime(timestamp):
    """Convert AFTime object to datetime in local timezone.

    Args:
        timestamp (`System.DateTime`): Timestamp in .NET format to convert to `datetime`.

    Returns:
        `datetime`: Datetime with the timezone info from :data:`PIConfig.DEFAULT_TIMEZONE
                    <PIconnect.config.PIConfigContainer.DEFAULT_TIMEZONE>`.
    """
    return datetime(
        timestamp.Year,
        timestamp.Month,
        timestamp.Day,
        timestamp.Hour,
        timestamp.Minute,
        timestamp.Second,
        timestamp.Millisecond * 1000,
    )


MAP_PITYPE_2_NUMPY = {
    PIPointType.Null: None,
    PIPointType.Int16: np.int16,
    PIPointType.Int32: np.int32,
    PIPointType.Float16: np.float16,
    PIPointType.Float32: np.float32,
    PIPointType.Float64: np.float64,
    PIPointType.Digital: bool,
    PIPointType.Timestamp: np.datetime64,
    PIPointType.String: str,
    PIPointType.Blob: object,
}

MAP_TIME_FREQUENCY_TO_PI = {"raw data": None}


def cast2python(val):
    if str(type(val)) == "<class 'System.DateTime'>":
        return timestamp_to_datetime(val)

    if str(type(val)) == "<class 'OSIsoft.AF.PI.PIPointType'>":
        return MAP_PITYPE_2_NUMPY[val]

    return val


class OsisoftPiConnector(AbstractConnector):
    TYPE = "osisoft-pi"
    CATEGORY = "historian"
    SUPPORTED_FILTERS = ["name", "tags_file", "time"]
    SUPPORTED_OPERATIONS = [
        SupportedOperation.READ_TAG_PERIOD,
        SupportedOperation.READ_TAG_META,
    ]
    DEFAULT_ATTRIBUTES = [
        ("tag", {"Type": "str", "Name": "Tag Name"}),
        ("engunits", {"Type": "str", "Name": "Units"}),
        ("typicalvalue", {"Type": "str", "Name": "Typical Value"}),
        ("descriptor", {"Type": "str", "Name": "Description"}),
        ("pointsource", {"Type": "str", "Name": "Point Source"}),
        # ('pointtype', {
        #     'Type': str,
        #     'Name': 'Type'
        # }),
        ("compressing", {"Type": "int", "Name": "Compression"}),
        ("changer", {"Type": "str", "Name": "Modified By"}),
    ]
    DEFAULT_PAGE_SIZE = 200000
    ABSOLUTE_MAX_VALUES_TO_READ = 1000000000

    def __init__(self, conn_name="pi_client", server_name="default", **kwargs):
        super(OsisoftPiConnector, self).__init__(conn_name)
        self._server = None
        self._server_name = server_name
        self._page_size = (
            int(kwargs["page_size"])
            if "page_size" in kwargs
            else OsisoftPiConnector.DEFAULT_PAGE_SIZE
        )

    @staticmethod
    def list_connection_fields():
        return {
            "server_name": {
                "name": "Server Name",
                "type": "list",
                "values": [
                    i["Name"] for i in OsisoftPiConnector.list_registered_targets()
                ],
                "default_value": "",
                "optional": False,
            },
            "page_size": {
                "name": "Data Read Page Size",
                "type": "list",
                "values": ["200000", "20000", "10000", "5000", "1000"],
                "default_value": OsisoftPiConnector.DEFAULT_PAGE_SIZE,
                "optional": False,
            },
        }

    @staticmethod
    def list_registered_targets():
        pi_servers = PIServers()
        ret = []

        for srv in pi_servers:
            ret.append(
                {
                    "uid": f"{OsisoftPiConnector.TYPE}::{srv.Name}:{srv.UniqueID}",
                    "Name": srv.Name,
                    "Host": srv.ConnectionInfo.Host,
                    "Port": srv.ConnectionInfo.Port,
                }
            )

        return ret

    @staticmethod
    def target_info(host=None):
        return {"Name": "absolute-fake", "Endpoints": []}

    @property
    def connected(self):
        return self._server is not None

    def connect(self):
        self._server = None

        for srv in PIServers():
            if self._server_name == srv.Name:
                self._server = srv

        if not self._server:
            raise TargetConnectionError(
                f"Error connecting to {self._server_name} - this server is not registered under PIServers()"
            )

        try:
            # https://docs.aveva.com/bundle/af-sdk/page/html/M_OSIsoft_AF_PI_PIServer_Connect.htm
            self._server.Connect(force=True)

            log.debug(f"Connected to {self._server_name}, page_size={self._page_size}")

        except Exception as e:
            self._server = None
            raise TargetConnectionError(
                f"Error connecting to {self._server_name} - {e}"
            )

    @active_connection
    def disconnect(self):
        self._server.Disconnect()
        self._server = None

    @active_connection
    def connection_info(self):
        return {
            "OneLiner": f"[{self.TYPE}] '{self._server.Name}'@{self._server.ConnectionInfo.Host}:"
            f"{self._server.ConnectionInfo.Port} ",
            "ServerName": self._server.Name,
            "Description": self._server.Description,
            "Version": self._server.ServerVersion,
            "Host": self._server.ConnectionInfo.Host,
            "Port": self._server.ConnectionInfo.Port,
        }

    @active_connection
    def list_tags(
        self,
        filter: Union[str, list] = "",
        include_attributes: Union[bool, list] = False,
        recursive: bool = False,
        max_results: int = 0,
    ):
        if max_results == 0:
            max_results = 2**32

        if isinstance(include_attributes, list):
            dotnet_attributes = List[str]()
            for attr in include_attributes:
                dotnet_attributes.Add(attr)

        # https://pisquare.osisoft.com/s/Blog-Detail/a8r1I000000H723QAC/passing-a-list-of-tag-names-to-the-findpipoints-method
        # https://github.com/bzshang/PI-AF-SDK-Basic-Samples/blob/master/ExamplesLibrary/ReadingValuesExamples/ReadFromPIExample.cs
        if isinstance(filter, list):
            dotnet_filter = List[str]()
            for tag in filter:
                dotnet_filter.Add(tag)

            # Find tags by passing a list
            # https://docs.aveva.com/bundle/af-sdk/page/html/M_OSIsoft_AF_PI_PIPoint_FindPIPoints_2.htm
            pts = PIPoint.FindPIPoints(
                self._server,
                dotnet_filter,
                dotnet_attributes if isinstance(include_attributes, list) else None,
            )

        else:
            # https://docs.aveva.com/en-US/bundle/af-sdk/page/html/M_OSIsoft_AF_PI_PIPoint_FindPIPoints_4.htm
            pts = PIPoint.FindPIPoints(
                self._server,
                filter,
                None,
                dotnet_attributes if isinstance(include_attributes, list) else None,
            )

        if include_attributes:
            res = {}
            for ind, pt in zip(range(max_results), pts):
                res[pt.Name] = {
                    a: cast2python(pt.GetAttribute(a))
                    for a in pt.FindAttributeNames(None)
                }
                res[pt.Name]["HasChildren"] = False
        else:
            res = {
                pt.Name: {"Name": pt.Name, "HasChildren": False}
                for _, pt in zip(range(max_results), pts)
            }

        return res

    @active_connection
    def read_tag_attributes(self, tags: list, attributes: list = None):
        names = tags
        if isinstance(tags, list):
            names = List[str]()
            for tag in tags:
                names.Add(tag)

        if attributes is not None:
            dotnet_attributes = List[str]()
            for attr in attributes:
                dotnet_attributes.Add(attr)

        pts = PIPoint.FindPIPoints(
            self._server,
            names,
            dotnet_attributes if isinstance(attributes, list) else None,
        )

        res = {}
        for pt in pts:
            attributes = (
                attributes
                if isinstance(attributes, list)
                else pt.FindAttributeNames(None)
            )
            res[pt.Name] = {a: cast2python(pt.GetAttribute(a)) for a in attributes}

        return res

    @active_connection
    def read_tag_values(self, tags: list):
        raise RuntimeError("unsupported")

    @active_connection
    def read_tag_values_period(
        self,
        tags: list,
        first_timestamp=None,
        last_timestamp=None,
        time_frequency=None,
        max_results=None,
        result_format="dataframe",
        progress_callback=None,
    ):
        # if isinstance(first_timestamp, str):
        #     first_timestamp = parser.parse(first_timestamp)
        # if isinstance(last_timestamp, str):
        #     last_timestamp = parser.parse(last_timestamp)
        if isinstance(first_timestamp, datetime):
            first_timestamp = first_timestamp.strftime("%Y/%m/%d %H:%M:%S")
        if isinstance(last_timestamp, datetime):
            last_timestamp = last_timestamp.strftime("%Y/%m/%d %H:%M:%S")

        total_values_to_read = max_results or self.ABSOLUTE_MAX_VALUES_TO_READ

        assert result_format in ["dataframe", "series", "tuple"]

        names = tags
        if isinstance(tags, list):
            names = List[str]()
            for tag in tags:
                names.Add(tag)

        pts = PIPoint.FindPIPoints(self._server, names, None)

        if first_timestamp or last_timestamp:
            start_time = AFTime(first_timestamp)
            end_time = AFTime(last_timestamp)

            time_range = AFTimeRange(start_time, end_time)

            freq = (
                MAP_TIME_FREQUENCY_TO_PI[time_frequency.lower()]
                if time_frequency and time_frequency.lower() in MAP_TIME_FREQUENCY_TO_PI
                else time_frequency
            )

            tag_series = []
            for pt in pts:
                if progress_callback:
                    progress_callback(pt.Name.lower())

                # Read pages
                page_series = []

                if freq:
                    log.debug(
                        f"Reading interpolated values (freq='{freq}') for range {time_range}..."
                    )

                    #  https://docs.aveva.com/bundle/af-sdk/page/html/T_OSIsoft_AF_Time_AFTimeSpan.htm
                    time_span = AFTimeSpan.Parse(freq)

                    next_start_time = start_time

                    # print('starting')

                    while (
                        next_start_time < time_range.EndTime
                        and total_values_to_read > 0
                    ):
                        values_to_read = min(self._page_size, total_values_to_read)

                        next_end_time = (
                            time_span.Multiply(next_start_time, values_to_read - 1)
                            if time_span.Multiply(next_start_time, values_to_read - 1)
                            < time_range.EndTime
                            else time_range.EndTime
                        )

                        page_time_range = AFTimeRange(next_start_time, next_end_time)

                        # https://docs.aveva.com/bundle/af-sdk/page/html/M_OSIsoft_AF_PI_PIPoint_InterpolatedValues.htm
                        try:
                            records = pt.InterpolatedValues(
                                page_time_range, time_span, "", False
                            )
                        except PITimeoutException as e:
                            log.warn(
                                f"Retrying after pt.InterpolatedValues timeout: {e}"
                            )
                            records = pt.InterpolatedValues(
                                page_time_range, time_span, "", False
                            )

                        if records.Count == 0:
                            break

                        total_values_to_read -= records.Count

                        formatted_data = {
                            timestamp_to_datetime(val.Timestamp.UtcTime): val.Value
                            for val in records
                        }
                        page_series.append(
                            pd.Series(
                                formatted_data,
                                index=list(formatted_data.keys()),
                                name=pt.Name,
                                dtype=None if records else np.float32,
                            )
                        )

                        next_start_time = (
                            records[records.Count - 1].Timestamp + time_span
                        )

                else:
                    log.debug("Reading recorded values for ...")

                    # https://docs.aveva.com/bundle/af-sdk/page/html/T_OSIsoft_AF_Data_AFBoundaryType.htm
                    boundary = AFBoundaryType.Inside
                    next_start_time = start_time

                    # print('starting')
                    # print(f'range: {time_range}            next_start_time={next_start_time}')

                    while (
                        next_start_time < time_range.EndTime
                        and total_values_to_read > 0
                    ):
                        page_time_range = AFTimeRange(
                            next_start_time, time_range.EndTime
                        )

                        values_to_read = min(self._page_size, total_values_to_read)

                        # https://docs.aveva.com/bundle/af-sdk/page/html/M_OSIsoft_AF_PI_PIPoint_RecordedValues.htm
                        try:
                            records = pt.RecordedValues(
                                page_time_range, boundary, "", False, values_to_read
                            )
                        except PITimeoutException as e:
                            log.warn(f"Retrying after pt.RecordedValues timeout: {e}")
                            records = pt.RecordedValues(
                                page_time_range, boundary, "", False, values_to_read
                            )

                        if records.Count == 0:
                            break

                        total_values_to_read -= records.Count

                        formatted_data = {
                            timestamp_to_datetime(val.Timestamp.UtcTime): val.Value
                            for val in records
                        }
                        page_series.append(
                            pd.Series(
                                formatted_data,
                                index=list(formatted_data.keys()),
                                name=pt.Name,
                                dtype=None if records else np.float32,
                            )
                        )

                        next_start_time = records[
                            records.Count - 1
                        ].Timestamp + AFTimeSpan.Parse("1 second")

                tag_series.append(
                    pd.concat(page_series, axis=0, sort=True)
                    if page_series
                    else pd.Series([], name=pt.Name, dtype=np.float32)
                )

            if not tag_series:
                return None

            if result_format == "dataframe":
                df = pd.concat(tag_series, axis=1, sort=True)
                df.index.name = "timestamp"
                return df
            elif result_format == "series":
                return tag_series if len(tag_series) > 1 else tag_series[0]
            else:
                raise NotImplementedError(f"{result_format} not yet implemented")

            # TODO: Bulk Support - https://csharp.hotexamples.com/examples/-/PIPointList/RecordedValues/php-pipointlist-recordedvalues-method-examples.html # noqa: E501

    @active_connection
    def write_tag_values(self, tags: dict, wait_for_result: bool = True, **kwargs):
        raise RuntimeError("unsupported")
