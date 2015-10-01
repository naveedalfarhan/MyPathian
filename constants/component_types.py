ENERGY_POINT = "EnergyPoint"
CALCULATED_POINT = "CalculatedPoint"
POSITION_POINT = "PositionPoint"
NUMERIC_POINT = "NumericPoint"
BINARY_POINT = "BinaryPoint"

ACCEPTANCE_REQUIREMENT = "AcceptanceRequirement"
COMMISSIONING_REQUIREMENT = "CommissioningRequirement"
CONTROL_SEQUENCE = "ControlSequence"
DEMAND_RESPONSE = "DemandResponse"
FUNCTION_TEST = "FunctionalTest"
LOAD_CURTAILMENT = "LoadCurtailment"
MAINTENANCE_REQUIREMENT = "MaintenanceRequirement"
ISSUE = "Issue"
PROJECT_REQUIREMENT = "ProjectRequirement"
RESPONSIBILITY = "Responsibility"
TASK = "Task"

_paragraph_map = {
    ACCEPTANCE_REQUIREMENT: "AR",
    COMMISSIONING_REQUIREMENT: "CR",
    CONTROL_SEQUENCE: "CS",
    DEMAND_RESPONSE: "DR",
    FUNCTION_TEST: "FT",
    LOAD_CURTAILMENT: "LC",
    MAINTENANCE_REQUIREMENT: "MR",
    ISSUE: "CI",
    PROJECT_REQUIREMENT: "PR",
    RESPONSIBILITY: "RR",
    TASK: "CT"
}

_point_map = {
    ENERGY_POINT: "EP",
    CALCULATED_POINT: "CP",
    POSITION_POINT: "PP",
    NUMERIC_POINT: "NP",
    BINARY_POINT: "BP"
}

valid_paragraph_types = _paragraph_map.values()
valid_point_types = _point_map.values()


def get_paragraph_prefix(paragraph_type):
    return _paragraph_map[paragraph_type]


def get_point_prefix(point_type):
    return _point_map[point_type]