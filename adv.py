from room import Room
from player import Player
from world import World
from util import Stack, Queue
from random import choice, sample
from ast import literal_eval

class Traverse:
    def __init__(self, master_graph, player):
        # the graph used for the map
        self.master_graph = master_graph
        # the graph that gets generated from traversing
        self.graph = {}
        # a set of the visited rooms
        self.visited = set()
        # Stack for the rooms to explore
        self.stack = Stack()
        # the most recently visited room
        self.previous_room = None
        # the most recently moved direction
        self.previous_move = None
        # the direction the player is moving in
        self.moving = None
        # the next room to visit
        self.next_room = None
        # class version of the player
        self.player = player
        # deadend flag
        self.deadend = False
        # the available exits for a given room
        self.exits = self.player.current_room.get_exits()
        self.neighbors = self.get_neighbors()

    def __str__(self):
        self.deadend = self.is_deadend(self.player.current_room)
        visited = self.player.current_room.id in self.visited
        if self.previous_room is None:
            return f"Current room: {self.player.current_room.id} \nExits: {self.exits} \nNeighbors: {self.neighbors} \nPrevious move: {previous_move} \nPrevious room: {self.previous_room} \nDeadend: {self.deadend} \nVisited: {visited} \nNext room {self.next_room}"

        return f"Current room: {self.player.current_room.id} \nExits: {self.exits} \nNeighbors: {self.neighbors} \nPrevious move: {previous_move} \nPrevious room: {self.previous_room.id} \nDeadend: {self.deadend} \nVisited: {visited} \nNext room {self.next_room}"

    def update_class(self, player, previous_move):
        '''
        Updates the player reference to the player outside of this class
        '''
        self.player = player
        self.exits = player.current_room.get_exits()
        self.neighbors = self.get_neighbors()
        self.previous_move = previous_move
        self.previous_room = player.current_room.get_room_in_direction(self.reverse_direction(previous_move)) if previous_move is not None else None

    def update_graph(self,player = None,previous_move = None, backtrack=False):
        '''
        updates the graph
        '''

        # get the last move (used to connect the graph to the previous room)
        previous = self.previous_move if previous_move is None else previous_move
        if player is not None:
            self.update_class(player, previous)
            self.visited.add(self.player.current_room.id)
        else:
            raise ValueError(f"Player must not be None")



        # check if the graph is empty
        if len(self.graph) < 1:
            # add the room to the graph
            self.graph[self.player.current_room.id] = {}
            # set all of the exits as unexplored paths
            for ext in self.exits:
                self.graph[self.player.current_room.id][ext] = "?"

        elif len(self.graph) > 0:
            # check if the room ID is in the graph
            flag = self.player.current_room.id in self.graph
            # if its not
            if flag is False:
                # add it to the graph
                self.graph[self.player.current_room.id] = {}
                # set all the exits to the default value
                for ext in self.exits:
                    self.graph[self.player.current_room.id][ext] = "?"

            # connect the graph to the previous room
            reverse = self.reverse_direction(previous)
            # get the room before the current room
            roombefore = self.player.current_room.get_room_in_direction(reverse)
            if not backtrack:
                # make the room before point to the current room
                self.graph[roombefore.id][previous] = self.player.current_room.id
                # make the current room point to the room before it
                self.graph[self.player.current_room.id][reverse] = roombefore.id



        return self.graph

    def reverse_direction(self, direction):
        if direction is not None:
            reverse_dirs = {"n": "s", "s": "n", "e": "w", "w": "e"}
            return reverse_dirs[direction]
        else:
            raise ValueError(f"The direction {direction} is invalid")

    def get_neighbors(self, current_room=None, obj = False):
        # the room ID to look up in the master graph
        room_id = self.player.current_room.id if current_room is None else current_room.id
        # the data for that room
        subgraph = self.master_graph[room_id]
        #print(f"Graph data at room {room_id} {self.master_graph[room_id]}")
        neighbors = []
        if obj is False:
            # loop through each key/value pair and append the room ID number
            for key, value in subgraph.items():
                neighbors.append(value)
        else:
            exits = current_room.get_exits()
            for ext in exits:
                neighbors.append(current_room.get_room_in_direction(ext))

        return neighbors

    def is_deadend(self, current_room=None):
        '''
        takes in a room ID number (or uses the room the player is currently at) and checks all the paths it could take.
        If all of those paths are already explored, the room is a dead end
        '''
        # this will be the room number to look for
        current_room = self.player.current_room.id if current_room is None else current_room.id
        # check to make sure the room is in the graph
        if current_room in self.graph:
            subgraph = self.graph[current_room]
        else:
            raise IndexError(f"The room ID {current_room} was not found in the graph")

        for key, value in subgraph.items():
            if value == "?":
                return False

        return True

    def nextroom(self, moving):
        room_in_direction = self.player.current_room.get_room_in_direction(moving)
        self.next_room = room_in_direction.id
        return room_in_direction.id

    def get_direction(self, player=None):
        '''
        chooses a direction for the player to move in based on the paths that are unexplored
        '''
        self.player = self.player if player is None else player

        # add all the neighbors to the stack
        for neighbor in self.get_neighbors(self.player.current_room):
            self.stack.push(neighbor)

        skip = False
        while not skip:
            #print(f"{self.stack.show()} the stack")
            # pop from the stack and check if the room is not in visited
            roomID = self.stack.pop()
            #print(f"{roomID} was popped from the stack")
            # get the graph data for the current room
            subdata = self.master_graph[self.player.current_room.id]
            # find the room that was popped from the stack and return the direction
            for key, value in subdata.items():
                if value == roomID:
                    self.moving = key

            self.next_room = self.nextroom(self.moving)
            #print(f"Moving {self.moving}")
            #print(f"Next room {self.next_room}")

            # if the next room is in visited but the rooms need to be connected, visit that room
            if self.next_room in self.visited and self.check_connection(current_room=self.player.current_room, moving=self.moving):
                skip = True
                return self.moving
            elif self.next_room in self.visited:
                skip = False
            elif self.next_room not in self.visited:
                skip = True
                return self.moving

    def check_connection(self, current_room=None, moving=None):
        '''
        This function checks to see if next room the player is going to visit will need to be connected to the current room
        while the next room has already been visited.
        This basically checks if the player has walked in a loop.
        If the room the player is going to has already been visited, normally that room would get skipped.
        This checks to see if the next room hasn't been linked to the current room in the graph.
        If it returns true, the room wont be skipped, if it returns false the room will be skipped.
        '''

        current_room = self.player.current_room.id if current_room is None else current_room.id
        moving = self.moving if moving is None else moving
        next_room = self.nextroom(moving)
        #print(f"Next room -> {next_room}")
        moving_reverse = self.reverse_direction(moving)
        #print(f"Reverse direction {moving_reverse}")

        if (self.graph[next_room][moving_reverse] == "?") and (self.master_graph[next_room][moving_reverse] == current_room):
            print(f"Room {current_room} needs to be connected to room {next_room}")
            return True
        else:
            return False

    def backtrack(self, player,traversal_path):
        '''
        Makes the player travel back to the most recent room
        '''
        # flag that determines whether or not the room was found
        found = False
        # a copy of the traversal path as the travel back path
        travelback = traversal_path.copy()
        traversal = []
        #print(f"Current room {player.current_room.id}")

        while not found:
            #print(travelback)
            # get the reverse direction of the most current direction
            if self.all_rooms_searched() is False:
                direction = self.reverse_direction(travelback.pop())
            traversal.append(direction)
            print(f"Traveling back direction {direction}")
            # have the player travel there
            player.travel(direction)
            # get the room ID number
            roomID = player.current_room.id

            print(f"The player traveled back to {roomID}")
            # get the data for that room ID
            roomdata = self.graph[roomID]
            # update the class
            self.update_class(player,direction)
            # check if the room has any unexplored paths
            for key,value in roomdata.items():
                if value == "?":
                    print(f"The value from the subgraph {roomdata} is {key}")
                    return direction,traversal


            print(f"length of the graph {len(self.graph)}")

    def bfs(self, player, traversal_path):
        """
        Return a list containing the shortest path from
        starting_vertex to destination_vertex in
        breath-first order.
        """
        # create the queue
        q = Queue()
        # enqueue a path to current room
        q.enqueue([player.current_room])
        visited = set()

        while q.size() > 0:
            # get the first path
            path = q.dequeue()
            # grab room from the back
            v = path[-1]
            # check if its been visited
            if v not in visited:
                visited.add(v.id)
                # find the room in the graph
                data = self.graph[v.id]
                # see if the room has unexplored paths
                for value in data.values():
                    if value == "?":
                        return path

                for neighbor in self.get_neighbors(v,obj = True):
                    path_copy = path.copy()
                    path_copy.append(neighbor)
                    q.enqueue(path_copy)

    def all_rooms_searched(self):
        if self.graph == self.master_graph:
            print("All rooms searched")
            return True
        else:
            return False

    def decode(self, path):
        """
        decodes the travels back path made up by the bfs
        """
        travel = []
        for count,room in enumerate(path):
            #print(room.id)
            # find the room in the graph
            data = self.graph[room.id]
            #print(data)
            index = count + 1
            if index != len(path):
                for key, value in data.items():
                    if value == path[index].id:
                        #print(key)
                        travel.append(key)

        return travel


