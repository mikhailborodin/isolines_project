import os
from django.test import TestCase
from django.urls import reverse
from .models import UploadedFile
from django.conf import settings


class IsolineGenerationTestCase(TestCase):
    def setUp(self):
        self.uploaded_file = None
        self.base_path = settings.BASE_DIR

    def test_upload_file(self):
        # Test file upload functionality
        source_path = os.path.join(self.base_path, 'isolines_app/fixtures/sample.geojson')
        with open(source_path, 'rb') as file:
            response = self.client.post(reverse('upload_file'), {'file': file})

        # Check if the file was uploaded successfully
        self.assertEqual(response.status_code, 302)  # Check for a redirect status code

        # Verify the uploaded file is stored in the database
        uploaded_files_count = UploadedFile.objects.count()
        self.assertEqual(uploaded_files_count, 1)  # Check if one file is uploaded

        uploaded_file = UploadedFile.objects.first()
        self.assertIn('uploads/sample', uploaded_file.file.path) # Check the file path
        self.uploaded_file = uploaded_file

    def test_isoline_generation(self):
        # Test isoline generation functionality
        # Create test data or mock the necessary objects
        source_path = os.path.join(self.base_path, 'isolines_app/fixtures/sample.geojson')
        with open(source_path, 'rb') as file:
            self.client.post(reverse('upload_file'), {'file': file})

        # Make a POST request to the API endpoint
        response = self.client.get(reverse('api_endpoint_url'))

        # Check if the response is successful
        self.assertEqual(response.status_code, 200)  # Check for a successful status code

        # Validate the response data
        response_data = response.json()
        # Add your assertions to validate the generated isolines

        # Add more test cases for different scenarios as needed

    def tearDown(self):
        # Clean up any test data or objects created during the tests
        pass
