import numpy as np

class Node(object):
    def __init__(self, inbound_nodes=[]):
        # Nodes from which this Node receives values
        self.inbound_nodes = inbound_nodes
        # Nodes to which this Node passes values
        self.outbound_nodes = []
        # A calculated value
        self.value = None
        # Add this node as an outbound node on its inputs.
        for n in self.inbound_nodes:
            n.outbound_nodes.append(self)

    # These will be implemented in a subclass.
    def forward(self):
        """
        Forward propagation.

        Compute the output value based on `inbound_nodes` and
        store the result in self.value.
        """
        raise NotImplemented


class Input(Node):
    def __init__(self):
        # an Input node has no inbound nodes,
        # so no need to pass anything to the Node instantiator
        Node.__init__(self)

    # NOTE: Input node is the only node that may
    # receive its value as an argument to forward().
    #
    # All other node implementations should calculate their
    # values from the value of previous nodes, using
    # self.inbound_nodes
    #
    # Example:
    # val0 = self.inbound_nodes[0].value
    def forward(self, value=None):
        if value is not None:
            self.value = value


class Add(Node):
    def __init__(self, *inputs):
        Node.__init__(self, inputs)

    def forward(self):
        sum = 0
        for input in self.inbound_nodes:
            sum += input.value
        self.value = sum


class Mul(Node):
    def __init__(self, *inputs):
        Node.__init__(self, inputs)

    def forward(self):
        product = 1
        for input in self.inbound_nodes:
            product *= input.value
        self.value = product

class Linear(Node):
    def __init__(self, X, W, b):
        Node.__init__(self, [X, W, b])

    def forward(self):
        X = self.inbound_nodes[0].value
        W = self.inbound_nodes[1].value
        b = self.inbound_nodes[2].value
        self.value = np.dot(X, W) + b

class Sigmoid(Node):
    """
    You need to fix the `_sigmoid` and `forward` methods.
    """
    def __init__(self, node):
        Node.__init__(self, [node])

    def _sigmoid(self, x):
        """
        This method is separate from `forward` because it
        will be used later with `backward` as well.

        `x`: A numpy array-like object.
        """
        return 1. / (1. + np.exp(-x))



    def forward(self):
        # This is a dummy value to prevent numpy errors
        # if you test without changing this method.
        input_value = self.inbound_nodes[0].value
        self.value = self._sigmoid(input_value)

class MSE(Node):
    def __init__(self, y, a):
        """
        The mean squared error cost function.
        Should be used as the last node for a network.
        """
        # Call the base class' constructor.
        Node.__init__(self, [y, a])

    def forward(self):
        """
        Calculates the mean squared error.
        """
        # NOTE: We reshape these to avoid possible matrix/vector broadcast
        # errors.
        #
        # For example, if we subtract an array of shape (3,) from an array of shape
        # (3,1) we get an array of shape(3,3) as the result when we want
        # an array of shape (3,1) instead.
        #
        # Making both arrays (3,1) insures the result is (3,1) and does
        # an elementwise subtraction as expected.
        y = self.inbound_nodes[0].value.reshape(-1, 1)
        a = self.inbound_nodes[1].value.reshape(-1, 1)
        errors = y - a
        square_errors = np.square(errors)
        mean_square_errors = np.mean(square_errors)
        self.value = mean_square_errors


"""
No need to change anything below here!
"""


def topological_sort(feed_dict):
    """
    Sort generic nodes in topological order using Kahn's Algorithm.

    `feed_dict`: A dictionary where the key is a `Input` node and the value is the respective value feed to that node.

    Returns a list of sorted nodes.
    """

    input_nodes = [n for n in feed_dict.keys()]

    G = {}
    nodes = [n for n in input_nodes]
    while len(nodes) > 0:
        n = nodes.pop(0)
        if n not in G:
            G[n] = {'in': set(), 'out': set()}
        for m in n.outbound_nodes:
            if m not in G:
                G[m] = {'in': set(), 'out': set()}
            G[n]['out'].add(m)
            G[m]['in'].add(n)
            nodes.append(m)

    L = []
    S = set(input_nodes)
    while len(S) > 0:
        n = S.pop()

        if isinstance(n, Input):
            n.value = feed_dict[n]

        L.append(n)
        for m in n.outbound_nodes:
            G[n]['out'].remove(m)
            G[m]['in'].remove(n)
            # if no other incoming edges add to S
            if len(G[m]['in']) == 0:
                S.add(m)
    return L


def forward_pass_unsorted(graph):
    """
    Performs a forward pass through a list of sorted Nodes.

    Arguments:

        `graph`: The result of calling `topological_sort`.
    """
    # Forward pass
    for n in graph:
        n.forward()

def forward_pass(output_node, sorted_nodes):
    """
    Performs a forward pass through a list of sorted nodes.

    Arguments:

        `output_node`: A node in the graph, should be the output node (have no outgoing edges).
        `sorted_nodes`: A topologically sorted list of nodes.

    Returns the output Node's value
    """

    for n in sorted_nodes:
        n.forward()

    return output_node.value