# Load world
world = World()


# You may uncomment the smaller graphs for development and testing purposes.
#map_file = "maps/test_line.txt"
#map_file = "maps/test_cross.txt"
#map_file = "maps/test_loop.txt"

#map_file = "maps/test_loop_fork.txt"
map_file = "maps/main_maze.txt"

# Loads the map into a dictionary
room_graph=literal_eval(open(map_file, "r").read())
world.load_graph(room_graph)

# Print an ASCII map
world.print_rooms()

player = Player(world.starting_room)
traversal_path = []
# TRAVERSAL TEST
visited_rooms = set()
player.current_room = world.starting_room
#visited_rooms.add(player.current_room)
master_graph = {}
graph = {}
for key, value in sorted(room_graph.items()):
    print(f"Key: {key} value: {value[1]}")
    master_graph[key] = value[1]

#print(master_graph)

roomsleft = len(room_graph) - len(visited_rooms)
trvse = Traverse(master_graph, player)
previous_move = None
moving = None
roomsleft = 15
back = False

while roomsleft > 0:
    print(f"The player is in room {player.current_room.id}")
    graph = trvse.update_graph(player=player, previous_move=previous_move,backtrack=back )
    #print(f"Graph {graph}")
    if trvse.all_rooms_searched() is False:
        if trvse.is_deadend(current_room=player.current_room) is False:
            moving = trvse.get_direction(player=player)
            traversal_path.append(moving)
            #print(f"The player is moving {moving}")
            visited_rooms.add(player.current_room)
            trvse.nextroom(moving)
            #print(trvse)
            player.travel(moving)
            #print(f"the player just moved to {player.current_room.id}")
            previous_move = moving
            roomsleft = len(room_graph) - len(visited_rooms)
            back = False

        elif trvse.is_deadend(current_room=player.current_room):
            #print(trvse)
            print(f"Room {player.current_room.id} is a deadend")
            path = trvse.bfs(player, traversal_path)
            path = trvse.decode(path)
            traversal_path += path
            for move in path:
                player.travel(move)
            back = True
            trvse.stack = Stack()
            print(f"Previous move is {previous_move}")
            #print(f"The travel back path is {path}")
    else:
        break

    # print(f"Moving: {moving}")
    # print(f"Graph {graph}")
    print(len(traversal_path))
    roomsleft -= 1

    print()



#print(graph)



player.current_room = world.starting_room
for move in traversal_path:
    #print(f"{player.current_room.id} moving {move}")
    player.travel(move)
    visited_rooms.add(player.current_room)

if len(visited_rooms) == len(room_graph):
    print(f"TESTS PASSED: {len(traversal_path)} moves, {len(visited_rooms)} rooms visited")
else:
    print("TESTS FAILED: INCOMPLETE TRAVERSAL")
    print(f"{len(room_graph) - len(visited_rooms)} unvisited rooms")



#######
# UNCOMMENT TO WALK AROUND
#######
# player.current_room.print_room_description(player)
# while True:
#     cmds = input("-> ").lower().split(" ")
#     if cmds[0] in ["n", "s", "e", "w"]:
#         player.travel(cmds[0], True)
#     elif cmds[0] == "q":
#         break
#     else:
#         print("I did not understand that command.")
