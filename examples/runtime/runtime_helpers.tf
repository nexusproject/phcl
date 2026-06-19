output "module_dir" {
  value = "/Users/dvm/WORK/PHCL/phcl/examples/runtime"
}

output "rendered_text" {
  value = "hello PHCL from runtime"
}

output "rendered_multiline" {
  value = <<-EOF
#!/usr/bin/env bash
echo "hello PHCL"
EOF
}

output "manual_multiline" {
  value = <<-EOF
line one
line two
EOF
}

output "native_file" {
  value = file("${path.module}/notes.txt")
}
