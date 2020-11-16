import boto3
import os
import tkinter
from tkinter import filedialog as fileselector
from imghdr import what as check_file_image_type
import time

s3_service_name = "s3"
region_name = "eu-west-1"
bucket_name = "cwkimgbucket"
script_run_dir = os.path.dirname(os.path.realpath(__file__))

s3 = boto3.resource("s3")
s3_client = boto3.client(s3_service_name, region_name=region_name)

def run():
    exit = False

    while not exit:
        option_one = "1 - Upload a selected image to a selected bucket"
        option_two = "2 - Download a selected image from a selected bucket"
        option_three = "3 - Exit application"
        application_menu = "\n{}\n{}\n{}\n".format(option_one, option_two, option_three)
        print(application_menu)
        selected_option = input("Select an application menu option (1,2,3):")
        
        if selected_option == "1":
            upload_image()
        elif selected_option == "2":
            download_image()
        elif selected_option == "3": 
            exit = True
            print("exiting application...")
        else:
            print("input {} is invalid, please choose from the option selection menu"\
                .format(selected_option))
        
""" Functionality """
def upload_image():
    image_for_upload = get_image_for_upload()

    image_for_upload_name = os.path.basename(os.path.normpath(image_for_upload))
    
    bucket_select_msg = "image upload"
    bucket_selected = get_s3_bucket(bucket_select_msg)
    
    s3_client.upload_file(image_for_upload, bucket_selected, image_for_upload_name)
    print("Uploaded image {} to bucket {}".format(image_for_upload_name, bucket_selected))

def download_image():
    bucket_select_msg = "image download"
    bucket_selected = get_s3_bucket(bucket_select_msg)
    download_images_dir = "downloaded_images"
    download_path = "{}/{}".format(script_run_dir, download_images_dir)

    bucket = s3.Bucket(bucket_selected)

    file_get_success = False

    bucket_files = list(bucket.objects.all())
    while file_get_success == False:
        file_no_shown = 1
        for img_file in bucket_files:
            print("file number: {} file name: {}".format(file_no_shown, img_file.key))
            file_no_shown += 1

        select_image_no_str = input("Select an image for download (1,2,3 etc.):")

        if not select_image_no_str.isdecimal() or int(select_image_no_str) > len(bucket_files):
            print("error, input {} is invalid. Please enter a valid file number".format(select_image_no_str))
            continue

        select_image_no = int(select_image_no_str) - 1
        selected_image = bucket_files[select_image_no].key

        filepath_for_store = "{}/{}".format(download_path, selected_image)
        file_get_success = True


    bucket.download_file(selected_image, filepath_for_store)

""" Utility functions"""    
def get_s3_bucket(bucket_select_msg : str):
    response = s3_client.list_buckets()
    buckets_to_select = list()
    bucket_get_success = False
    bucket_selected = None

    while bucket_get_success == False:
        buckets_shown = 1

        for bucket in response["Buckets"]:
            bucket_name = bucket["Name"]
            print("bucket {} name: {}".format(str(buckets_shown), bucket_name))
            buckets_to_select.append(bucket_name)
            buckets_shown += 1

        selected_bucket_no_str = input("select a bucket for {} through bucket number input (1,2,3 etc.):".format(bucket_select_msg))
        
        if not selected_bucket_no_str.isdecimal() or int(selected_bucket_no_str) > len(buckets_to_select) - 1:
             print("error, input {} is invalid. Please enter a valid bucket number".format(selected_bucket_no_str))
        else:
            selected_bucket_no = int(selected_bucket_no_str) - 1
            bucket_selected = buckets_to_select[int(selected_bucket_no)]
            bucket_get_success = True

    return bucket_selected

def get_image_for_upload():
    # Hide tkinter root window when getting file.
    tk_gui = tkinter.Tk()
    tk_gui.withdraw()
    file_select_success = False

    while not file_select_success:
        # Get user to select a file.
        path_to_selected_file = fileselector.askopenfilename()
        
        # Check the selected file is an image.
        try:
            file_is_image = check_file_image_type(path_to_selected_file) != None
        except:
            print("Error occured when selecting file, try again.")
             # Wait 500 ms to allow the user to read the error message.
            time.sleep(0.5)
            continue

        if not file_is_image:
            print("Only image files should be selected for upload. Please select again.")
            # Wait 500 ms to allow the user to read the error message.
            time.sleep(0.5)
        else:
            file_select_success = True
    
    return path_to_selected_file

run()