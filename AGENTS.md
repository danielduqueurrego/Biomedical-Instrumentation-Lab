## Student installation and usability priority
This project must be as easy as possible for undergraduate students to install and use.

### Requirements
- Minimize required software installations.
- Prefer a single Python distribution for students, ideally Anaconda or another free Conda-based option.
- Avoid requiring students to install multiple tools, IDEs, package managers, or complex drivers unless absolutely necessary.
- The student workflow should be:
  1. install the required Python distribution,
  2. create or load one environment,
  3. run one command or double-click one launcher script.

### Python dependency policy
- Keep dependencies minimal.
- Prefer widely used, stable, free packages.
- Avoid unnecessary GUI frameworks or heavy libraries unless they clearly improve usability.
- Do not introduce dependencies that are difficult to install on Windows or macOS.

### Deliverable expectations
- Provide an environment file for setup.
- Provide a simple launch script for students.
- Provide clear setup instructions written for beginners.
- Prefer one main application entry point per lab.
- Design the software so students can use it without editing source code.

### Usability goal
The final student-facing workflow should feel close to:
- connect Arduino,
- open terminal or launcher,
- run one command,
- see live plots,
- save data automatically.
