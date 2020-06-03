from __future__ import print_function
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service

import array
try:
  from gi.repository import GObject
except ImportError:
  import gobject as GObject
import advertising
import gatt_server
import argparse

import rospy
from std_msgs.msg import String
from multiprocessing import Process
import cPickle


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--adapter-name', type=str, help='Adapter name', default='')
    args = parser.parse_args()
    adapter_name = args.adapter_name

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    mainloop = GObject.MainLoop()

    advertising.advertising_main(mainloop, bus, adapter_name)
    gatt_server.gatt_server_main(mainloop, bus, adapter_name)
    mainloop.run()

def listener():

    # In ROS, nodes are uniquely named. If two nodes with the same
    # name are launched, the previous one is kicked off. The
    # anonymous=True flag means that rospy will choose a unique
    # name for our 'listener' node so that multiple listeners can
    # run simultaneously.
    rospy.init_node('listener', anonymous=True)

    #rospy.Subscriber("/seva_events", String, executeSevaEvent)
    rospy.Subscriber("/my_topic", String, executeSevaEvent)
    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

def executeSevaEvent(data):
    event = data.data
    rospy.loginfo(rospy.get_caller_id() + "Seva Event Executor: %s", event)
    rospy.loginfo(event+" triggered.")
    file = open('SevaEvent.dat', 'wb')
    cPickle.dump(event, file, protocol = -1)
    file.close()

class movement(object):
    def __init__(self):
	self.move = 0


if __name__ == '__main__':
    m = movement()
    p1 = Process(target = main)
    p1.start()
    p2 = Process(target = listener)
    p2.start()
    p1.join()
    p2.join()

