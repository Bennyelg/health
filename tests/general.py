from utils.healthUtils import decodeResponse, cleanOldSamples, getTimesWasHealthyTillAvRequest

import datetime
import requests
import unittest

class TestHealthChecker(unittest.TestCase):
    
    def test_decodeResponseShouldPassIfJsonResponse(self):
        jsonSample = {
            "time": "2018-10-21T14:20:20.900Z",
            "service": "Command Processor",
            "environment": "development",
            "host": "N/A",
            "status": {
            "db": {
            "status": "OK"
            },
            "overall": "OK"
            },
            "build": "4d37d1b8\n0.0.0-2472\n",
            "duration": 3
        }
        sample = decodeResponse(jsonSample, injected=True)
        self.assertTrue(sample["wasHealthy"])
    
    def test_decodeResponseShouldPassIfXMLResponse(self):
        xmlSample = """
        <HealthCheck xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <exception/>
            <machineName>IP-AC1860D3</machineName>
            <status>Good</status>
            <date>2018-10-21T14:20:39.5467387+00:00</date>
            <build>Api.Staging.10.18.2018.215.release_v23_0_0.b34d90c</build>
        </HealthCheck>
        """
        sample = decodeResponse(xmlSample, injected=True)
        self.assertTrue(sample["wasHealthy"])
    
    def test_CleanServiceOldSamplesByGivingIntervalShouldReturnEmptyData(self):
        mockServiceSample = \
        [{'lastFetchTime': datetime.datetime(2018, 10, 22, 17, 51, 41, 317172), 'serviceName': 'bim360-dm', 'wasHealthy': True},
         {'lastFetchTime': datetime.datetime(2018, 10, 22, 17, 52, 12, 802514), 'serviceName': 'bim360-dm', 'wasHealthy': True},
         {'lastFetchTime': datetime.datetime(2018, 10, 22, 17, 52, 56, 731422), 'serviceName': 'bim360-dm', 'wasHealthy': True},
         {'lastFetchTime': datetime.datetime(2018, 10, 22, 17, 53, 56, 629768), 'serviceName': 'bim360-dm', 'wasHealthy':True}]
        self.assertEqual(cleanOldSamples(mockServiceSample, interval=1), [])  # * interval is in minutes

    def test_CleanServiceOldSamplesByGivingIntervalShouldReturnElement(self):
        catchCurrentTime = datetime.datetime.now()
        mockServiceSample = \
        [{'lastFetchTime': datetime.datetime(2018, 10, 22, 17, 51, 41, 317172), 'serviceName': 'bim360-dm', 'wasHealthy': True},
         {'lastFetchTime': datetime.datetime(2018, 10, 22, 17, 52, 12, 802514), 'serviceName': 'bim360-dm', 'wasHealthy': True},
         {'lastFetchTime': datetime.datetime(2018, 10, 22, 17, 52, 56, 731422), 'serviceName': 'bim360-dm', 'wasHealthy': True},
         {'lastFetchTime': catchCurrentTime, 'serviceName': 'bim360-dm', 'wasHealthy':True}]
        self.assertEqual(
            cleanOldSamples(mockServiceSample, interval=1),
            [{'lastFetchTime': catchCurrentTime, 'serviceName': 'bim360-dm', 'wasHealthy':True}]
         )  # * interval is in minutes

    def test_CalculatingTheServiceAvailabilityShouldReturnTheRightValue(self):
        requestedTime = datetime.datetime.now()
        mockServiceSample = \
        [{'lastFetchTime': requestedTime - datetime.timedelta(minutes=2), 'serviceName': 'bim360-dm', 'wasHealthy': True},
         {'lastFetchTime': requestedTime - datetime.timedelta(minutes=3), 'serviceName': 'bim360-dm', 'wasHealthy': True},
         {'lastFetchTime': requestedTime - datetime.timedelta(minutes=4), 'serviceName': 'bim360-dm', 'wasHealthy': True},
         {'lastFetchTime': requestedTime - datetime.timedelta(minutes=1), 'wasHealthy':True}]
        self.assertEqual(
            getTimesWasHealthyTillAvRequest(requestedTime, mockServiceSample, interval=5),
            4
         )  

    def test_CalculatingTheServiceAvailabilityShouldIgnoreOldSamplesIfAny(self):
        requestedTime = datetime.datetime.now()
        mockServiceSample = \
        [{'lastFetchTime': requestedTime - datetime.timedelta(minutes=2), 'serviceName': 'bim360-dm', 'wasHealthy': True},
         {'lastFetchTime': requestedTime - datetime.timedelta(minutes=3), 'serviceName': 'bim360-dm', 'wasHealthy': True},
         {'lastFetchTime': requestedTime - datetime.timedelta(minutes=10), 'serviceName': 'bim360-dm', 'wasHealthy': True}, # this one should ignore.
         {'lastFetchTime': requestedTime - datetime.timedelta(minutes=1), 'wasHealthy':True}]
        self.assertEqual(
            getTimesWasHealthyTillAvRequest(requestedTime, mockServiceSample, interval=5),
            3
         )  

    def test_CalculatingTheServiceAvailabilityShouldIgnoreServiceIfUnhealthy(self):
        requestedTime = datetime.datetime.now()
        mockServiceSample = \
        [{'lastFetchTime': requestedTime - datetime.timedelta(minutes=2), 'serviceName': 'bim360-dm', 'wasHealthy': True},
         {'lastFetchTime': requestedTime - datetime.timedelta(minutes=3), 'serviceName': 'bim360-dm', 'wasHealthy': True},
         {'lastFetchTime': requestedTime - datetime.timedelta(minutes=10), 'serviceName': 'bim360-dm', 'wasHealthy': True}, # this one should ignore.
         {'lastFetchTime': requestedTime - datetime.timedelta(minutes=1), 'wasHealthy': False}]  # should ignore too
        self.assertEqual(
            getTimesWasHealthyTillAvRequest(requestedTime, mockServiceSample, interval=5),
            2
         )  

if __name__ == '__main__':
    unittest.main()