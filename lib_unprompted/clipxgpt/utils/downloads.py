"""
    Utility functions for loading weights.
"""

import gdown


def download_weights(checkpoint_fpath, model_size="L"):
    """
    Downloads weights from Google Drive.
    """

    download_id = (
        "1pSQruQyg8KJq6VmzhMLFbT_VaHJMdlWF"
        if model_size.strip().upper() == "L"
        else "1Gh32arzhW06C1ZJyzcJSSfdJDi3RgWoG"
    )

    gdown.download(
        f"https://drive.google.com/uc?id={download_id}", checkpoint_fpath, quiet=False
    )
