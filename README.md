# anatawa12's blender libraries extension

## how to install

1. download zip [here][zip-link].
2. open preference of Blender at 'Edit' menu
3. Select `Add-ons` from left menu
4. Click `install...`
5. select downloaded zip

[zip-link]: https://github.com/anatawa12/blender-lib/archive/refs/heads/master.zip

## License

GPL-3.0-only. see LICENSE

When you create pull requests, please approve me to publish your changes in GPL 3.0 or later.
I may change the license to later version of GPL.

## To use this library

Add following code into the head of your script and use functions like `a.<func>()`.
Please replace `<minimum required library version>` with the version you want to use.

```python
import bpy
import addon_utils
from importlib import import_module

l = [m for m in addon_utils.modules() if "anatawa12_library_selector" in m.bl_info]
if len(l) == 0:
    bpy.context.window_manager.popup_menu(
        (lambda s, c: s.layout.label(text="Please install anatawa12's blender library from https://github.com/anatawa12/blender-lib")), 
        title="Error", icon='ERROR')
a = import_module(l[0].__name__)
a.version_check(<minimum required library version>)
```
