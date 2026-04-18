from .build import BuildResult, command_build, compile_file, discover_python_files, output_path_for
from .config import DEFAULT_OUTPUT_EXTENSION, FileConfig, load_file_config, normalize_extension
from .loading import clear_module_tree, execute_file, execute_module, is_valid_module_part, resolve_module_target
from .main import build_parser, main
from .ui import Ansi, NO_COLOR, heading, paint, print_group_heading, print_result, status_word, use_color


if __name__ == "__main__":
    raise SystemExit(main())
