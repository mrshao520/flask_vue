import datetime
import logging as rel_log
import os
import shutil
from datetime import timedelta
from flask import *


UPLOAD_FOLDER = r'./uploads'

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'bmp'])
app = Flask(__name__)
app.secret_key = 'secret!'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

werkzeug_logger = rel_log.getLogger('werkzeug')
werkzeug_logger.setLevel(rel_log.ERROR)

# 解决缓存刷新问题
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)


# 添加header解决跨域
@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'
    return response


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/')
def hello_world():
    return redirect(url_for('static', filename='./index.html'))


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    # 获取上传图片的文件名
    file = request.files['file']
    print(datetime.datetime.now(), file.filename)
    # 判断图片后缀是否符合要求格式
    if file and allowed_file(file.filename):
        # 文件保存路径
        src_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        print(f'src_path : {src_path}')
        # 保存图片
        file.save(src_path)
        # 拷贝图片到 /tmp/ct 路径下
        shutil.copy(src_path, './tmp')
        image_path = os.path.join('./tmp', file.filename)
        
        # 处理
        pic_name = 'untitled.png'
    
        return jsonify({'status': 1,
                        'image_url': 'http://127.0.0.1:5003/tmp/' + file.filename,
                        'draw_url': 'http://127.0.0.1:5003/tmp/' + pic_name,
                        'image_info': ''})

    return jsonify({'status': 0})


# show photo  页面获取图片
@app.route('/tmp/<path:file>', methods=['GET'])
def show_photo(file):
    if request.method == 'GET':
        if not file is None:
            image_data = open(f'tmp/{file}', "rb").read()
            response = make_response(image_data)
            response.headers['Content-Type'] = 'image/png'
            return response


if __name__ == '__main__':
    files = [
        'uploads', 'tmp'
    ]
    for ff in files:
        if not os.path.exists(ff):
            os.makedirs(ff)
    app.run(host='127.0.0.1', port=5003, debug=True)
