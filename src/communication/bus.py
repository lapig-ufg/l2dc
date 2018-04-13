import pika
from .message import Message

EXCHANGE_KEY = 'message'

class SyncPublisher():
	
	def __init__(self, config,  publish_channel):
		self._connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
		self._channel = self._connection.channel()
		
		self.publisherQueue = publish_channel
		self._channel.queue_declare(queue=self.publisherQueue, durable=True)

	def publish(self, message):
		self._channel.basic_publish(exchange=EXCHANGE_KEY, routing_key=self.publisherQueue, body=message.serialize())

class AsyncConsumerPublisher():
	 
	def __init__(self, config,  subcribe_channel, publish_channel):
		self._closing = False
		self._consumer_tag = None
		self._url = 'amqp://guest:guest@localhost:5672/%2F'

		self.consumerQueue = subcribe_channel
		self.consumerReady = False

		self.publisherQueue = publish_channel
		self.publisherReady = False

		self._connection = self.connect()

	def connect(self):
		return pika.SelectConnection(pika.URLParameters(self._url), self.on_connection_open, stop_ioloop_on_close=False)

	def on_connection_open(self, unused_connection):
		self._connection.add_on_close_callback(self.on_connection_closed)
		self.open_channel()

	def on_connection_closed(self, connection, reply_code, reply_text):
		self._channel = None
		if self._closing:
				self._connection.ioloop.stop()
		else:
				self._connection.add_timeout(5, self.reconnect)

	def reconnect(self):
		self._connection.ioloop.stop()

		if not self._closing:
			self._connection = self.connect()
			self._connection.ioloop.start()

	def open_channel(self):
		self._connection.channel(on_open_callback=self.on_channel_open)

	def on_channel_open(self, channel):
		self._channel = channel
		self._channel.basic_qos(prefetch_count=1)
		self._channel.add_on_close_callback(self.on_channel_closed)

		if not self.consumerQueue is None:
			self.create_consumer()

		if not self.publisherQueue is None:
			self.create_publisher()
		
	def on_channel_closed(self, channel, reply_code, reply_text):
		self._connection.close()

	def create_consumer(self):
		self._channel.exchange_declare(callback=self.on_consumer_exchange_ready, exchange=EXCHANGE_KEY, exchange_type='direct')

	def on_consumer_exchange_ready(self, unused_frame):
		self._channel.queue_declare(callback=self.on_consumer_queue_ready, queue=self.consumerQueue, durable=True)
			
	def on_consumer_queue_ready(self, method_frame):
		self._channel.queue_bind(callback=self.on_consumer_queue_bind, queue=self.consumerQueue, exchange=EXCHANGE_KEY, routing_key=self.consumerQueue)

	def on_consumer_queue_bind(self, unused_frame):
		self._channel.add_on_cancel_callback(self.on_consumer_cancelled)
		self._consumer_tag = self._channel.basic_consume(consumer_callback=self.on_message, queue=self.consumerQueue)
		self.consumerReady = True

	def on_consumer_cancelled(self, method_frame):
		if self._channel:
			self._channel.close()
			self.consumerReady = False

	def on_message(self, unused_channel, basic_deliver, properties, body):
		rawData = body.decode('utf-8');
		result = self.consumerCallback(Message(rawData))
		if result:
			self._channel.basic_ack(basic_deliver.delivery_tag)
		else:
			self._channel.basic_nack(basic_deliver.delivery_tag)

	def create_publisher(self):
		self._channel.exchange_declare(callback=self.on_publisher_exchange_ready, exchange=EXCHANGE_KEY, exchange_type='direct')

	def on_publisher_exchange_ready(self, unused_frame):
		self._channel.queue_declare(callback=self.on_publisher_queue_ready, queue=self.publisherQueue, durable=True)
			
	def on_publisher_queue_ready(self, method_frame):
		self._channel.queue_bind(callback=self.on_publisher_queue_bind, queue=self.publisherQueue, exchange=EXCHANGE_KEY, routing_key=self.publisherQueue)

	def on_publisher_queue_bind(self, unused_frame):
		self._channel.add_on_cancel_callback(self.on_publisher_cancelled)
		self.publisherReady = True

	def on_publisher_cancelled(self, method_frame):
		if self._channel:
			self._channel.close()
			self.publisherReady = False

	def publish(self, message):
		self._channel.basic_publish(exchange=EXCHANGE_KEY, routing_key=self.publisherQueue, body=message.serialize(), properties=pika.BasicProperties(delivery_mode = 2))

	def listen(self, consumerCallback):
		self.consumerCallback = consumerCallback
		self._connection.ioloop.start()