variable "region" {
  type = string
  default = "us-east-1"
}

variable "enabled" {
  type = bool
  default = true
}

variable "ports" {
  type = list(number)
  default = [80, 443]
}

variable "settings" {
  type = object({name = string, enabled = optional(bool)})
}

variable "pair" {
  type = tuple([string, number])
}

output "payload" {
  value = {
    region = var.region
    enabled = var.enabled
    ports = var.ports
  }
}

variable "raw_payload" {
  type = any
}
