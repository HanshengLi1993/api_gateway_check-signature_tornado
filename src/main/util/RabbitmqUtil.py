# -*- coding:utf-8 -*-
import pika
from .LogUtil import *


class RabbitmqProducer:
    """
    RabbitMQ消息发布工具
    """

    def __init__(self, host, port, user, password, exchangeName, queueName, routeKey):
        self.__rabbitmq_host = host
        self.__rabbitmq_port = port
        self.__rabbitmq_user = user
        self.__rabbitmq_password = password
        self.__exchangeName = exchangeName
        self.__queueName = queueName
        self.__routeKey = routeKey
        self.__logger = LogUtil()

    def init_conn(self, data_key):
        conn_broker = None
        try:
            credentials = pika.PlainCredentials(
                self.__rabbitmq_user, self.__rabbitmq_password)
            conn_params = pika.ConnectionParameters(
                self.__rabbitmq_host, self.__rabbitmq_port, credentials=credentials)
            conn_broker = pika.BlockingConnection(conn_params)
            # 创建虚拟连接channel
            cha = conn_broker.channel()
            cha.confirm_delivery()
            # 创建队列anheng,durable参数为真时，队列将持久化；exclusive为真时，建立临时队列
            result = cha.queue_declare(
                queue=self.__queueName, durable=True, exclusive=False,
                arguments={'x-expires': 604800000}  # 队列中的消息存活时间是7天
            )
            # result.method.message_count队列消息数量
            # 创建名为yanfa,类型为fanout的exchange，其他类型还有direct和topic，如果指定durable为真，exchange将持久化
            cha.exchange_declare(
                durable=True,
                exchange=self.__exchangeName,
                exchange_type='topic',
            )

            # 绑定exchange和queue,result.method.queue获取的是队列名称
            # cha.queue_bind(exchange=self.exchangeName, queue=result.method.queue, routing_key=self.routeKey, )
            cha.queue_bind(
                exchange=self.__exchangeName,
                queue=result.method.queue,
                routing_key=self.__routeKey +
                            "." +
                            data_key,
            )
            # 公平分发，使每个consumer在同一时间最多处理一个message，收到ack前，不会分配新的message
            cha.basic_qos(prefetch_count=1)
            return conn_broker, cha
        except Exception as e:
            if conn_broker:
                conn_broker.close()
            error = "rabbitmq initialize fail " + str(e)
            self.__logger.error(error)
            raise Exception(error)

    def message_publish(self, message, conn_broker, channel, data_key):
        """
        # 发送信息到队列‘anheng'
        message = ' '.join(sys.argv[:])
        # 消息持久化指定delivery_mode=；
        cha.basic_publish(exchange='', routing_key='anheng', body=message, properties=pika.BasicProperties(delivery_mode=2, ))
        # 关闭连接
        conn_broker.close()
        """
        try:

            ack = channel.basic_publish(
                exchange=self.__exchangeName,
                routing_key=self.__routeKey + "." + data_key,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2))
            if ack:
                # print("put message to rabbitmq successed!")
                pass
            else:
                # print("put message to rabbitmq failed")
                self.__logger.info("put message to rabbitmq failed")
                self.message_publish(message, conn_broker, channel, data_key)
        except Exception as e:
            error = "rabbitmq publish message fail " + str(e)
            self.__logger.error(error)
            raise Exception(error)
        finally:
            conn_broker.close()


