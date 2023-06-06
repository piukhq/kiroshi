# Kiroshi

TODO: Actually Write some docs

## SFTP

### Mastercard

Mastercard must be configured in one of the following config matrices, else Harmonia will get sad:

```json
{
    "TGX4": {
        "sftp_host": "mtf.files.mastercard.com",
        "sftp_port": 16022,
        "sftp_user": "Z218502",
        "sftp_dir": "/0073185/test/download/TGX4",
        "blob_container": "harmonia-imports",
        "blob_dir": "test/mastercard-settlement",
    },
    "TGX2": {
        "sftp_host": "files.mastercard.com",
        "sftp_port": 16022,
        "sftp_user": "Z216458",
        "sftp_dir": "/0073185/production/download/TGX2",
        "blob_container": "harmonia-imports",
        "blob_dir": "mastercard",
    },
    "TS44": {
        "sftp_host": "files.mastercard.com",
        "sftp_port": 16022,
        "sftp_user": "Z218502",
        "sftp_dir": "/0073185/production/download/TS44",
        "blob_container": "harmonia-imports",
        "blob_dir": "payment/mastercard",
    },
}
```
