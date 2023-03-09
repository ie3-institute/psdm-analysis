from dataclasses import dataclass
from datetime import datetime
from typing import Set

from psdm_analysis.io.utils import check_filter
from psdm_analysis.models.result.grid.node import NodesResult
from psdm_analysis.models.result.participant.participants_res_container import (
    ParticipantsResultContainer,
)


@dataclass(frozen=True)
class ResultContainer:
    name: str
    nodes: NodesResult
    participants: ParticipantsResultContainer

    def __len__(self):
        return len(self.nodes) + len(self.participants)

    # todo: implement slicing
    def __getitem__(self, slice_val):
        pass

    @classmethod
    def from_csv(
        cls,
        name: str,
        simulation_data_path: str,
        delimiter: str,
        simulation_end: datetime = None,
        from_agg_results: bool = True,
        filter_start: datetime = None,
        filter_end: datetime = None,
    ):
        check_filter(filter_start, filter_end)
        # todo: load async
        nodes = NodesResult.from_csv(
            simulation_data_path,
            delimiter,
            simulation_end,
            filter_start=filter_start,
            filter_end=filter_end,
        )

        if simulation_end is None:
            some_node_res = next(iter(nodes.nodes.values()))
            # todo: this only works if we can guarantee order
            simulation_end = some_node_res.data.iloc[-1].name

        participants = ParticipantsResultContainer.from_csv(
            simulation_data_path,
            delimiter,
            simulation_end,
            from_agg_results=from_agg_results,
            filter_start=filter_start,
            filter_end=filter_end,
        )

        return cls(name, nodes, participants)

    def uuids(self) -> set[str]:
        return set(self.nodes.nodes.keys())

    # todo: implement
    def filter_by_nodes(self, nodes: Set[str]):
        pass

    def filter_for_time_interval(self, start: datetime, end: datetime):
        return ResultContainer(
            self.name,
            self.nodes.filter_for_time_interval(start, end),
            self.participants.filter_for_time_interval(start, end),
        )
