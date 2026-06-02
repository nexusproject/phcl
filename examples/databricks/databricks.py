from phcl.terraform import TerraformPHCL as PHCL  # noqa: N812
from phcl.syntax import hcl_jsonencode
from phcl.terraform import Data, Output, Provider, Resource, Variable
from phcl.types import STRING


class DatabricksHost(Variable):
    type = STRING


class DatabricksToken(Variable):
    type = STRING
    sensitive = True


class TeamName(Variable):
    type = STRING
    default = "data-platform"


class Databricks(Provider["databricks"]):
    host = DatabricksHost._
    token = DatabricksToken._


class WorkspaceGroup(Data["databricks_group"]):
    display_name = TeamName._


class WorkspaceClusterPolicy(Resource["databricks_cluster_policy"]):
    name = "shared-jobs"
    definition = hcl_jsonencode(
        {
            "dbus_per_hour": {
                "type": "range",
                "maxValue": 10,
            }
        }
    )


class TeamEntitlements(Resource["databricks_group_role"]):
    group_id = WorkspaceGroup._.id
    role = "users"


class GroupId(Output):
    value = WorkspaceGroup._.id
