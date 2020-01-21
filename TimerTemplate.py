# Here is a template for modeling timers and timeout events for the rdt_Sender


class rdt_Sender(object):

	def __init__(self,env):
	
		.....

		# additional timer-related variables
		self.timeout_value=10
		self.timer_is_running=False
		self.timer=None

	# This function models a Timer's behavior.
	def timer_behavior(self):
		try:
			# Start
			self.timer_is_running=True
			yield self.env.timeout(self.timeout_value)
			# Stop
			self.timer_is_running=False
			# take some actions 
			self.timeout_action()
		except simpy.Interrupt:
			# upon interrupt, stop the timer
			self.timer_is_running=False

	# This function can be called to start the timer
	def start_timer(self):
		assert(self.timer_is_running==False)
		self.timer=self.env.process(self.timer_behavior())

	# This function can be called to stop the timer
	def stop_timer(self):
		assert(self.timer_is_running==True)
		self.timer.interrupt()

	def timeout_action(self):
		# add here the actions to be performed 
		# upon a timeout
		...
		
	def rdt_send(self,msg):
		# whatever actions should go here
		....

	
	def rdt_rcv(self,packt):
		# whatever actions should go here
		....
