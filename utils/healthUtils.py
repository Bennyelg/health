import json
import re
import os
import logging

from typing import Dict, List, Any
from six import string_types
from datetime import datetime, timedelta
from functools import singledispatch

from vibora import Vibora, Request
from vibora.responses import JsonResponse

from utils.helpers import hoursToSeconds, minutesToSeconds
from internal.configs import KNOWN_SERVICES, INTERVAL
import requests


#* HealthService functionality utils *#


def getServiceHealthInfo(serviceHealthUrl: str, cache: Dict[str, List[Dict[str, str]]]) -> List[Dict[str, Any]]:
    # getServiceHealthInfo - Get serviceHealthLogs information by specifing the service name.
    
    try:
        return cache[serviceHealthUrl]
    except KeyError:
        cache[serviceHealthUrl] = []
    
    return cache[serviceHealthUrl]


def getServiceResponse(url: str) -> requests.Response:
    # getServiceResponse - Making a `GET` response by giving URL.
    # If the response is failed to retrive we return an empty response.

    try:
        response = requests.get(url)
        return response
    except requests.exceptions.ConnectionError as err:
        logging.warning(f"Failed to extract response: {err}")
        return requests.Response()


def decodeResponse(response: requests.Response, injected=False) -> Dict[str, str]:
    # decodeResponse - By giving a response parsing the values we need.
    # Incase of failure we try to parse it using an xml decoder
    # arg: injected - is passed to notify that mimic response is passed.

    try:
        content = response if injected else response.json()
        serviceStatus = content["status"]["overall"]
        serviceName = content["service"]
    except Exception as err:
        logging.warning(f"Failed to decode json: {err}")
        serviceStatus, serviceName = decodeXMLResponse(response if injected else response.content)
    
    if serviceStatus and serviceName:
        return {
                "lastFetchTime": datetime.now(),
                "serviceName": serviceName,
                "wasHealthy": True if serviceStatus.lower() in ('good', 'ok') else False
                }
    
    return {}


def decodeXMLResponse(content: bytes) -> (str, str):
    # decodeXMLResponse - Parsing XML response using naive regex and string manipulations
    # can be achivie via better & safer ways.

    content = str(content)
    serviceStatus = ""
    serviceName = ""
    
    if content:
        try:
            
            serviceStatus = (
                re.findall(r'<status>[a-zA-Z]+</status>', content)[0]
                  .split("<status>")[1]
                  .split("<")[0]
            )
            
            serviceName = (
                re.findall(r'<machineName>[A-Z-0-9A-Z]+</machineName>', content)[0]
                  .split("<machineName>")[1]
                  .split("<")[0]
            )

        except IndexError as e:
            logging.error(f"Failed to parse URL: {e}")
    
    return serviceStatus, serviceName


def cleanOldSamples(serviceHealthyLogs: List[Dict[str, Any]], interval=INTERVAL) -> List[Dict[str, Any]]:
    # cleanOldSamples - clean old samples we do not need any more for calculation.
    # Don't need any more is depending on the interval we pass.

    return [serviceInfo 
            for serviceInfo in serviceHealthyLogs 
            if serviceInfo["lastFetchTime"] >= datetime.now() - timedelta(seconds=minutesToSeconds(interval))
            ]

    

def getTimesWasHealthyTillAvRequest(avReqDateTime: datetime, serviceHealthyLogs: List[Dict[str, Any]], interval=INTERVAL) -> int:
    # getTimesWasHealthyTillAvRequest - sum all the relevant samples took in the time frame we scheduled.

    return sum(
        1
        for item in serviceHealthyLogs
        if item["lastFetchTime"] >= avReqDateTime - timedelta(seconds=minutesToSeconds(interval)) and item["wasHealthy"]
    )


def readFromCache():
    # readFromCache - Simply read json file.

    with open(os.path.join(os.path.dirname(__file__), '..' , 'internal', 'db.json'), "r") as j:
        try:
            return json.load(j, object_hook=load_with_datetime)
        except Exception as err:
            return {}


def writeToCache(currentCache: Dict[str, str]):
    # writeToCache - Write the current state of our `cache` to the file back.

    with open(os.path.join(os.path.dirname(__file__), '..' , 'internal', 'db.json'), "w+") as fp:
        json.dump(currentCache, fp, ensure_ascii=False, indent=4, default=to_serializable)


# Internal usage. #


@singledispatch
def to_serializable(val):
    """Used by default."""
    return str(val)


def load_with_datetime(pairs, dt="%Y-%m-%d %H:%M:%S.%f"):
    """Load with dates"""
    d = {}
    for k, v in pairs.items():
        if isinstance(v, string_types):
            try:
                d[k] = datetime.strptime(v, dt)
            except ValueError:
                d[k] = v
        else:
            d[k] = v             
    return d