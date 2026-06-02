variable "databricks_host" {
  type = string
}

variable "databricks_token" {
  type = string
  sensitive = true
}

variable "team_name" {
  type = string
  default = "data-platform"
}

provider "databricks" {
  host = var.databricks_host
  token = var.databricks_token
}

data "databricks_group" "workspace_group" {
  display_name = var.team_name
}

resource "databricks_cluster_policy" "workspace_cluster_policy" {
  name = "shared-jobs"
  definition = jsonencode({dbus_per_hour = {type = "range", maxValue = 10}})
}

resource "databricks_group_role" "team_entitlements" {
  group_id = data.databricks_group.workspace_group.id
  role = "users"
}

output "group_id" {
  value = data.databricks_group.workspace_group.id
}
