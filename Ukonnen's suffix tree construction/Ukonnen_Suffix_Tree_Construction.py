import sys

class SuffixTree:
    '''
    Suffix tree class includes all nodes it has and all methods needed to construct suffix tree.
    '''
    class Node:
        '''
        Node class represents all kinds of node in suffix tree.
        '''
        def __init__(self, node_id, p, q):
            # node id is incremented whenever new node is added
            self.node_id = node_id
            self.children = []
            self.parent = None
            # index range here denotes the indexes in subtext at current phase.
            # and the text represented by index range is the label of the edge toward parent
            self.stringIndex = (p, q)
            self.node_linked_by_suffix_link = -1

        def addChild(self, node_id):
            self.children.append(node_id)

        def removeChild(self, node_id):
            self.children.remove(node_id)

        def setParent(self, node_id):
            self.parent = node_id

        def setSuffixLink(self, node_id):
            self.node_linked_by_suffix_link = node_id

        def setIndex(self, p, q):
            self.stringIndex = (p, q)

        def getID(self):
            return self.node_id

        def getChildren(self):
            return self.children

        def getParent(self):
            return self.parent

        def getSuffixLink(self):
            return self.node_linked_by_suffix_link

        def getIndex(self):
            return self.stringIndex

    def __init__(self):
        # text at current phase
        self.text = ""
        # initialize with root node
        self.nodes = {0: self.Node(0, 0, 0)}
        self.id_count = 1

    # get the node object with node id
    def getNode(self, node_id):
        return self.nodes[node_id]

    # get the list of ids of children
    def children(self, node_id):
        return self.getNode(node_id).getChildren()

    # check if node is leaf
    def isLeaf(self, node_id):
        return len(self.children(node_id)) == 0

    # get the id of parent
    def parent(self, node_id):
        return self.getNode(node_id).getParent()

    # get the label of edge between parent node_id1 and child node_id2
    def edgeLabel(self, node_id1, node_id2):
        if self.parent(node_id2) == node_id1:
            # get the index range of child
            string_index = self.getNode(node_id2).getIndex()

            # if right index is None, it means the end of current text
            if not string_index[1]:
                string_index = (string_index[0], len(self.text))
            return self.text[string_index[0]:string_index[1]]
        else:
            # misuse catch
            print("first node should be parent of second one.")
            return None

    # add a new node and arrange the relationships among new node and existing nodes
    def new_node(self, active_pos, i, j):
        active_node_id = active_pos[0]
        active_node_letter = active_pos[1]
        active_node_depth = active_pos[2]

        # if new node is inserted at node
        if active_node_letter == '':
            self.nodes[self.id_count] = self.Node(self.id_count, i, j)
            # new node is added below the existing node
            self.nodes[self.id_count].setParent(active_node_id)
            self.nodes[active_node_id].addChild(self.id_count)
            self.id_count += 1

            # return id of existing node
            return active_node_id

        # if new node is inserted at the middle of edge
        # then two nodes should be created
        else:
            inner_id = self.id_count
            # locate the newly created inner node in appropriate position with active_pos
            for child in self.children(active_node_id):
                curr_edge = self.edgeLabel(active_node_id, child)
                if curr_edge[0] == active_node_letter:
                    # split the index range at the point where the new node is created
                    child_string_index = self.getNode(child).getIndex()
                    index_split_point = child_string_index[0] + active_node_depth
                    self.getNode(child).setIndex(index_split_point, child_string_index[1])

                    # make inner node
                    # inner node becomes parent of child node of existing node
                    # and child of existing node
                    new_inner_node = self.Node(inner_id, child_string_index[0], index_split_point)
                    self.nodes[inner_id] = new_inner_node
                    self.nodes[inner_id].setParent(active_node_id)
                    self.nodes[active_node_id].addChild(inner_id)
                    self.nodes[active_node_id].removeChild(child)
                    self.nodes[inner_id].addChild(child)
                    self.getNode(child).setParent(inner_id)
                    self.id_count += 1
                    break

            # then, make leaf node
            # leaf node becomes child of newly created inner node
            leaf_id = self.id_count
            self.nodes[leaf_id] = self.Node(leaf_id, i, j)
            self.nodes[leaf_id].setParent(inner_id)
            self.nodes[inner_id].addChild(leaf_id)
            self.id_count += 1

            # return id of inner node
            return inner_id

    # add suffix link from node_i to node_j
    def add_suffix_link(self, node_i, node_j):
        if node_i != node_j:
            self.getNode(node_i).setSuffixLink(node_j)

    # move down(or walk down) from active_pos toward the edge where next character is c
    def move_down(self, active_pos, c):
        active_node_id = active_pos[0]
        active_node_letter = active_pos[1]
        active_node_depth = active_pos[2]

        # if I don't know where to head
        if active_node_letter == '':
            # find the edge whose first character matches with c
            for child in self.children(active_node_id):
                curr_edge = self.edgeLabel(active_node_id, child)
                if curr_edge[0] == c:
                    # if I get to the node
                    if len(curr_edge) == active_node_depth + 1:
                        return child, '', 0
                    return active_node_id, c, 1
            # there is no edge whose first character matches with c
            # I cannot move down
            return None

        # if I know where to head
        else:
            for child in self.children(active_node_id):
                curr_edge = self.edgeLabel(active_node_id, child)
                if curr_edge[0] == active_node_letter:
                    # if I get to the node
                    if len(curr_edge) == active_node_depth:
                        return child, '', 0
                    else:
                        # if I move down one step onto edge
                        if curr_edge[active_node_depth] == c:
                            return active_node_id, active_node_letter, active_node_depth + 1
                        # there is no edge whose first character matches with c
                        # I cannot move down
                        else:
                            return None
            print("Something wrong. It should not happen.")

    # move along suffix link
    # if there is no suffix link, it move to root
    def use_suffix_link(self, active_pos):
        active_node_id = active_pos[0]
        active_node_letter = active_pos[1]
        active_node_depth = active_pos[2]

        orig_label = ''
        # when move from the root node or the edge connected to root
        if active_node_id == 0:
            if active_node_depth == 0:
                depth = 0
            else:
                depth = active_node_depth - 1

            for child in self.children(active_node_id):
                curr_edge = self.edgeLabel(active_node_id, child)
                if curr_edge[0] == active_node_letter:
                    # record the label of the edge from which I move
                    orig_label = curr_edge[1:active_node_depth]
        # when move from the point irrelavant with root
        else:
            depth = active_node_depth

            for child in self.children(active_node_id):
                curr_edge = self.edgeLabel(active_node_id, child)
                if curr_edge[0] == active_node_letter:
                    # record the label of the edge from which I move
                    orig_label = curr_edge[0:active_node_depth]

        # destination node for which suffix link is headed
        dest_node = self.getNode(active_node_id).getSuffixLink()
        # if there is no suffix link yet, move to root
        if dest_node == -1:
            dest_node = 0

        # move down along the right way
        # from root to root
        if dest_node == 0 and depth == 0:
            return 0, '', 0
        else:
            while True:
                # move to node other than root
                if depth == 0:
                    return dest_node, '', 0

                # move to point amid of edge
                for child in self.children(dest_node):
                    curr_edge = self.edgeLabel(dest_node, child)
                    if curr_edge[0] == orig_label[0]:
                        if depth < len(curr_edge):
                            return dest_node, orig_label[0], depth
                        # if edge is shorter than depth,
                        # change active node to next inner node
                        else:
                            dest_node = child
                            orig_label = orig_label[len(curr_edge):depth]
                            depth -= len(curr_edge)

    # print the tree at certain phase in DOT format
    def print(self, phase):
        ret_str = ""
        ret_str += "digraph phase" + str(phase) + " {\n"
        for node in self.nodes.keys():
            line = ""
            for child in self.children(node):
                child_node = self.getNode(child)
                line += "\t{0} -> {1} ".format(node, child)
                line += '[ label =" {0} "]\n'.format(self.edgeLabel(node, child))
            if self.nodes[node].getSuffixLink() != -1:
                line += "\t{0} -> {1} [ style = dotted ]\n".format(node, self.nodes[node].getSuffixLink())
            if self.isLeaf(node):
                line += "\t{0} [ shape = box ]\n".format(node)
            ret_str += line
        ret_str += "}"
        return ret_str

