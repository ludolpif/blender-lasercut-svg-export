# Notes

# From initial manual reading (4.2 on 12/2024)

https://docs.blender.org/manual/en/4.2/advanced/extensions/addons.html

- Replace all references to the module name to `__package__`.
- Make all module imports to use relative import.
- Use wheels to pack your external Python dependencies.
- Remember to test it thoroughly.

