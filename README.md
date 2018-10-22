# <b> Health Dashboard Service </b>
___

Simple service which monitoring health of multiple services.

Project Tree

```
├── Dockerfile
├── README.md
├── api
│   ├── __init__.py
│   ├── run.py
│   └── v1
│       ├── __init__.py
│       └── routes.py
├── internal
│   ├── configs.py
│   └── db.json
├── responses_samples
│   ├── response_a.json
│   ├── response_b.json
│   └── response_c.xml
├── tests
│   └── general.py
└── utils
    ├── __init__.py
    ├── healthUtils.py
    └── helpers.py
```

# <b> Routes </b>

### /v1/services/availability/status

<i> Output example: </i>

```json
{
    "servicesAvailabilityStatus": [
        {
        "service": "https://bim360dm-dev.autodesk.com/health?self=true",
        "availability": "83.33%"
        },
        {
        "service": "https://commands.bim360dm-dev.autodesk.com/health",
        "availability": "83.33%"
        },
        {
        "service": "https://360-staging.autodesk.com/health",
        "availability": "83.33%"
        }
    ]
}
```

### /v1/services/health

<i> Output example: </i>

```json
    {
    "ServicesHealthInfo": [
        {
        "serviceUrl": "https://bim360dm-dev.autodesk.com/health?self=true",
        "currentStatus": "Healthy",
        "dateTime": 1540238788,
        "serviceName": "bim360-dm"
        },
        {
        "serviceUrl": "https://commands.bim360dm-dev.autodesk.com/health",
        "currentStatus": "Healthy",
        "dateTime": 1540238788,
        "serviceName": "Command Processor"
        },
        {
        "serviceUrl": "https://360-staging.autodesk.com/health",
        "currentStatus": "Healthy",
        "dateTime": 1540238788,
        "serviceName": "IP-AC1860D3"
        }
    ]
}
```

# <b> Add / Modify services to be monitored </b>

To Add / Modify services move to the `internal` folder and  open the `configs.py` file.


Add / Remove / Modify service can be changed at this section.

```python
KNOWN_SERVICES = [
    'https://bim360dm-dev.autodesk.com/health?self=true',
    'https://commands.bim360dm-dev.autodesk.com/health',
    'https://360-staging.autodesk.com/health'
]
```

Checking interval can be modify too

```python
INTERVAL = 60   # 60 MINUTES.
```

The interval value is crucial value since it is determine
how much data to save and how's the availability calculated for the services.

** Note:
default 60 simpley means: 60 minutes 
So, 60 minutes for every 1 minute samples = 60 samples.
if every sample returned with good health then the availability is 100%.


# <b> Tests </b>

Tests are very basic and probably not cover all cases. 
to run the test file just execute it from the `tests` directory.


# <b> Deploy </b>


```sh
Docker build -t healthservice . && docker run -d -p 5555:5555 healthservice
```

You can now direct into the browser and make requests.
http://localhost:5555/v1/services/availability/status
http://localhost:5555/v1/services/health


# <b> Whys? </b>

Q: why CamlCase and not snake_case ?
</br>
A: I think its cleaner but PEP-8 in general is a nice guideline.
</br>
</br>
Q: Why file as a storage.
</br>
A: Its a dummy service, (POC) use this service with his current mode will not work due to the fact that the write / read is not thread safe.
</br>
</br>
Q: why this framework ?
</br>
A: No idea, it looked nice, so I decided to try play with it.