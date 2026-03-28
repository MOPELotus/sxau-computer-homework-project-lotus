python -m disease_intel.cli run --input materials/source --output artifacts/latest
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
