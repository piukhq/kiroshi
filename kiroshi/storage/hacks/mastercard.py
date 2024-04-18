"""Hacks for Mastercard SFTP."""

import io

from azure.storage.blob import BlobServiceClient


def _mastercard(
    blob_client: BlobServiceClient,
    blob_container: str,
    blob_directory: str,
    filename: str,
    fo: io.BytesIO,
) -> None:
    settlement_client = blob_client.get_blob_client(
        container=blob_container,
        blob=f"{blob_directory}-settlement/{filename}",
    )
    refund_client = blob_client.get_blob_client(
        container=blob_container,
        blob=f"{blob_directory}-refund/{filename}",
    )

    content = io.TextIOWrapper(fo, encoding="utf-8")
    settlement_file = io.StringIO()
    refund_file = io.StringIO()

    for line in content:
        if line[0] != "D":
            # non-data records get written to both files
            settlement_file.write(line)
            refund_file.write(line)
        else:
            # data records get written to the appropriate file based on the spend amount
            spend_amount = int(line[slice(518, 518 + 12)])
            file = settlement_file if spend_amount >= 0 else refund_file
            file.write(line)

    settlement_file.seek(0)
    settlement_client.upload_blob(settlement_file.read())
    refund_file.seek(0)
    refund_client.upload_blob(refund_file.read())
