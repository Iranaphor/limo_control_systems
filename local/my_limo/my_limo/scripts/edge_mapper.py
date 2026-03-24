#!/usr/bin/env python3
import os
import yaml

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, HistoryPolicy, ReliabilityPolicy, DurabilityPolicy

from std_msgs.msg import String
from sensor_msgs.msg import Joy
from geometry_msgs.msg import PointStamped, PoseWithCovarianceStamped, Point


edge_template = """
    - edge_id: {name}_{name2}
      action: {action}
      action_type: {action_type}
      config: []
      fail_policy: fail
      fluid_navigation: true
      goal:
        target_pose:
          header:
            frame_id: $node.parent_frame
          pose: $node.pose
      node: {name2}
      recovery_behaviours_config: ''
      restrictions_planning: {restrictions}
      restrictions_runtime: obstacleFree_1"""


#tmap = opening.format(**{'gen_time':0, 'location':location})
#tmap += node.format(**{'name':name, 'location':location, 'vert': verts[type], 'x':x, 'y':y, 'vert':'*vert0', 'restrictions':'True'})
#node += edge.format(**{'name':'start', 'name2':'goal', 'action':'nav2', 'action_type':'nav2/GoToNode', 'restrictions':'True'})
#tmap += vert_sample


class EdgeMapper(Node):

    def __init__(self):
        super().__init__('edge_mapper')

        self.tmappath = os.getenv('edge_list')
        self.tmappath = os.getenv('TMAP_FILE_WRITE')
        self.edgepath = os.getenv('ENVIRONMENT_TEMPLATE') + '/config/topological/edge_list.yaml'

        self.tmap = ''
        qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.tmap_sub = self.create_subscription(String, '/topological_map_2', self.tmap_cb, qos)

        self.point = 'none'
        self.pose_sub = self.create_subscription(String, '/current_node', self.node_cb, 10)


    def tmap_cb(self, msg):
        print('map recieved')
        self.tmap = yaml.safe_load(msg.data)
        self.node_list = [n['node']['name'] for n in self.tmap['nodes']]
        self.edge_dict = {n['node']['name']:[] for  n in self.tmap['nodes']}

    def node_cb(self, msg):
      
        # Check if recieved map:
        if not self.tmap:
            print('map not yet available')
            return

        # Check if left node
        if msg.data == 'none':
            print('left node')
            return

        # Recieve node:
        node = msg.data
        print(f'Now at node: {node}')
        for e in self.edge_dict[node]:
            print(f'| i,')

        # Recieve inputs for each edge connected to the current node
        print('Identify the WayPoint id number for each node connected to the current node via a directed edge.')
        print('Enter \'q\' to finish this node:')
        inp = ''
        while inp != 'q':
            inp = input('  - node: ')
            waypoint = 'WayPoint'+inp
            if inp == 'q':
                print(' -      : exit detected')
                break
            if waypoint not in self.node_list:
                print(f' -     : this node {waypoint} is not known')
                continue
            self.edge_dict[node] += [waypoint]
        
        self.save_map()


    def save_map(self):
        print('\nWriting map to file...')

        # Define default edge parameters
        edge = {'name':'source', 'name2':'goal', 'action':'NavigateToPose', 'action_type':'geometry_msgs/PoseStamped', 'restrictions':'True'}

        # Loop through each node to populated edges
        for n in self.tmap['nodes']:
            edge['name'] = n['node']['name']

            # Loop through each logged edge for this node
            for e in self.edge_dict[n['node']['name']]:
                edge['name2'] = e
                n['node']['edges'] += yaml.safe_load(edge_template.format(**edge))

        # Write map to file
        with open(self.tmappath, 'w') as f:
            f.write(yaml.dump(self.tmap))


def main(args=None):
    rclpy.init(args=args)

    EM = EdgeMapper()
    rclpy.spin(EM)

    EM.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
