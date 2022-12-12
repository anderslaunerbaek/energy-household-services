import enum
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

import requests

DATETIME_FORMAT: str = "YYYY-MM-DD"


class TimeSerieAggLevels(Enum):

    ACTUAL = "Actual"
    QUARTER = "Quarter"
    HOUR = "Hour"
    DAY = "Day"
    MONTH = "Month"
    YEAR = "Year"


@dataclass
class MeteringPoint:
    streetCode: str
    streetName: str
    buildingNumber: str
    floorId: str
    roomId: str
    citySubDivisionName: str
    municipalityCode: int
    locationDescription: str
    settlementMethod: str
    meterReadingOccurrence: str
    firstConsumerPartyName: str
    secondConsumerPartyName: str
    meterNumber: int
    consumerStartDate: datetime
    meteringPointId: str
    typeOfMP: str
    balanceSupplierName: str
    postcode: int
    cityName: str
    hasRelation: bool
    consumerCVR: int
    dataAccessCVR: int
    childMeteringPoints: list = field(default_factory=list)


@dataclass
class MeteringPoints:
    result: list[MeteringPoint]

    @property
    def metering_point_ids(self) -> list[str]:
        return [itm.meteringPointId for itm in self.result]


@dataclass
class Electricity:

    token: str
    token_data: str = field(init=False)
    metering_points: MeteringPoints = field(init=False)

    def __post_init__(self):

        self.token_data = self.get_token_data()

        self.metering_points = self.get_metering_points()

    def get_token_data(self) -> str:
        url_token_data: str = "https://api.eloverblik.dk/CustomerApi/api/token"

        response = requests.get(url_token_data, headers=self.get_headers(self.token))

        return response.json()["result"]

    def get_metering_points(self) -> MeteringPoints:
        url: str = (
            "https://api.eloverblik.dk/CustomerApi/api/meteringpoints/meteringpoints"
        )

        response = requests.get(url, headers=self.get_headers(self.token_data))

        return MeteringPoints(
            [MeteringPoint(**itm) for itm in response.json()["result"]]
        )

    def get_headers(self, token: str) -> dict:
        return {"accept": "application/json", "Authorization": "Bearer " + token}

    @property
    def meter_json(self) -> dict:
        return {
            "meteringPoints": {"meteringPoint": self.metering_points.metering_point_ids}
        }

    def get_timeseries_data(
        self,
        date_from: str,
        date_to: str,
        aag_level: TimeSerieAggLevels = TimeSerieAggLevels.ACTUAL,
    ) -> dict:
        return {
            "dateFrom": date_from,
            "dateTo": date_to,
            "aggregation": aag_level.value,
        }
