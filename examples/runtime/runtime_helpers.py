from phcl.terraform import Output
from phcl.terraform import TerraformPHCL as PHCL  # noqa: N812
from phcl.runtime import heredoc, path_module, render_file
from phcl.syntax import hcl_file


MODULE_DIR = path_module()


class ModuleDir(Output):
    value = str(MODULE_DIR)


class RenderedText(Output):
    value = render_file(
        MODULE_DIR / "message.tmpl",
        context={
            "name": "PHCL",
            "place": "runtime",
        },
        heredoc=False,
    )


class RenderedMultiline(Output):
    value = render_file(
        MODULE_DIR / "script.tmpl",
        context={
            "name": "PHCL",
        },
    )


class ManualMultiline(Output):
    value = heredoc("line one\nline two")


class NativeFile(Output):
    value = hcl_file("${path.module}/notes.txt")
