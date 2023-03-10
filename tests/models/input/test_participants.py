import os

from psdm_analysis.models.input.enums import SystemParticipantsEnum
from psdm_analysis.models.input.participant.wec import WindEnergyConverters
from tests import utils

wecs = WindEnergyConverters.from_csv(
    utils.VN_SIMONA_INPUT_PATH, utils.VN_SIMONA_DELIMITER
)
assert len(wecs) == 2


def test_sp_enum():
    bm = SystemParticipantsEnum.BIOMASS_PLANT
    pv = SystemParticipantsEnum.PHOTOVOLTAIC_POWER_PLANT
    assert bm.has_type() is True
    assert pv.has_type() is False


def test_filter_for_node():
    filtered = wecs.filer_for_node("401f37f8-6f2c-4564-bc78-6736cb9cbf8d")
    assert len(filtered) == 1


def test_subset():
    subset = wecs.subset(["d6ad8c73-716a-4244-9ae2-4a3735e492ab", "not_in_df"])
    assert len(subset) == 1


def test_to_csv():
    path = os.path.join(utils.TEMP_DIR, "wecs")
    os.makedirs(path, exist_ok=True)
    wecs.to_csv(path, utils.VN_SIMONA_DELIMITER)
    wecs2 = WindEnergyConverters.from_csv(path, utils.VN_SIMONA_DELIMITER)
    # todo this needs to be tested for other participants
    assert (wecs.data.index.sort_values() == wecs2.data.index.sort_values()).all()
    assert (wecs.data.columns.sort_values() == wecs2.data.columns.sort_values()).all()
    assert (
        wecs.data.sort_index()
        .sort_index(axis=1)
        .equals(wecs2.data.sort_index().sort_index(axis=1))
    )
