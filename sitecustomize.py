import os, sys
root = os.path.dirname(__file__)
if sys.path[0] != root:
    if root not in sys.path:
        sys.path.insert(0, root)
