class FibHeap:
    # Trees are implemented using a doubly-linked list.
    # So parents point to children and children point to parents.
    class Node:
        def __init__(self, index, key):
            self.index = index
            self.key = key
            self.parent = None
            self.children = []
            self.marked = False

    def __init__(self):
        # Keeps track of:
        # 1) a pointer to the minimum key and the corresponding node object
        # 2) pointers to all nodes in the tree (accessed by index,
        #     so stored in a dictionary)
        # 3) pointers to the roots of all trees in the root level.
        self.min_key = float('inf')
        self.min_node = None
        self.nodes = {}
        self.root = []
    
    def is_empty(self):
        return len(self.nodes) == 0

    def in_heap(self, index):
        return index in self.nodes
    
    def update_min(self):
        # Given the root list, set the new min_key and min_node.
        self.min_key = float('inf')
        self.min_node = None
        for node in self.root:
            if node.key < self.min_key:
                self.min_key = node.key
                self.min_node = node

    def link(self, node1, node2):
        if node1.key <= node2.key:
            parent = node1
            child  = node2
        else:
            parent = node2
            child  = node1
        # Doubly-link the two nodes.
        child.parent = parent
        parent.children += [child]
        # Return the parent
        return parent

    def combine(self):
        # Merge root trees so that no two roots have the same rank.
        # It's possible that every tree in root has a different rank.
        # Since we might merge trees from all over the place, it will
        # be confusing to keep track of which index is next. So make a new
        # list of root nodes and set self.root to that.
        rank = {}
        while self.root:
            node = self.root.pop()
            node_rank = len(node.children)
            while node_rank in rank and rank[node_rank] != node:
                # Link the previous node with "node_rank" children
                # and the new node. Return the parent, which now contains
                # the other as its child, and the child now points to parent.
                # The parent after linking has node_rank+1 children, and its
                # previous state should be deleted from "rank".
                node0 = rank[node_rank]
                del rank[node_rank]
                node = self.link(node, node0)
                node_rank += 1
            # Record the new tree in the root list.
            rank[node_rank] = node

        self.root = rank.values()
        self.update_min()

    def insert(self, index, key):
        new_node = self.Node(index, key)
        # Pointers to this new node
        self.nodes[index] = new_node
        self.root += [new_node]
        # Update min pointer if necessary
        if key < self.min_key:
            self.min_key = key
            self.min_node = new_node

    def delete_min(self):
        # Move children of the min_node to root level.
        for node in self.min_node.children:
            node.parent = None
        self.root += self.min_node.children
        # Remove references to the "deleted" min_node.
        del self.nodes[self.min_node.index]
        self.root.remove(self.min_node)
        # print sys.getrefcount(self.min_node)
        # Merge root trees so that no two roots have the same rank.
        # Also updates the new min_key.
        self.combine()
        # print sys.getrefcount(self.min_node), len(self.min_node.children), self.min_node.parent

    def pop_min(self):
        if self.min_node != None:
            ret = [self.min_node.index, self.min_node.key]
            self.delete_min()
            return ret
        else:
            print "Fib heap is empty."

    def decrease_key(self, index, new_key):
        node = self.nodes[index]
        parent = node.parent
        if new_key > node.key:
            raise ValueError('New key must be less than old key.')
        # Decrease the key.
        node.key = new_key
        # If heap order is not violated, return.
        if parent == None:
            # Update min_node if a root is changed.
            if new_key < self.min_key: 
                self.min_key = new_key
                self.min_node = node
            return
        elif new_key > parent.key:
            return

        # If heap order is violated, move current tree rooted at "node" 
        # to the root list, unmark it.

        # Parent and child do not point to each other anymore.
        parent.children.remove(node)
        node.parent = None
        # Add the node to the root list, and unmark it.
        self.root += [node]
        node.marked = False

        # If its parent is unmarked, then mark it and stop.
        # If its parent is marked, move the parent into root list
        # and unmark it, and loop for the parent's parent.
        node, parent = parent, parent.parent
        while node.marked and parent:
            # Disconnect this node and its parent.
            parent.children.remove(node)
            node.parent = None
            # Add the node to the root list, and unmark it.
            self.root += [node]
            node.marked = False
            # Move up and loop.
            node, parent = parent, parent.parent

        # Stopped looping when node is unmarked and has a parent,
        #   in this case, it should be marked.
        # Or if it has no parent,
        #   if it is marked then move to root (already here) and unmark
        #   if it is unmarked, mark it.
        node.marked = not node.marked

        self.update_min()