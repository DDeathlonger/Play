#!/usr/bin/env python3
"""
Spaceship Designer Flowchart Generator
Creates comprehensive flowcharts showing application functionality and AI iteration process
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_functionality_flowchart():
    """Create a flowchart showing the application functionality flow"""
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Colors for different components
    colors = {
        'entry': '#4CAF50',      # Green - Entry points
        'core': '#2196F3',       # Blue - Core functionality  
        'ui': '#FF9800',         # Orange - UI components
        'data': '#9C27B0',       # Purple - Data/Storage
        'output': '#F44336',     # Red - Output/Export
        'utils': '#607D8B'       # Blue Gray - Utilities
    }
    
    # Define flowchart elements
    boxes = [
        # Entry Points
        {'name': 'main.py\n(Entry Point)', 'pos': (5, 11), 'color': colors['entry']},
        {'name': 'VS Code\nLaunch Config', 'pos': (2, 11), 'color': colors['entry']},
        {'name': 'Task Runner', 'pos': (8, 11), 'color': colors['entry']},
        
        # Core Application
        {'name': 'spaceship_designer.py\n(Optimized App)', 'pos': (5, 9.5), 'color': colors['core']},
        {'name': 'spaceship_advanced.py\n(Legacy App)', 'pos': (2, 9.5), 'color': colors['core']},
        {'name': 'spaceship_utils.py\n(Shared Utilities)', 'pos': (8, 9.5), 'color': colors['utils']},
        
        # UI Components
        {'name': 'OptimizedSpaceshipApp\n(Main Window)', 'pos': (5, 8), 'color': colors['ui']},
        {'name': 'HighPerformanceViewer\n(3D OpenGL)', 'pos': (3, 6.5), 'color': colors['ui']},
        {'name': 'SimplifiedControlPanel\n(UI Controls)', 'pos': (7, 6.5), 'color': colors['ui']},
        
        # Core Logic
        {'name': 'OptimizedSpaceshipGenerator\n(Mesh Generation)', 'pos': (5, 5), 'color': colors['core']},
        {'name': 'MeshUtils\n(Primitives)', 'pos': (2, 3.5), 'color': colors['utils']},
        {'name': 'ConfigUtils\n(Save/Load)', 'pos': (5, 3.5), 'color': colors['utils']},
        {'name': 'PerformanceUtils\n(Optimization)', 'pos': (8, 3.5), 'color': colors['utils']},
        
        # Data Layer
        {'name': 'SpaceshipGeometryNode\n(Data Class)', 'pos': (1, 2), 'color': colors['data']},
        {'name': 'Grid Configuration\n(JSON)', 'pos': (5, 2), 'color': colors['data']},
        {'name': 'Trimesh Objects\n(3D Geometry)', 'pos': (9, 2), 'color': colors['data']},
        
        # Output
        {'name': 'STL Export\n(3D Printing)', 'pos': (2, 0.5), 'color': colors['output']},
        {'name': 'GLB Export\n(Web/Games)', 'pos': (5, 0.5), 'color': colors['output']},
        {'name': 'OBJ Export\n(General)', 'pos': (8, 0.5), 'color': colors['output']},
    ]
    
    # Draw boxes
    for box in boxes:
        # Create rounded rectangle
        bbox = FancyBboxPatch(
            (box['pos'][0] - 0.7, box['pos'][1] - 0.3),
            1.4, 0.6,
            boxstyle="round,pad=0.05",
            facecolor=box['color'],
            edgecolor='black',
            linewidth=1,
            alpha=0.8
        )
        ax.add_patch(bbox)
        
        # Add text
        ax.text(box['pos'][0], box['pos'][1], box['name'], 
               ha='center', va='center', fontsize=8, fontweight='bold',
               color='white', wrap=True)
    
    # Define connections
    connections = [
        # Entry to core
        ((5, 11), (5, 9.5)),      # main.py -> spaceship_designer
        ((2, 11), (2, 9.5)),      # VS Code -> legacy
        ((8, 11), (5, 9.5)),      # Task -> designer
        
        # Core to UI
        ((5, 9.5), (5, 8)),       # designer -> main window
        ((5, 8), (3, 6.5)),       # main -> viewer
        ((5, 8), (7, 6.5)),       # main -> controls
        
        # UI to logic  
        ((3, 6.5), (5, 5)),       # viewer -> generator
        ((7, 6.5), (5, 5)),       # controls -> generator
        
        # Logic to utils
        ((5, 5), (2, 3.5)),       # generator -> mesh utils
        ((5, 5), (5, 3.5)),       # generator -> config utils
        ((5, 5), (8, 3.5)),       # generator -> perf utils
        
        # Utils to data
        ((2, 3.5), (1, 2)),       # mesh -> module
        ((5, 3.5), (5, 2)),       # config -> json
        ((8, 3.5), (9, 2)),       # perf -> trimesh
        
        # Data to output
        ((5, 2), (2, 0.5)),       # json -> STL
        ((5, 2), (5, 0.5)),       # json -> GLB  
        ((5, 2), (8, 0.5)),       # json -> OBJ
    ]
    
    # Draw connections
    for start, end in connections:
        arrow = ConnectionPatch(start, end, "data", "data",
                              arrowstyle="->", shrinkA=5, shrinkB=5,
                              mutation_scale=20, fc="black", alpha=0.6)
        ax.add_patch(arrow)
    
    # Add title and legend
    ax.text(5, 11.7, 'Spaceship Designer - Functionality Flow', 
           ha='center', va='center', fontsize=16, fontweight='bold')
    
    # Create legend
    legend_elements = [
        mpatches.Patch(color=colors['entry'], label='Entry Points'),
        mpatches.Patch(color=colors['core'], label='Core Logic'),
        mpatches.Patch(color=colors['ui'], label='UI Components'),
        mpatches.Patch(color=colors['utils'], label='Utilities'),
        mpatches.Patch(color=colors['data'], label='Data Layer'),
        mpatches.Patch(color=colors['output'], label='Export Output')
    ]
    
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.0, 1.0))
    
    plt.tight_layout()
    plt.savefig('../reference/flowcharts/functionality_flow.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✓ Functionality flowchart saved: .github/copilot/reference/flowcharts/functionality_flow.png")

def create_ai_iteration_flowchart():
    """Create flowchart showing AI iteration process with context checking"""
    
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Colors for AI workflow
    colors = {
        'start': '#4CAF50',      # Green - Start
        'context': '#2196F3',    # Blue - Context operations
        'decision': '#FF9800',   # Orange - Decision points
        'action': '#9C27B0',     # Purple - Actions
        'update': '#F44336',     # Red - Updates
        'reference': '#607D8B'   # Blue Gray - References
    }
    
    # Define AI workflow elements
    workflow_boxes = [
        # Start
        {'name': 'GitHub Copilot\nActivation', 'pos': (5, 9.5), 'color': colors['start'], 'shape': 'oval'},
        
        # Context Check Phase
        {'name': 'Check Current\nContext', 'pos': (5, 8.5), 'color': colors['context']},
        {'name': 'Read .github/\ncopilot-instructions.md', 'pos': (2, 7.5), 'color': colors['reference']},
        {'name': 'Scan .github/copilot/\nreference/', 'pos': (8, 7.5), 'color': colors['reference']},
        {'name': 'Check File\nStructure', 'pos': (5, 7), 'color': colors['context']},
        
        # Decision Phase
        {'name': 'Context\nComplete?', 'pos': (5, 6), 'color': colors['decision'], 'shape': 'diamond'},
        {'name': 'Read Additional\nFiles', 'pos': (2, 5), 'color': colors['context']},
        
        # Action Phase
        {'name': 'Execute User\nRequest', 'pos': (5, 4.5), 'color': colors['action']},
        {'name': 'Modify Code/\nFiles', 'pos': (3, 3.5), 'color': colors['action']},
        {'name': 'Generate New\nContent', 'pos': (7, 3.5), 'color': colors['action']},
        
        # Update Phase
        {'name': 'Update Copilot Context\n.github/copilot/', 'pos': (5, 2.5), 'color': colors['update']},
        {'name': 'Update .github/\ncopilot-instructions.md', 'pos': (2, 1.5), 'color': colors['update']},
        {'name': 'Update Flowcharts\n.github/copilot/reference/flowcharts/', 'pos': (8, 1.5), 'color': colors['update']},
        
        # End
        {'name': 'Ready for Next\nIteration', 'pos': (5, 0.5), 'color': colors['start'], 'shape': 'oval'},
    ]
    
    # Draw workflow boxes
    for box in workflow_boxes:
        shape = box.get('shape', 'rect')
        
        if shape == 'diamond':
            # Diamond shape for decision
            diamond = mpatches.RegularPolygon(
                box['pos'], 4, radius=0.5, orientation=np.pi/4,
                facecolor=box['color'], edgecolor='black', alpha=0.8
            )
            ax.add_patch(diamond)
        elif shape == 'oval':
            # Oval shape for start/end
            oval = mpatches.Ellipse(
                box['pos'], 1.6, 0.6,
                facecolor=box['color'], edgecolor='black', alpha=0.8
            )
            ax.add_patch(oval)
        else:
            # Rectangle for normal boxes
            bbox = FancyBboxPatch(
                (box['pos'][0] - 0.8, box['pos'][1] - 0.3),
                1.6, 0.6,
                boxstyle="round,pad=0.05",
                facecolor=box['color'],
                edgecolor='black',
                linewidth=1,
                alpha=0.8
            )
            ax.add_patch(bbox)
        
        # Add text
        ax.text(box['pos'][0], box['pos'][1], box['name'], 
               ha='center', va='center', fontsize=8, fontweight='bold',
               color='white', wrap=True)
    
    # Define workflow connections
    workflow_connections = [
        # Main flow
        ((5, 9.5), (5, 8.5)),     # Start -> Check Context
        ((5, 8.5), (2, 7.5)),     # Check -> Read instructions
        ((5, 8.5), (8, 7.5)),     # Check -> Scan references
        ((2, 7.5), (5, 7)),       # Instructions -> File check
        ((8, 7.5), (5, 7)),       # References -> File check
        ((5, 7), (5, 6)),         # File check -> Decision
        
        # Decision branches
        ((5, 6), (2, 5)),         # Decision -> Read more (No)
        ((5, 6), (5, 4.5)),       # Decision -> Execute (Yes)
        ((2, 5), (5, 7)),         # Read more -> back to check
        
        # Action phase
        ((5, 4.5), (3, 3.5)),     # Execute -> Modify
        ((5, 4.5), (7, 3.5)),     # Execute -> Generate
        ((3, 3.5), (5, 2.5)),     # Modify -> Update
        ((7, 3.5), (5, 2.5)),     # Generate -> Update
        
        # Update phase
        ((5, 2.5), (2, 1.5)),     # Update -> Update instructions
        ((5, 2.5), (8, 1.5)),     # Update -> Update flowcharts
        ((2, 1.5), (5, 0.5)),     # Instructions -> Ready
        ((8, 1.5), (5, 0.5)),     # Flowcharts -> Ready
        
        # Loop back
        ((5, 0.5), (5, 9.5)),     # Ready -> Start (next iteration)
    ]
    
    # Draw connections with different styles
    for i, (start, end) in enumerate(workflow_connections):
        if i == len(workflow_connections) - 1:  # Loop back arrow
            # Curved arrow for loop back
            style = "arc3,rad=0.3"
            alpha = 0.4
            color = 'red'
        else:
            style = "arc3,rad=0.1"
            alpha = 0.7
            color = 'black'
            
        arrow = ConnectionPatch(start, end, "data", "data",
                              arrowstyle="->", shrinkA=5, shrinkB=5,
                              connectionstyle=style,
                              mutation_scale=20, fc=color, alpha=alpha)
        ax.add_patch(arrow)
    
    # Add labels for decision branches
    ax.text(3.5, 5.5, 'No', ha='center', va='center', fontsize=8, 
           bbox=dict(boxstyle="round,pad=0.2", facecolor='yellow', alpha=0.7))
    ax.text(5.5, 5.2, 'Yes', ha='center', va='center', fontsize=8,
           bbox=dict(boxstyle="round,pad=0.2", facecolor='lightgreen', alpha=0.7))
    
    # Add title
    ax.text(5, 9.8, 'GitHub Copilot - AI Iteration Process with Context Checking', 
           ha='center', va='center', fontsize=14, fontweight='bold')
    
    # Add side annotations
    ax.text(0.5, 8, 'CONTEXT\nPHASE', ha='center', va='center', fontsize=10,
           rotation=90, fontweight='bold', color=colors['context'])
    ax.text(0.5, 6, 'DECISION\nPHASE', ha='center', va='center', fontsize=10,
           rotation=90, fontweight='bold', color=colors['decision'])
    ax.text(0.5, 4, 'ACTION\nPHASE', ha='center', va='center', fontsize=10,
           rotation=90, fontweight='bold', color=colors['action'])
    ax.text(0.5, 2, 'UPDATE\nPHASE', ha='center', va='center', fontsize=10,
           rotation=90, fontweight='bold', color=colors['update'])
    
    plt.tight_layout()
    plt.savefig('../reference/flowcharts/ai_iteration_process.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✓ AI iteration flowchart saved: .github/copilot/reference/flowcharts/ai_iteration_process.png")

def create_data_flow_diagram():
    """Create a data flow diagram showing how data moves through the system"""
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Colors for data flow
    colors = {
        'input': '#4CAF50',      # Green - Input
        'process': '#2196F3',    # Blue - Processing
        'storage': '#FF9800',    # Orange - Storage
        'output': '#F44336'      # Red - Output
    }
    
    # Data flow elements
    data_elements = [
        # Input
        {'name': 'User Input\n(UI Controls)', 'pos': (1, 7), 'color': colors['input']},
        {'name': 'Configuration\n(JSON Files)', 'pos': (1, 5), 'color': colors['input']},
        
        # Processing
        {'name': 'SpaceshipGeometryNode\n(Validation)', 'pos': (3, 6), 'color': colors['process']},
        {'name': 'Grid Management\n(Position Logic)', 'pos': (5, 7), 'color': colors['process']},
        {'name': 'Mesh Generation\n(Primitives)', 'pos': (5, 5), 'color': colors['process']},
        {'name': 'Mesh Combination\n(Trimesh)', 'pos': (7, 6), 'color': colors['process']},
        
        # Storage
        {'name': 'Memory Cache\n(Mesh Objects)', 'pos': (3, 4), 'color': colors['storage']},
        {'name': 'GPU Buffer\n(Vertex Data)', 'pos': (7, 4), 'color': colors['storage']},
        
        # Output
        {'name': '3D Visualization\n(OpenGL)', 'pos': (9, 7), 'color': colors['output']},
        {'name': 'File Export\n(STL/GLB/OBJ)', 'pos': (9, 5), 'color': colors['output']},
        {'name': 'Configuration Save\n(JSON)', 'pos': (9, 3), 'color': colors['output']},
    ]
    
    # Draw data elements
    for element in data_elements:
        bbox = FancyBboxPatch(
            (element['pos'][0] - 0.6, element['pos'][1] - 0.4),
            1.2, 0.8,
            boxstyle="round,pad=0.05",
            facecolor=element['color'],
            edgecolor='black',
            linewidth=1,
            alpha=0.8
        )
        ax.add_patch(bbox)
        
        ax.text(element['pos'][0], element['pos'][1], element['name'], 
               ha='center', va='center', fontsize=8, fontweight='bold',
               color='white', wrap=True)
    
    # Data flow connections
    data_flows = [
        # Input to processing
        ((1, 7), (3, 6)),        # User input -> Module
        ((1, 5), (3, 6)),        # Config -> Module
        ((3, 6), (5, 7)),        # Module -> Grid
        ((3, 6), (5, 5)),        # Module -> Mesh gen
        
        # Processing flow
        ((5, 7), (7, 6)),        # Grid -> Combination
        ((5, 5), (7, 6)),        # Mesh gen -> Combination
        
        # Storage connections
        ((5, 5), (3, 4)),        # Mesh gen -> Cache
        ((7, 6), (7, 4)),        # Combination -> GPU
        
        # Output connections
        ((7, 6), (9, 7)),        # Combination -> Visualization
        ((7, 6), (9, 5)),        # Combination -> Export
        ((5, 7), (9, 3)),        # Grid -> Config save
    ]
    
    # Draw data flows
    for start, end in data_flows:
        arrow = ConnectionPatch(start, end, "data", "data",
                              arrowstyle="->", shrinkA=5, shrinkB=5,
                              mutation_scale=15, fc="gray", alpha=0.7,
                              linewidth=2)
        ax.add_patch(arrow)
    
    # Add title and annotations
    ax.text(5, 7.7, 'Spaceship Designer - Data Flow Diagram', 
           ha='center', va='center', fontsize=14, fontweight='bold')
    
    # Add data type labels
    ax.text(1, 1.5, 'INPUT', ha='center', va='center', fontsize=12,
           fontweight='bold', color=colors['input'])
    ax.text(5, 1.5, 'PROCESSING', ha='center', va='center', fontsize=12,
           fontweight='bold', color=colors['process'])
    ax.text(5, 2.5, 'STORAGE', ha='center', va='center', fontsize=12,
           fontweight='bold', color=colors['storage'])
    ax.text(9, 1.5, 'OUTPUT', ha='center', va='center', fontsize=12,
           fontweight='bold', color=colors['output'])
    
    plt.tight_layout()
    plt.savefig('../reference/flowcharts/data_flow_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✓ Data flow diagram saved: .github/copilot/reference/flowcharts/data_flow_diagram.png")

if __name__ == "__main__":
    print("Generating Spaceship Designer Reference Flowcharts...")
    print("=" * 60)
    
    try:
        # Set matplotlib to use non-interactive backend
        import matplotlib
        matplotlib.use('Agg')
        
        # Generate all flowcharts
        create_functionality_flowchart()
        create_ai_iteration_flowchart()
        create_data_flow_diagram()
        
        print("=" * 60)
        print("✓ All flowcharts generated successfully!")
        print("Files created in .github/copilot/reference/flowcharts/:")
        print("  - functionality_flow.png")
        print("  - ai_iteration_process.png") 
        print("  - data_flow_diagram.png")
        
    except Exception as e:
        print(f"Error generating flowcharts: {e}")
        import traceback
        traceback.print_exc()