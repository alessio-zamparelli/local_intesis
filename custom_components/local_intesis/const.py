DOMAIN = "local_intesis"

DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin"

CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_SCAN_INTERVAL = 300
MIN_SCAN_INTERVAL = 6
MAX_SCAN_INTERVAL = 300

API_LOGIN = "login"
API_GET_INFO = "getinfo"
API_GET_DP = "getavailabledatapoints"
API_GET_VALUE = "getdatapointvalue"
API_SET_VALUE = "setdatapointvalue"

UID_POWER = 1
UID_MODE = 2
UID_FAN_SPEED = 4
UID_VVANE = 5
UID_HVANE = 6
UID_SETPOINT = 9
UID_TEMPERATURE = 10
UID_SETPOINT_MIN = 35
UID_SETPOINT_MAX = 36
UID_OUTDOOR_TEMP = 37
UID_CONFIG_VVANE = 63
UID_CONFIG_HVANE = 64
UID_CLIMATE_WORKING_MODE = 42
UID_AQUAREA_COOL_CONSUMPTION = 81
UID_AQUAREA_HEAT_CONSUMPTION = 82
UID_ALARM_STATUS = 14
UID_ERROR_CODE = 15
UID_ERROR_CODE_LEGACY = 144
UID_RSSI = 60002

ERROR_COMMUNICATION_VALUE = 65535

MODE_MAP = {
    0: "auto",
    1: "heat",
    2: "dry",
    3: "fan",
    4: "cool",
}

MODE_REVERSE = {v: k for k, v in MODE_MAP.items()}

HVAC_MODE_MAP = {
    "auto": "heat_cool",
    "heat": "heat",
    "dry": "dry",
    "fan": "fan_only",
    "cool": "cool",
}

HVAC_MODE_REVERSE = {v: k for k, v in HVAC_MODE_MAP.items()}

FAN_SPEED_TABLES = {
    6: {1: "low", 2: "high"},
    7: {0: "auto", 1: "low", 2: "high"},
    14: {1: "low", 2: "medium", 3: "high"},
    15: {0: "auto", 1: "low", 2: "medium", 3: "high"},
    30: {0: "auto", 1: "low", 2: "medium", 3: "high", 4: "high"},
    31: {0: "auto", 1: "low", 2: "medium", 3: "high", 4: "high"},
    62: {1: "quiet", 2: "low", 3: "medium", 4: "high", 5: "max"},
    63: {0: "auto", 1: "quiet", 2: "low", 3: "medium", 4: "high", 5: "max"},
    126: {1: "speed 1", 2: "speed 2", 3: "speed 3", 4: "speed 4", 5: "speed 5", 6: "speed 6"},
    127: {0: "auto", 1: "speed 1", 2: "speed 2", 3: "speed 3", 4: "speed 4", 5: "speed 5", 6: "speed 6"},
}

PRESET_MODE_MAP = {
    0: "comfort",
    1: "eco",
    2: "powerful",
}
ERROR_MAP = {
    0: {"code": "H00", "desc": "No abnormality detected"},
    2: {"code": "H91", "desc": "Tank booster heater OLP abnormality"},
    13: {"code": "F38", "desc": "Unknown"},
    20: {"code": "H90", "desc": "Indoor/outdoor abnormal communication"},
    36: {"code": "H99", "desc": "Indoor heat exchanger freeze prevention"},
    38: {"code": "H72", "desc": "Tank temperature sensor abnormality"},
    42: {"code": "H12", "desc": "Indoor/outdoor capacity unmatched"},
    156: {"code": "H76", "desc": "Indoor - control panel communication abnormality"},
    193: {"code": "F12", "desc": "Pressure switch activate"},
    195: {"code": "F14", "desc": "Outdoor compressor abnormal rotation"},
    196: {"code": "F15", "desc": "Outdoor fan motor lock abnormality"},
    197: {"code": "F16", "desc": "Total running current protection"},
    200: {"code": "F20", "desc": "Outdoor compressor overheating protection"},
    202: {"code": "F22", "desc": "IPM overheating protection"},
    203: {"code": "F23", "desc": "Outdoor DC peak detection"},
    204: {"code": "F24", "desc": "Refrigerant cycle abnormality"},
    205: {"code": "F27", "desc": "Pressure switch abnormality"},
    207: {"code": "F46", "desc": "Outdoor current transformer open circuit"},
    208: {"code": "F36", "desc": "Outdoor air temperature sensor abnormality"},
    209: {"code": "F37", "desc": "Indoor water inlet temperature sensor abnormality"},
    210: {"code": "F45", "desc": "Indoor water outlet temperature sensor abnormality"},
    212: {"code": "F40", "desc": "Outdoor discharge pipe temperature sensor abnormality"},
    214: {"code": "F41", "desc": "PFC control"},
    215: {"code": "F42", "desc": "Outdoor heat exchanger temperature sensor abnormality"},
    216: {"code": "F43", "desc": "Outdoor defrost temperature sensor abnormality"},
    222: {"code": "H95", "desc": "Indoor/outdoor wrong connection"},
    224: {"code": "H15", "desc": "Outdoor compressor temperature sensor abnormality"},
    225: {"code": "H23", "desc": "Indoor refrigerant liquid temperature sensor abnormality"},
    226: {"code": "H24", "desc": "Unknown"},
    227: {"code": "H38", "desc": "Indoor/outdoor mismatch"},
    228: {"code": "H61", "desc": "Unknown"},
    229: {"code": "H62", "desc": "Water flow switch abnormality"},
    230: {"code": "H63", "desc": "Refrigerant low pressure abnormality"},
    231: {"code": "H64", "desc": "Refrigerant high pressure abnormality"},
    232: {"code": "H42", "desc": "Compressor low pressure abnormality"},
    233: {"code": "H98", "desc": "Outdoor high pressure overload protection"},
    234: {"code": "F25", "desc": "Cooling/heating cycle changeover abnormality"},
    235: {"code": "F95", "desc": "Cooling high pressure overload protection"},
    236: {"code": "H70", "desc": "Indoor backup heater OLP abnormality"},
    237: {"code": "F48", "desc": "Outdoor EVA outlet temperature sensor abnormality"},
    238: {"code": "F49", "desc": "Outdoor bypass outlet temperature sensor abnormality"},
    ERROR_COMMUNICATION_VALUE: {"code": "N/A", "desc": "Communication error between PA-IntesisHome"},
}
