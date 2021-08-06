"""CDL dataset."""

import os
from typing import Any, Callable, Dict, Optional

from rasterio.crs import CRS

from .geo import RasterDataset
from .utils import check_integrity, download_and_extract_archive


class CDL(RasterDataset):
    """Cropland Data Layer (CDL) dataset.

    The `Cropland Data Layer
    <https://data.nal.usda.gov/dataset/cropscape-cropland-data-layer>`_, hosted on
    `CropScape <https://nassgeodata.gmu.edu/CropScape/>`_, provides a raster,
    geo-referenced, crop-specific land cover map for the continental United States. The
    CDL also includes a crop mask layer and planting frequency layers, as well as
    boundary, water and road layers. The Boundary Layer options provided are County,
    Agricultural Statistics Districts (ASD), State, and Region. The data is created
    annually using moderate resolution satellite imagery and extensive agricultural
    ground truth.

    If you use this dataset in your research, please cite it using the following format:

    * https://www.nass.usda.gov/Research_and_Science/Cropland/sarsfaqs2.php#Section1_14.0
    """  # noqa: E501

    filename_glob = "*_30m_cdls.*"
    filename_regex = r"""
        ^(?P<date>\d+)
        _30m_cdls\..*$
    """
    date_format = "%Y"
    is_image = False

    url = "https://www.nass.usda.gov/Research_and_Science/Cropland/Release/datasets/{}_30m_cdls.zip"  # noqa: E501
    md5s = [
        (2020, "97b3b5fd62177c9ed857010bca146f36"),
        (2019, "49d8052168c15c18f8b81ee21397b0bb"),
        (2018, "c7a3061585131ef049bec8d06c6d521e"),
        (2017, "dc8c1d7b255c9258d332dd8b23546c93"),
        (2016, "bb4df1b2ee6cedcc12a7e5a4527fcf1b"),
        (2015, "d17b4bb6ee7940af2c45d6854dafec09"),
        (2014, "6e0fcc800bd9f090f543104db93bead8"),
        (2013, "38df780d8b504659d837b4c53a51b3f7"),
        (2012, "2f3b46e6e4d91c3b7e2a049ba1531abc"),
        (2011, "dac7fe435c3c5a65f05846c715315460"),
        (2010, "18c9a00f5981d5d07ace69e3e33ea105"),
        (2009, "81a20629a4713de6efba2698ccb2aa3d"),
        (2008, "e6aa3967e379b98fd30c26abe9696053"),
    ]

    def __init__(
        self,
        root: str = "data",
        crs: Optional[CRS] = None,
        res: Optional[float] = None,
        transforms: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
        download: bool = False,
        checksum: bool = False,
    ) -> None:
        """Initialize a new Dataset instance.

        Args:
            root: root directory where dataset can be found
            crs: :term:`coordinate reference system (CRS)` to warp to
                (defaults to the CRS of the first file found)
            res: resolution of the dataset in units of CRS
                (defaults to the resolution of the first file found)
            transforms: a function/transform that takes an input sample
                and returns a transformed version
            download: if True, download dataset and store it in the root directory
            checksum: if True, check the MD5 of the downloaded files (may be slow)

        Raises:
            FileNotFoundError: if no files are found in ``root``
            RuntimeError: if ``download=False`` but dataset is missing or checksum fails
        """
        self.root = root
        self.checksum = checksum

        if download:
            self._download()

        if not self._check_integrity():
            raise RuntimeError(
                "Dataset not found or corrupted. "
                + "You can use download=True to download it"
            )

        super().__init__(root, crs, res, transforms)

    def _check_integrity(self) -> bool:
        """Check integrity of dataset.

        Returns:
            True if dataset files are found and/or MD5s match, else False
        """
        for year, md5 in self.md5s:
            filepath = os.path.join(self.root, "{}_30m_cdls.zip".format(year))
            if not check_integrity(filepath, md5 if self.checksum else None):
                return False
        return True

    def _download(self) -> None:
        """Download the dataset and extract it."""
        if self._check_integrity():
            print("Files already downloaded and verified")
            return

        for year, md5 in self.md5s:
            download_and_extract_archive(
                self.url.format(year),
                self.root,
                md5=md5 if self.checksum else None,
            )