tree = SuffixTree()  # empty tree class
active_pos = (0, '', 0)  # (active_node_id, active_node_letter, active_node_depth)
# active_node_id = 0 means root node

s = sys.argv[1]
assert isinstance(s, str), "given argument is not string."

for i, c in enumerate(s):
    tree.text += c  # c = s[i] # tree.text becomes s[0..i-1]
    visited_nodes = []  # list of parents of nodes created during the current phase

    while True:
        new_pos = tree.move_down(active_pos, c)
        if new_pos is None:  # moving down is impossible
            link_target = tree.use_suffix_link(active_pos)  # traverse via suffix link
            if active_pos == (0, '', 0):
                is_insertion_at_root = True
            else:
                is_insertion_at_root = False
            parent_id = tree.new_node(active_pos, i, None)  # index None denotes end of current text
            visited_nodes.append(parent_id)  # add a parent of newly created node
            active_pos = link_target  # target reached by suffix link becomes new active_pos
            # phase end only if active_pos lie at root node
            if link_target == (0, '', 0) and is_insertion_at_root:
                break


        else:  # when the suffix we need to insert is found to exist in the tree already
            visited_nodes.append(active_pos[0])  # add current active_node_id
            active_pos = new_pos  # set the position moved down as active_pos
            break
    for j in range(len(visited_nodes) - 1):
            tree.add_suffix_link(visited_nodes[j],
                                 visited_nodes[j + 1])  # make new suffix links between consecutive parents

    output = open("suffix_tree_" + s + "_phase_" + str(i+1) + ".DOT", "w")
    output.write(tree.print(i))
    output.close()