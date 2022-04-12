#!/usr/bin/env python
import roslib
roslib.load_manifest('learning_tf')
import rospy
import math
# import tf provides the tf.TransformListener
import tf
import geometry_msgs.msg
import turtlesim.srv

if __name__=='__main__':
    # initializes the ROS node for the process, only have one node per rospy process
    rospy.init_node('turtle_tf_listener')

    # creating a TransformListener object to start receiving transformations over the wire 
    # and buffers them for up to 10 seconds
    # this makes recieving transforms much easier
    listener = tf.TransformListener()

    # makes sure service is available before calling it
    # creates spawner proxy to call service and enable connection
    # spawner is turtlesim spawn service (takes in x,y,theta and name(opt))
    rospy.wait_for_service('spawn')
    spawner = rospy.ServiceProxy('spawn', turtlesim.srv.Spawn)
    spawner(4,2,0, 'tutrle2')

    # creates publisher that can talk with Turtlesim and instruct it to move
    turtle_vel = rospy.Publisher('turtle2/cmd_vel', geometry_msgs.msg.Twist, queue_size=1)

    # set publish rate to start receiving tf transformations over the wire:
    rate = rospy.Rate(10.0)
    
    # this is most common use pattern for testing for shutdown
    # query listenser for a specific trasnformation by lookupTransform
    while not rospy.is_shutdown():
        try:
            # we want the transform from the /turtle1 frame to the /turtle2 frame
            # then at the time we want to transform, providing rospy.time(0) will
            # return to us the latest available transform
            (trans, rot) = listener.lookupTransform('/turtle2', '/turtle1', rospy.Time(0))
        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            continue
        # this function will return two lists, first (x,y,z) linear transform of the
        # child frame relative to the parent and the second (x,y,z,w) quaternion required
        # to rotate from the parent orientation to the child orientation 
        
        angular = 4 * math.atan2(trans[1], trans[0])
        linear = 0.5 * math.sqrt(trans[0] ** 2 + trans[1] ** 2)
        cmd = geometry_msgs.msg.Twist()
        cmd.linear.x = linear 
        cmd.angular.z = angular
        turtle_vel.publish(cmd)

        rate.sleep()
