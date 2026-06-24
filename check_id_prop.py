from neomodel import StructuredNode
import inspect

print('StructuredNode.id:', getattr(StructuredNode, 'id', None))
if hasattr(StructuredNode, 'id'):
    attr = getattr(StructuredNode, 'id')
    print(type(attr))
    if isinstance(attr, property):
        print('property')
        print('  fget:', attr.fget)
        print('  fset:', attr.fset)
        print('  fdel:', attr.fdel)
    else:
        print('Not a property')
else:
    print('No id attribute')

# Let's also check the source if possible
try:
    print(inspect.getsource(attr.fget))
except Exception as e:
    print('Cannot get source:', e)
