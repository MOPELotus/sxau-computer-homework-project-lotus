python -m disease_intel.cli run --input data/sample/outbreak_events_sample.csv --output artifacts/latest
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
