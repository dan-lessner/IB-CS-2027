# Copilot Instructions for IB-CS-2027

## Project Overview
This repository contains various Python projects and examples, primarily focused on educational purposes. The projects include simulations, games, and algorithmic implementations. The codebase is organized into directories based on topics or teams, such as `OOP`, `L-Systems`, and `Examples`.

### Key Components
- **Aquarium Simulations**: Found in `Akvarka/` and `Examples/OOP/`, these projects simulate fish movement and interactions using `tkinter`.
- **L-Systems**: Located in `L-Systems/`, these projects implement Lindenmayer systems for procedural graphics generation.
- **Games**: Examples include pool simulations in `OOP/` and `Examples/OOP/`.
- **Algorithmic Examples**: Found in `Examples/`, these include basic algorithms and data structure implementations.

## Developer Workflows
### Running Projects
1. Navigate to the desired project directory.
2. Run the Python script using:
   ```bash
   python <script_name>.py
   ```

### Adding Dependencies
- Most projects use only the Python standard library. If external dependencies are added, document them in the project folder.

### Debugging
- Use `print` statements for debugging.
- For GUI-based projects, ensure the `tkinter` window is responsive during debugging.

## Project-Specific Conventions
### General
- Use `tkinter` for GUI-based projects.
- Follow object-oriented programming principles where applicable.

### Naming Conventions
- Use descriptive names for variables and functions.
- Class names should follow PascalCase.

### Code Structure
- Keep related functions and classes in the same file.
- Use comments to explain complex logic.

## Integration Points
### External Dependencies
- `tkinter`: Used for GUI development.
- `math`: Used for mathematical calculations.

### Cross-Component Communication
- Projects are generally standalone. Shared utilities or libraries should be placed in a common directory.

## Examples of Patterns
### Object-Oriented Programming
- Example: `Fish` class in `Examples/OOP/aqua_adv_oop_inheritance.py`.
- Pattern: Encapsulate behavior and attributes in classes.

### Event-Driven Programming
- Example: `drop_food` function in `Examples/OOP/aqua_adv_list_of_dicts.py`.
- Pattern: Bind events to GUI elements using `tkinter`.

### Algorithm Implementation
- Example: Postfix evaluation in `Calculation interpreter/Chris/PostfixV1.py`.
- Pattern: Use stacks for expression evaluation.

## Key Files and Directories
- `Akvarka/`: Aquarium simulations.
- `L-Systems/`: Lindenmayer system implementations.
- `Examples/`: Miscellaneous examples and tutorials.
- `OOP/`: Object-oriented programming examples.

## Notes for AI Agents
- Focus on maintaining readability and simplicity.
- Avoid introducing external dependencies unless necessary.
- Ensure GUI elements are responsive and visually appealing.

---
Feel free to update this document as the project evolves.