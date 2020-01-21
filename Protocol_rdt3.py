# SimPy model for the Reliable Data Transport (rdt) Protocol 3.0 (Using ACK0 and ACK1)

#
# Sender-side (rdt_Sender)
#       - receives messages to be delivered from the upper layer
#         (SendingApplication)
#       - Implements the protocol for reliable transport
#        using the udt_send() function provided by an unreliable channel.
#
# Receiver-side (rdt_Receiver)
#       - receives packets from the unrealible channel via calls to its
#       rdt_rcv() function.
#       - implements the receiver-side protocol and delivers the collected
#       data to the receiving application.

# Author: Paras Yadav


# ACK_0 is implemented as self.payload=ACK , self.seq_num=0
# ACK_1 is implemented as self.payload=ACK , self.seq_num=1



import simpy
import random
from Packet import Packet
import sys
import time

# the sender can be in one of these four states:
WAITING_FOR_CALL_0_FROM_ABOVE = 0
WAITING_FOR_CALL_1_FROM_ABOVE = 1
WAIT_FOR_ACK_0 = 2
WAIT_FOR_ACK_1 = 3

# the receiver can be in one of these two states:
WAITING_FOR_CALL_0_FROM_BELOW = 4
WAITING_FOR_CALL_1_FROM_BELOW = 5


class rdt_Sender(object):

	def __init__(self, env):
		# Initialize variables
		self.env = env
		self.channel = None

		# some state variables
		self.state = WAITING_FOR_CALL_0_FROM_ABOVE
		self.packet_to_be_sent = None
		
		# additional timer-related variables
		self.timeout_value=6
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
		if self.timer_is_running==False:
                        # resend the packet
			self.channel.udt_send(self.packet_to_be_sent)
			self.start_timer()

	def rdt_send(self, msg):
		if self.state==WAITING_FOR_CALL_0_FROM_ABOVE:
			self.packet_to_be_sent = Packet(seq_num=0, payload=msg)
			# send it over the channel
			self.channel.udt_send(self.packet_to_be_sent)
			self.start_timer()
			# wait for an ACK
			self.state = WAIT_FOR_ACK_0
			return True
		elif self.state==WAITING_FOR_CALL_1_FROM_ABOVE:
			self.packet_to_be_sent = Packet(seq_num=1, payload=msg)

			# send it over the channel
			self.channel.udt_send(self.packet_to_be_sent)
			# wait for an ACK
			self.start_timer()
			self.state = WAIT_FOR_ACK_1
			return True
		else:
			return False

	def rdt_rcv(self, packt):
		if self.state == WAIT_FOR_ACK_0:
			if(packt.seq_num == 0 and packt.corrupted == False):
                                # Received an ACK_0. Stop the timer.
				self.stop_timer()
				self.state = WAITING_FOR_CALL_1_FROM_ABOVE
			else:
                                # take timeout action
				self.timeout_action()

		elif self.state == WAIT_FOR_ACK_1 :
			if(packt.seq_num == 1 and packt.corrupted == False):
                                # Received an ACK_1. Stop the timer.
				self.stop_timer()
				self.state = WAITING_FOR_CALL_0_FROM_ABOVE
			else:
                                # take timeout action
				self.timeout_action()
		else:
                        return False


class rdt_Receiver(object):
	def __init__(self, env):
		# Initialize variables
		self.env = env
		self.state = WAITING_FOR_CALL_0_FROM_BELOW
		self.receiving_app = None
		self.channel = None

	def rdt_rcv(self, packt):
		# This function is called by the lower-layer when a packet arrives
		# at the receiver
		if self.state == WAITING_FOR_CALL_0_FROM_BELOW:
			if(packt.seq_num == 0 and packt.corrupted == False):
                                # Received correct packet. Send ACK_0 
				response = Packet(seq_num=0, payload="ACK")
				self.channel.udt_send(response)
				self.receiving_app.deliver_data(packt.payload)
				self.state = WAITING_FOR_CALL_1_FROM_BELOW
			else :
                                # Need to resend packet.
                                # send ACK_1 and discard this packet.
				response = Packet(seq_num=1, payload="ACK") 
				self.channel.udt_send(response)
	    
		elif self.state==WAITING_FOR_CALL_1_FROM_BELOW:
			if(packt.seq_num==1 and packt.corrupted==False):
                                # Received correct packet. Send ACK_0
				response = Packet(seq_num=1, payload="ACK") 
				self.channel.udt_send(response)
				self.receiving_app.deliver_data(packt.payload)
				self.state=WAITING_FOR_CALL_0_FROM_BELOW
			else :
                                # Need to resend packet.
                                # send ACK_1 and discard this packet.
				response = Packet(seq_num=0, payload="ACK") 
				self.channel.udt_send(response)