class RabbitmqSubscriber:
    """
    RabbitMQ消息订阅工具
    """

    def __init__(self, host, port, user, password, exchangeName, queueName):
        self.__rabbitmq_host = host
        self.__rabbitmq_port = port
        self.__rabbitmq_user = user
        self.__rabbitmq_password = password
        self.__exchangeName = exchangeName
        self.__queueName = queueName
        self.__logger = LogUtil()

    def init_conn(self, queueName, routingKey):
        conn_broker = None
        try:
            credentials = pika.PlainCredentials(self.__rabbitmq_user, self.__rabbitmq_password)
            conn_params = pika.ConnectionParameters(self.__rabbitmq_host, self.__rabbitmq_port, credentials=credentials)
            conn_broker = pika.BlockingConnection(conn_params)
            # 创建虚拟连接channel
            cha = conn_broker.channel()

            # 创建名为yanfa,类型为fanout的exchange，其他类型还有direct和topic，如果指定durable为真，exchange将持久化
            cha.exchange_declare(durable=True, exchange=self.__exchangeName, exchange_type='topic', )
            cha.exchange_declare(durable=True, exchange=self.__exchangeName + "@retry", exchange_type='topic', )
            cha.exchange_declare(durable=True, exchange=self.__exchangeName + "@failed", exchange_type='topic', )

            # 创建队列anheng,durable参数为真时，队列将持久化；exclusive为真时，建立临时队列
            arguments = {'x-expires': 604800000}  # 队列的存活时间是7天
            cha.queue_declare(queue=queueName, durable=True, exclusive=False, arguments=arguments)
            cha.queue_declare(queue=queueName + "@failed", durable=True, exclusive=False, arguments=arguments)
            arguments = {"x-dead-letter-exchange": self.__exchangeName,
                         "x-message-ttl": 30 * 1000,
                         "x-dead-letter-routing-key": queueName}
            cha.queue_declare(queue=queueName + "@retry", durable=True, exclusive=False, arguments=arguments)

            # 绑定exchange和queue,result.method.queue获取的是队列名称
            cha.queue_bind(exchange=self.__exchangeName, queue=queueName, routing_key=routingKey, )
            cha.queue_bind(exchange=self.__exchangeName, queue=queueName, routing_key=queueName, )
            cha.queue_bind(exchange=self.__exchangeName + "@failed", queue=queueName + "@failed", routing_key=queueName, )
            cha.queue_bind(exchange=self.__exchangeName + "@retry", queue=queueName + "@retry", routing_key=queueName, )
            # 公平分发，使每个consumer在同一时间最多处理一个message，收到ack前，不会分配新的message
            cha.basic_qos(prefetch_count=1)

            return conn_broker, cha
        except Exception as e:
            if conn_broker:
                conn_broker.close()
            error = "rabbitmq initialize fail " + str(e)
            self.__logger.error(error)
            raise Exception(error)

    def subscribe(self, conn_broker, channel, queueName):
        try:
            channel.basic_consume(self.consume_message, queue=queueName, no_ack=False, )

            # print('开始等待消息')
            self.__logger.info('开始等待消息')

            channel.basic_qos(prefetch_count=1)
            channel.start_consuming()
        except Exception as e:
            channel.basic_consume(self.retry_consume, queue=queueName, no_ack=True, )
            channel.start_consuming()

    def consume_message(self, ch, method, properties, body):
        try:
            """
            连接规则引擎，处理队列中的消息
            """
            # do something
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            # print(str(e))
            error = "consume message fail " + str(e)
            self.__logger.error(error)
            raise Exception(error)

    def retry_consume(self, ch, method, properties, body):
        try:
            retryCount = self.getRetryCount(properties)
            if retryCount > 3:
                # 重试次数大于3次，则自动加入到失败队列
                # print("failed. send message to failed exchange")
                self.__logger.info("failed. send message to failed exchange")
                headers = {"x-orig-routing-key": self.getOrigRoutingKey(properties, "")}
                ch.basic_publish(exchange=self.__exchangeName + "@failed", routing_key=self.__queueName, body=body, properties=pika.BasicProperties(delivery_mode=2, headers=headers))
            else:
                # 重试次数小于3，则加入到重试队列，30s后再重试
                # print("exception. send message to retry exchange")
                self.__logger.info("exception. send message to retry exchange")
                headers = properties.headers
                if headers is None:
                    headers = {"x-orig-routing-key": self.getOrigRoutingKey(properties, "")}
                ch.basic_publish(exchange=self.__exchangeName + "@retry", routing_key=self.__queueName, body=body, properties=pika.BasicProperties(delivery_mode=2, headers=headers))
        except Exception as e:
            error = "retry to consume message fail " + str(e)
            self.__logger.error(error)
            raise Exception(error)

    def getRetryCount(self, properties):
        retry_count = 0
        try:
            headers = properties.headers
            if headers is not None:
                if headers["x-death"] is not None:
                    deaths = headers["x-death"]
                    if len(deaths) > 0:
                        death = deaths[0]
                        retry_count = death["count"]
        except Exception as e:
            error = "getRetryCount fail " + str(e)
            self.__logger.error(error)
            raise Exception(error)
        finally:
            return retry_count

    def getOrigRoutingKey(self, properties, defaultValue):
        routingKey = defaultValue
        try:
            headers = properties.headers
            if headers is not None:
                if headers["x-orig-routing-key"] is not None:
                    routingKey = str(headers["x-orig-routing-key"])
        except Exception as e:
            error = "getOrigRoutingKey fail " + str(e)
            self.__logger.error(error)
            raise Exception("getOrigRoutingKey fail " + str(e))
        finally:
            return routingKey
