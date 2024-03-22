from flask import Flask, request, abort, jsonify
import paho.mqtt.client as mqtt
import json
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import threading
app = Flask(__name__)

# 必須放上自己的 Channel Access Token 和 Channel Secret
line_bot_api_1 = LineBotApi('1HW5JEisgrQeGuT4CFkdpxqKUg7yBSMamvnNDjhWRkat5YbZ1Iyhca0wV51oaLWTFlZgfFMzom7p1PEpmToK7CEqD1medGIoOe9CNMEMx2avpLzjdk4oiPfjKnmspDaeWtjlwQ3z9vDzGZb5tFQYwAdB04t89/1O/w1cDnyilFU=')
line_bot_api_2 = LineBotApi('errkKdVGGSOpGQyTYB8qx34Oz5jQyjvLYiOrUHPRTRKxnj0pPBsVgUc56his6mcpE+amMWwQ5TThJ8ULQkQCJ2e0RIUz6psW9xJV5AtKqMz79uz8kFSIO/LuqbnYtqiNRVG6IMb6oC2AAZSMUxqtRgdB04t89/1O/w1cDnyilFU=')
handler_1 = WebhookHandler('f0aad20dffe66fbb3be96965801aa2fe')
handler_2 = WebhookHandler('d40c1545b1955dbbca91653e56e6b569')


# MQTT Broker 連接設置
mqtt_broker_host = "partechiiot.ddns.net"
mqtt_broker_port = 1883
mqtt_username = "bot1"
mqtt_password = "chrisli1216"


# MQTT 連接和發佈訊息的函式
def send_to_mqtt(topic, message):
    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.username_pw_set(username=mqtt_username, password=mqtt_password)
    client.connect(mqtt_broker_host, mqtt_broker_port)
    client.publish(topic, message)
    client.disconnect()
# Line Bot Webhook 處理函式

import json  # 确保导入了json模块

def on_message_1(client, userdata, msg):
    try:
        # 解析收到的消息
        try:
            received_message = msg.payload.decode('utf-8')
            print(received_message)
            print("-" * 10)
        except UnicodeDecodeError:
            # 如果 UTF-8 解码失败，尝试使用错误处理来替代无法解码的部分
            received_message = msg.payload.decode( 'Big5')
            print(received_message)
            print("*" * 10)

        print(received_message)
        print("*" * 10)
        # 解析 JSON 字符串
        received_message = json.loads(received_message)  # 使用 json.loads() 而不是 json.load()
        # 从消息中提取 user_id 和 message
        
        message_text = received_message["message"]
        user_id = received_message["user_id"]
        if isinstance(user_id,str):
            user_ids =[user_id]
        else:
            user_ids = user_id
        for user_id in user_ids:
            if user_id is not None:
                # 使用 Line Bot API 发送消息
                line_bot_api_1.push_message(user_id, messages=TextSendMessage(text=message_text))
    except Exception as e:
        print(f"Error: {e}")


def on_message_2(client, userdata, msg):
    try:
        # 解析收到的消息
        try:
            received_message = msg.payload.decode('utf-8')
            print(received_message)
            print("-" * 10)
        except UnicodeDecodeError:
            # 如果 UTF-8 解码失败，尝试使用错误处理来替代无法解码的部分
            received_message = msg.payload.decode( 'Big5')
            print(received_message)
            print("*" * 10)

        print(received_message)
        print("*" * 10)
        # 解析 JSON 字符串
        received_message = json.loads(received_message)  # 使用 json.loads() 而不是 json.load()
        # 从消息中提取 user_id 和 message
        message_text = received_message["message"]
        user_id = received_message["user_id"]
        if isinstance(user_id,str):
            user_ids =[user_id]
        else:
            user_ids = user_id
        for user_id in user_ids:
            if user_id is not None:
                # 使用 Line Bot API 发送消息
                line_bot_api_2.push_message(user_id, messages=TextSendMessage(text=message_text))
    except Exception as e:
        print(f"Error: {e}")


@handler_1.add(MessageEvent, message=TextMessage)
def webhook_handler_1(event):
    user_id = event.source.user_id
    message_text = event.message.text
    # send_to_mqtt("IIOT/linenot/JS", json.dumps({"user_id": user_id, "message": message_text}))
    return "Message forwarded to MQTT Broker."


@handler_2.add(MessageEvent, message=TextMessage)
def webhook_handler_2(event):
    user_id = event.source.user_id
    message_text = event.message.text
    # send_to_mqtt("IIOT/linebot/lt", json.dumps({"user_id": user_id, "message": message_text}))
    return "Message forwarded to MQTT Broker."

def mqtt_listen_1():
    # Create MQTT client instance
    print("_________________________________________________________")
    client = mqtt.Client()
    
    # Set message receive callback function
    client.on_message = on_message_1
    
    # Connect to MQTT server
    broker_address = "partechiiot.ddns.net"
    client.connect(broker_address, 1883, 60)

    # Subscribe to topic
    topic = "IIOT/linenot/JS"
    client.subscribe(topic)

    # Start MQTT client loop to receive messages
    client.loop_forever()

def mqtt_listen_2():
    # Create MQTT client instance
    client = mqtt.Client()

    # Set message receive callback function
    client.on_message = on_message_2
    print(client.message_callback)
    # Connect to MQTT server
    broker_address = "partechiiot.ddns.net"
    client.connect(broker_address, 1883, 60)

    # Subscribe to topic
    topic = "IIOT/linebot/lt"
    client.subscribe(topic)

    # Start MQTT client loop to receive messages
    client.loop_forever()


@app.route("/callback", methods=["POST"])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler_1.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@app.route("/callbook", methods=["POST"])
def callbook():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler_2.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

if __name__ == "__main__":
    # 创建线程并运行 mqtt_listen() 函数
    mqtt_thread_1 = threading.Thread(target=mqtt_listen_1, daemon=True)
    mqtt_thread_1.start()

    mqtt_thread_2 = threading.Thread(target=mqtt_listen_2, daemon=True)
    mqtt_thread_2.start()

    # 运行 Flask 应用
    port = 8000
    app.run(host='0.0.0.0', port=port)