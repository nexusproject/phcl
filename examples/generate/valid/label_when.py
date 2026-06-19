from phcl.runtime import generate, label, this, when
from phcl.terraform import Output, Resource
from phcl.terraform import TerraformPHCL as PHCL  # noqa: N812


ENABLE_ARCHIVE_BUCKET = False

WORKLOADS = {
    "api": {
        "bucket": "phcl-example-api",
        "team": "platform",
    },
    "web": {
        "bucket": "phcl-example-web",
        "team": "frontend",
    },
}


@label("app", "logs")
class LogsBucket(Resource["aws_s3_bucket"]):
    bucket = "phcl-example-logs"
    tags = {
        "Name": "logs",
        "ManagedBy": "PHCL",
    }


@label("app", "workload")
@generate(WORKLOADS)
class WorkloadBucket(Resource["aws_s3_bucket"]):
    bucket = this.value["bucket"]
    tags = {
        "Name": this.key,
        "Label": this.label,
        "Team": this.value["team"],
        "ManagedBy": "PHCL",
    }


@when(ENABLE_ARCHIVE_BUCKET)
@label("app", "archive")
class ArchiveBucket(Resource["aws_s3_bucket"]):
    bucket = "phcl-example-archive"


class ExampleBucketIds(Output):
    value = {
        "logs": LogsBucket._.id,
        "api": WorkloadBucket._["api"].id,
        "web": WorkloadBucket._["web"].id,
    }
