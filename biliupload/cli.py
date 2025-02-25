# Copyright (c) 2025 biliupload

import argparse
import sys
import os
import logging
from biliupload.ioer import ioer
from biliupload.login.login_bili import login_bili
from biliupload.utils.parse_cookies import parse_cookies
from biliupload.upload.bili_upload import BiliUploader
from biliupload.utils.parse_yaml import parse_yaml
from biliupload.controller.upload_controller import UploadController
from biliupload.login.check_login import CheckLogin
from biliupload.login.logout_bili import Logout
from biliupload.controller.download_controller import DownloadController

def cli():
    logging.basicConfig(
        format='[%(levelname)s] - [%(asctime)s %(name)s] - %(message)s',
        level=logging.INFO
    )
    parser = argparse.ArgumentParser(description='Python implementation of biliup')
    parser.add_argument('-V', '--version', action='version', version='biliupload 0.0.2', help='Print version information')

    subparsers = parser.add_subparsers(dest='subcommand', help='Subcommands')

    # Login subcommand
    login_parser = subparsers.add_parser('login', help='Login and save the cookie')
    login_parser.add_argument('--export', action='store_true', help='(default is false) Export the login cookie file')

    # Logout subcommand
    logout_parser = subparsers.add_parser('logout', help='Logout the current account')

    # Upload subcommand
    upload_parser = subparsers.add_parser('upload', help='Upload the video')
    upload_parser.add_argument('video_path', help='(required) The path to video file')
    upload_parser.add_argument('-y', '--yaml', default='', help='The path to yaml file(if yaml file is provided, the arguments below will be ignored)')
    upload_parser.add_argument('--copyright', type=int, default=2, help='(default is 2) 1 for original, 2 for reprint')
    upload_parser.add_argument('--title', default='', help='(default is video name) The title of video')
    upload_parser.add_argument('--desc', default='', help='(default is empty) The description of video')
    upload_parser.add_argument('--tid', type=int, default=138, help='(default is 138) For more info to the type id, refer to https://biliup.github.io/tid-ref.html')
    upload_parser.add_argument('--tag', default='biliupload', help='(default is biliupload) Video tags, separated by comma')
    upload_parser.add_argument('--line', default='bda2', help='(default is bda2) Line refer to https://biliup.github.io/upload-systems-analysis.html')
    upload_parser.add_argument('--source', default='来源于网络', help='(default is 来源于网络) The source of video (if your video is re-print)')
    upload_parser.add_argument('--cover', default='', help='(default is empty) The cover of video (if you want to customize, set it as the path to your cover image)')
    upload_parser.add_argument('--dynamic', default='', help='(default is empty) The dynamic information')

    # Check login subcommand
    check_login_parser = subparsers.add_parser('check', help='Check if the user is logged in')

    # Download subcommand
    download_parser = subparsers.add_parser('download', help='Download the video')

    download_parser.add_argument('bvid', help='(required) the bvid of video')
    download_parser.add_argument('--danmaku', action='store_true', help='(default is false) download the danmaku of video')
    download_parser.add_argument('--quality', type=int, default=64, help='(default is 64) the resolution of video')
    download_parser.add_argument('--chunksize', type=int, default=1024, help='(default is 1024) the chunk size of video')
    download_parser.add_argument('--multiple', action='store_true', help='(default is false) download the multiple videos if have set')

    args = parser.parse_args()

    # Check if no subcommand is provided
    if args.subcommand is None:
        print("No subcommand provided. Please specify a subcommand.")
        parser.print_help()
        sys.exit()

    if args.subcommand == 'login':
        login_bili(args.export)

    if args.subcommand == 'logout':
        Logout().logout_bili()

    if args.subcommand == 'upload':
        # print(args)
        if args.yaml:
            # * is used to unpack the tuple
            upload_metadata = UploadController.package_upload_metadata(*parse_yaml(args.yaml))
        else:
            upload_metadata = UploadController.package_upload_metadata(
                args.line, args.copyright, args.tid, args.title, 
                args.desc, args.tag, args.source, args.cover, args.dynamic
            )
        ioer().update_multiple_config(args.subcommand, upload_metadata)
        upload_controller = UploadController()
        upload_controller.upload_and_publish_video(args.video_path)

    if args.subcommand == 'check':
        CheckLogin().check_bili_login()

    if args.subcommand == 'download':
        # print(args)
        download_metadata = DownloadController.package_download_metadata(args.danmaku, args.quality, args.chunksize, args.multiple)
        ioer().update_multiple_config(args.subcommand, download_metadata)
        download_controller = DownloadController()
        download_controller.download_video(args.bvid)

if __name__ == '__main__':
    cli()