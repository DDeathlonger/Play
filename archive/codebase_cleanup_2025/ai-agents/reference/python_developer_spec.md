You are an expert Python developer specializing in 3D modeling, GUI applications, and file I/O for Windows environments. Your task is to generate a complete, self-contained Python script (compatible with Python 3.14 running in VS Code on Windows) that fulfills the following requirements exactly. Do not omit or alter any details—implement everything as specified.

### Core Objective
Create a GUI application that generates and previews a downloadable 3D mesh file of a simplistic, cartoonish spaceship. The spaceship should feature crazy cool and sleek angles. Make it super clean in design, with no limits on intricate details in the generation code (e.g., precise vertices, edges, and textures for a polished look).

### Step-by-Step Generation Process
1. **Reference Image Generation**: First, programmatically generate a 2D reference image (e.g., using Matplotlib or Pillow) depicting the simplistic cartoonish spaceship from a side or interactive perspective view. This image serves as a visual guide and should be displayed in the GUI for reference.

2. **3D Mesh Generation**: Using the reference image as a blueprint, generate a matching 3D textured mesh file. Ensure the mesh is downloadable in standard formats like STL or GLB. The mesh must look identical to the reference image in style—cartoonish, sleek, submarine-like, with connected shapes and high-detail geometry.

### Geometry Management
- Represent the entire 3D model using a static array grid (e.g., a NumPy array or similar data structure) stored in local storage. This array grid holds and modifies the geometry data (vertices, faces, textures, etc.) for the spaceship.
- Ensure every shape in the model is fully connected to every other shape (no disconnected components—use union operations or welding in the mesh generation).
- The array grid must support saving to the local filesystem (e.g., as a JSON or binary file) for reloading and recreating the model later.

### GUI Features
- Build the entire application with a GUI (using Tkinter, PyQt, or similar—prefer something lightweight and Windows-compatible).
- Dedicate a main preview pane to render the 3D model in real-time based on the current array grid data. Updates to the grid should trigger efficient re-renders (e.g., only regenerate affected geometry to avoid lag).
- Include a dedicated editing panel (e.g., sidebar or bottom section) where users can adjust:
  - The number of various geometries (e.g., sliders or inputs for adding/subtracting fuselage sections, fins, engines, etc.).
  - Properties of each geometry (e.g., scale, rotation, texture parameters, position—store all changes directly in the array grid).
- Maintain all geometry properties persistently in the local storage data file (load on startup, auto-save on edits).

### Export and Usability
- Provide buttons in the GUI to export the final mesh as a downloadable file in STL, GLB, or another standard 3D format.
- The script must run standalone in VS Code on Windows—include all necessary imports, handle dependencies (assume standard libraries like NumPy, Matplotlib, and a 3D library like Trimesh or Open3D are available), and ensure no external installs are required beyond what's in a standard Python 3.14 env.
- Output the complete script in a single, executable code block. Test mentally for efficiency, cleanliness, and full connectivity of shapes.

Generate the full Python script now, ensuring it produces a "crazy cool" yet submarine-inspired cartoonish spaceship that's super clean and detailed.