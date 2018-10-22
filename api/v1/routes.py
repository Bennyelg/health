from threading import Timer
from datetime import datetime, timedelta

from vibora import Request
from vibora.responses import JsonResponse
from vibora.blueprints import Blueprint

from internal.configs import KNOWN_SERVICES, INTERVAL
from utils.healthUtils import (
    writeToCache, readFromCache, getServiceHealthInfo, 
    getTimesWasHealthyTillAvRequest, cleanOldSamples, 
    getServiceResponse, decodeResponse
)
from utils.helpers import minutesToSeconds


v1 = Blueprint()


@v1.route("/services/health")
async def getStatuses(request: Request) -> JsonResponse:
    # servicesAvailabilityInfo - Get current state of the service
    # Geather all the services set to be monitored from the `KNOWN_SERVICES`.
    servicesHealthSummary: List[Dict[str, Any]] = [] 
    cache = readFromCache()
    for serviceHealthUrl in KNOWN_SERVICES:
        serviceLogInfo = getServiceHealthInfo(serviceHealthUrl, cache)
        servicesHealthSummary.append(
            {
             "serviceUrl": serviceHealthUrl,
             "currentStatus": ("Healthy" if len(serviceLogInfo) > 0 and serviceLogInfo[-1]["wasHealthy"] else "Not Healthy"),
             "dateTime": datetime.now(), 
             "serviceName": serviceLogInfo[-1]["serviceName"] if len(serviceLogInfo) > 0 else "Unknown"
             }
        )
    return JsonResponse({"ServicesHealthInfo": servicesHealthSummary})


@v1.route("/services/availability/status")
async def servicesAvailabilityInfo() -> JsonResponse:
    # servicesAvailabilityInfo - Calculate the availability of each service
    # from the time requested (which is now) - the INTERVAL (in minutes = default 60)
    # assuming the `getStatuses` route is called every one minute.
    requestedTime = datetime.now()
    servicesAvailability: List[Dict[str, str]] = []
    cache = readFromCache()
    for service in KNOWN_SERVICES:
        try:
            healthCount = getTimesWasHealthyTillAvRequest(requestedTime,cache[service])
            ratio = min((healthCount / INTERVAL) * 100, 100)
            servicesAvailability.append({
                "service": service,
                "availability": f"{ratio:.2f}%"
            })
        except KeyError as err:
            # Failed due to keyError, can be raised if this route is called but we didn't
            # Yet save any sample from the `getStatuses` route.
            servicesAvailability.append({"service": service, "availability": "No Samples"})
            logging.warning(f"No Samples on {service} found.")

    return JsonResponse({"servicesAvailabilityStatus": servicesAvailability})


def sampleStatuses(interval):
    Timer(interval, sampleStatuses, [interval]).start()
    currentCache = readFromCache()
    for serviceHealthUrl in KNOWN_SERVICES:
        response = getServiceResponse(serviceHealthUrl)
        # Get all the known information of the requested service from the CACHE.
        serviceLogInfo = getServiceHealthInfo(serviceHealthUrl, currentCache)
        data = decodeResponse(response)
        if data:
            # We did manage to decode and we have the relevant information of the current status
            # So, we append it to the service log info.
            serviceLogInfo.append(data)
        # Eathier we did manage to get the current state or not
        # We keep clean samples which taken more than 60 minutes ago.

        currentCache[serviceHealthUrl] = cleanOldSamples(serviceLogInfo)
    
    writeToCache(currentCache)


sampleStatuses(minutesToSeconds(1))

