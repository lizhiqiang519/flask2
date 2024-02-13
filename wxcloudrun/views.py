from datetime import datetime
from flask import render_template, request, jsonify
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.model import Counters
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response

from flask import Flask, request, jsonify
import os
import requests
import logging

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


@app.route('/file_extraction_and_chat_completion', methods=['POST'])
def file_extraction_and_chat_completion():
    app.logger.info("Received a new request for file extraction and chat completion")

    data = request.json
    fileID = data.get('fileID')

    if not fileID:
        app.logger.error("No fileID provided in the request")
        return jsonify({"error": "No fileID provided"})

    app.logger.info(f"Attempting to get download URL for fileID: {fileID}")
    download_url = get_download_url(fileID)

    if not download_url:
        app.logger.error(f"Failed to get download URL for fileID: {fileID}")
        return jsonify({"error": "Failed to get download URL"})

    app.logger.info(f"Downloading file from URL: {download_url}")
    response = requests.get(download_url)

    if response.status_code != 200:
        app.logger.error(f"Failed to download file from URL: {download_url}")
        return jsonify({"error": "Failed to download file"})

    temp_path = f'/tmp/{os.path.basename(download_url)}'
    app.logger.info(f"Saving downloaded file to temporary path: {temp_path}")

    with open(temp_path, 'wb') as temp_file:
        temp_file.write(response.content)

    app.logger.info("Extracting content from the PDF using OpenAI")
    extracted_content = extract_content_with_openai(temp_path)

    app.logger.info("Cleaning up: removing temporary file")
    os.remove(temp_path)

    app.logger.info("Returning extracted content to the client")
    return jsonify({"extractedContent": extracted_content})


def get_download_url(fileID):
    # Placeholder for actual implementation
    app.logger.debug(f"Mocking download URL retrieval for fileID: {fileID}")
    return "https://example.com/path/to/file"


def extract_content_with_openai(file_path):
    # Placeholder for actual implementation
    app.logger.debug(f"Mocking content extraction for file at: {file_path}")
    return "Extracted content here"

@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    app.logger.info('1231235656223')

    download_url = request.json.get('downloadUrl')
    if not download_url:
        app.logger.error('Missing download URL')
        return "Missing download URL", 400

    app.logger.info(f'Received download URL: {download_url}')

    try:
        response = requests.get(download_url, timeout=30)  # 设置超时时间
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