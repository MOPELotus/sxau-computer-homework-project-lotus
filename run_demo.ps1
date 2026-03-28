python -m disease_intel.cli run --input "materials/source/全格式示例包" --output artifacts/latest
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
