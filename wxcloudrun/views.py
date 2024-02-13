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
