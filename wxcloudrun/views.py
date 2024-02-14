from datetime import datetime
from flask import render_template, request
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.model import Counters
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response

from flask import Flask, request, jsonify
import os
import requests
import logging

from flask import Flask, request, jsonify
import requests
from pathlib import Path
from openai import OpenAI  # 假设这是一个示例类，根据您的实际API客户端进行调整

from flask import Flask, request, jsonify
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tcb.v20180608 import tcb_client, models


app = Flask(__name__)

# 配置日志记录
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    """
    :return: 返回index页面
    """
    return render_template('index.html')


@app.route('/api/count', methods=['POST'])
def count():
    """
    :return:计数结果/清除结果
    """

    # 获取请求体参数
    params = request.get_json()

    # 检查action参数
    if 'action' not in params:
        return make_err_response('缺少action参数')

    # 按照不同的action的值，进行不同的操作
    action = params['action']

    # 执行自增操作
    if action == 'inc':
        counter = query_counterbyid(1)
        if counter is None:
            counter = Counters()
            counter.id = 1
            counter.count = 1
            counter.created_at = datetime.now()
            counter.updated_at = datetime.now()
            insert_counter(counter)
        else:
            counter.id = 1
            counter.count += 1
            counter.updated_at = datetime.now()
            update_counterbyid(counter)
        return make_succ_response(counter.count)

    # 执行清0操作
    elif action == 'clear':
        delete_counterbyid(1)
        return make_succ_empty_response()

    # action参数错误
    else:
        return make_err_response('action参数错误')


@app.route('/api/count', methods=['GET'])
def get_count():
    """
    :return: 计数的值
    """
    counter = Counters.query.filter(Counters.id == 1).first()
    return make_succ_response(0) if counter is None else make_succ_response(counter.count)


@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    app.logger.info('1231235656223')

    download_url = request.json.get('downloadUrl')
    if not download_url:
        app.logger.error('Missing download URL')
        return "Missing download URL", 400

    app.logger.info(f'Received download URL: {download_url}')

    try:
        response = requests.get(download_url, timeout=3000)  # 设置超时时间
        if response.status_code == 200:
            local_path = 'tmp/downloaded_file.pdf'
            with open(local_path, 'wb') as f:
                f.write(response.content)
            app.logger.info(f'PDF downloaded successfully. Local path: {local_path}')
            return f"PDF downloaded successfully. Local path: {local_path}"
        else:
            app.logger.error(f'Failed to download PDF. HTTP status code: {response.status_code}')
            return "Failed to download PDF", 500
    except requests.RequestException as e:
        app.logger.error(f'Error downloading PDF: {str(e)}')
        return "Error downloading PDF", 500


# 初始化API客户端（根据您的实际情况进行调整）
client = OpenAI(
    api_key="Y2xlNTY0a2JidmRqa2ZqazU3dDA6bXNrLUNSN0dGVmU0UHJvUzlialpGZnVjTzJud3FrNU0=",
    base_url="https://api.example.com/v1",
)


@app.route('/uploadPdf', methods=['POST'])
def upload_pdf():
    app.logger.info('1231235656223')

    data = request.get_json()
    download_url = data.get('downloadUrl')

    if not download_url:
        return jsonify({'error': 'Missing download URL'}), 400

    # 下载文件的本地保存路径
    local_path = Path("downloaded_file.pdf")

    try:
        # 下载文件
        response = requests.get(download_url)
        if response.status_code == 200:
            # 保存下载的文件
            local_path.write_bytes(response.content)

            # 上传文件到API服务
            # 注意：这里假设client.files.create接受本地文件路径，根据实际API调整
            file_object = client.files.create(file=local_path, purpose="file-extract")

            # 假设上传成功后的处理，根据您的需求调整
            return jsonify(
                {'message': 'PDF downloaded and uploaded successfully', 'file_object': str(file_object)}), 200
        else:
            return jsonify({'error': 'Failed to download the file from URL'}), 500
    except requests.RequestException as e:
        return jsonify({'error': f'Error downloading PDF: {str(e)}'}), 500

@app.route('/api/upload', methods=['POST'])
def upload_pdf():
    app.logger.info('1238885523')

    file_id = request.json.get('fileID')
    try:
        # 假设你已经设置了环境变量或者在这里直接填写你的SecretId和SecretKey
        cred = credential.Credential("你的SecretId", "你的SecretKey")
        client = tcb_client.TcbClient(cred, "你的区域")
        req = models.DownloadFileRequest()
        req.FileID = file_id
        response = client.DownloadFile(req)
        print(response.FileContent)  # 这里是文件内容
        # 根据需要处理文件，比如保存到本地
        file_path = "/path/to/save/" + file_id.split('/')[-1] + ".pdf"
        with open(file_path, 'wb') as f:
            f.write(response.FileContent)
        return jsonify({"message": "文件处理成功", "path": file_path})
    except TencentCloudSDKException as err:
        print(err)
        return jsonify({"error": "处理失败"}), 500

@app.route('/download', methods=['POST'])
def download_file():
    app.logger.info('1238568992231223')

    # 从POST请求的JSON体中获取文件的临时链接
    file_url = request.json.get('fileUrl')
    if not file_url:
        return jsonify({'error': 'Missing file URL'}), 400

    # 提取文件名并定义保存路径
    file_name = file_url.split('/')[-1]
    save_path = file_name  # 直接使用文件名作为保存路径，将文件保存在当前目录

    try:
        # 使用requests下载文件
        response = requests.get(file_url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            return jsonify({'message': 'File downloaded successfully', 'path': save_path})
        else:
            return jsonify({'error': 'Failed to download file'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=False)