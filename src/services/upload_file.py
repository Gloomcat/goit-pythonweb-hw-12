import cloudinary
import cloudinary.uploader


class UploadFileService:
    """
    Service class for handling file uploads to Cloudinary.

    This class configures Cloudinary and provides a method to upload user files.
    """

    def __init__(self, cloud_name: str, api_key: str, api_secret: str):
        """
        Initializes the Cloudinary file upload service.

        Args:
            cloud_name (str): Cloudinary cloud name.
            api_key (str): Cloudinary API key.
            api_secret (str): Cloudinary API secret.
        """
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username: str) -> str:
        """
        Uploads a file to Cloudinary.

        The uploaded file is stored under the `RestApp/{username}` public ID.

        Args:
            file: The file object to be uploaded.
            username (str): The username associated with the file.

        Returns:
            str: The URL of the uploaded file.
        """
        public_id = f"RestApp/{username}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url
