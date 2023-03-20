import os
import boto3
import peewee

class UploadedFile(peewee.Model):
    file_path = peewee.CharField()
    destination_path = peewee.CharField(null=True)
    is_attachment = peewee.BooleanField(default=False)
    file_url = peewee.CharField(null=True)

    class Meta:
        database = 'your_database_instance'

    def upload_to_digitalocean(self):
        s3 = boto3.resource(
            's3',
            endpoint_url=self.your_digitalocean_endpoint_url,
            region_name=self.your_digitalocean_region,
            aws_access_key_id=self.your_digitalocean_access_key_id,
            aws_secret_access_key=self.your_digitalocean_secret_access_key
        )

        if self.destination_path:
            obj = s3.Bucket(self.your_digitalocean_bucket).Object(self.destination_path)
        else:
            file_name = os.path.basename(self.file_path)
            obj_key = os.path.join('uploads', self.id, file_name)
            obj = s3.Bucket(self.your_digitalocean_bucket).Object(obj_key)

        upload_params = {'ACL': 'public-read'}
        if self.is_attachment:
            upload_params['ContentDisposition'] = 'attachment'
        obj.upload_file(self.file_path, ExtraArgs=upload_params)

        self.file_url = obj.public_url
        self.save()
