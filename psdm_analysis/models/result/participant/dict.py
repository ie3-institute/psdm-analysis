import logging
from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from pandas.core.groupby import DataFrameGroupBy

from psdm_analysis.io.utils import csv_to_grpd_df, get_file_path
from psdm_analysis.models.entity import ResultEntities
from psdm_analysis.models.input.enums import EntitiesEnum, SystemParticipantsEnum


@dataclass(frozen=True)
class ResultDict(ABC):
    entity_type: EntitiesEnum
    entities: Dict[str, ResultEntities]

    def __len__(self):
        return len(self.entities)

    def __contains__(self, uuid):
        return uuid in self.entities

    def __getitem__(self, uuid):
        return self.entities[uuid]

    @staticmethod
    def get_grpd_df(
        sp_type: SystemParticipantsEnum,
        simulation_data_path: str,
        delimiter: str,
    ) -> Optional[DataFrameGroupBy]:
        file_name = sp_type.get_csv_result_file_name()
        path = get_file_path(simulation_data_path, file_name)

        if not path.exists():
            logging.info(
                "No results built for {} since {} does not exist".format(
                    file_name, str(path)
                )
            )
            return None

        return csv_to_grpd_df(file_name, simulation_data_path, delimiter)

    @staticmethod
    def safe_get_path(sp_type: SystemParticipantsEnum, data_path: str) -> Optional[str]:
        file_name = sp_type.get_csv_result_file_name()
        path = get_file_path(data_path, file_name)
        if path.exists():
            return path
        else:
            logging.info(
                "No results built for {} since {} does not exist".format(
                    file_name, str(path)
                )
            )
            return None

    @classmethod
    def create_empty(cls, sp_type):
        return cls(sp_type, dict())

    def subset(self, uuids):
        matched_participants = {
            uuid: self.entities[uuid] for uuid in self.entities.keys() & uuids
        }

        return type(self)(self.entity_type, matched_participants)

    def subset_split(self, uuids: [str]):
        """
        Returns a results result containing the given uuids and a results result containing the remaining uuids.
        :param uuids: the uuids with which to split the result
        :return:
        """

        rmd_uuids = self.entities.keys() - uuids
        return self.subset(uuids), self.subset(rmd_uuids)

    # noinspection PyArgumentList
    def filter_for_time_interval(self, start: datetime, end: datetime):
        return type(self)(
            self.entity_type,
            {
                uuid: result.filter_for_time_interval(start, end)
                for uuid, result in self.entities.items()
            },
        )
