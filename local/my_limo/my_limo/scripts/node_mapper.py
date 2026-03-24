#!/usr/bin/env python3
import os

import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from sensor_msgs.msg import Joy
from geometry_msgs.msg import PointStamped, PoseWithCovarianceStamped, Point


opening = """
meta:
  last_updated: {gen_time}
metric_map: {location}
name: {location}
pointset: {location}
transformation:
  child: topo_map
  parent: map
  rotation:
    w: 1.0
    x: 0.0
    y: 0.0
    z: 0.0
  translation:
    x: 0.0
    y: 0.0
    z: 0.0
nodes:"""

node = """
- meta:
    map: {location}
    node: {name}
    pointset: {location}
  node:
    localise_by_topic: ''
    parent_frame: map
    name: {name}
    pose:
      orientation:
        w: 0.7897749049165983
        x: 0.0
        y: 0.0
        z: -0.6133967717260812
      position:
        x: {x}
        y: {y}
        z: 0.0
    properties:
      xy_goal_tolerance: 0.3
      yaw_goal_tolerance: 0.1
    restrictions_planning: {restrictions}
    restrictions_runtime: obstacleFree_1
    verts: *{vert}
    edges: []"""

vert_sample = """
verts:
  verts:
  - verts: &vert0
    - x: -0.13
      y:  0.213
    - x: -0.242
      y:  0.059
    - x: -0.213
      y: -0.13
    - x: -0.059
      y: -0.242
    - x:  0.13
      y: -0.213
    - x:  0.242
      y: -0.059
    - x:  0.213
      y:  0.13
    - x:  0.059
      y:  0.242"""

#tmap = opening.format(**{'gen_time':0, 'location':location})
#tmap += node.format(**{'name':name, 'location':location, 'vert': verts[type], 'x':x, 'y':y, 'vert':'*vert0', 'restrictions':'True'})
#tmap += vert_sample


class NodeMapper(Node):

    def __init__(self):
        super().__init__('node_mapper')

        self.location = os.getenv('FIELD_NAME', 'unknown')
        self.tmappath = os.getenv('TMAP_FILE_WRITE')
        self.tmap = vert_sample
        self.tmap += opening.format(**{'gen_time':0, 'location':self.location})
        self.total_nodes = 0

        self.nodepath = os.getenv('ENVIRONMENT_TEMPLATE') + '/config/topological/node_list.yaml'
        with open(self.nodepath, 'w') as f:
            f.write('')

        self.say = self.create_publisher(String, '/verbaliser/speaker', 10)

        self.cp_sub = self.create_subscription(PointStamped, '/clicked_point', self.clicked_point_cb, 10)

        self.point = Point()
        self.pose_sub = self.create_subscription(PoseWithCovarianceStamped, '/amcl_pose', self.pose_cb, 10)

        self.x_pressed = False
        self.joy_sub = self.create_subscription(Joy, '/joy', self.joy_cb, 10)

        
    def pose_cb(self, msg):
        self.point = msg.pose.pose.position

    def joy_cb(self, msg):
        if msg.buttons[2] == True and self.x_pressed == False:
            print('jot input detected')
            self.x_pressed = True
            self.save_location(x=self.point.x, y=self.point.y)
        elif msg.buttons[2] == False:
            self.x_pressed = False

    def clicked_point_cb(self, msg):
        print('point click detected')
        self.save_location(x=msg.point.x, y=msg.point.y)

    def save_location(self, x, y):
        print('saving location:', [x, y])

        # Append node location to simple file
        with open(self.nodepath, 'a') as f:
            f.write(str(x) + ", " + str(y) + "\n")

        # Construct node in tmap and save to file
        self.total_nodes += 1
        self.tmap += node.format(**{'name':'WayPoint%s'%self.total_nodes, 'location':self.location, 'x':x, 'y':y, 'vert':'vert0', 'restrictions':'True'})
        
        self.say.publish(String(data=f'WayPoint{self.total_nodes} at: x {round(x,1)}, y {round(y,1)}'))

        with open(self.tmappath, 'w') as f:
            f.write(self.tmap)


def main(args=None):
    rclpy.init(args=args)

    NM = NodeMapper()
    rclpy.spin(NM)

    NM.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
