# High-Level Action Plan

This document outlines a high-level plan of action for addressing the major architectural issues discovered during the code review.

## 1. Refactor the API Server

*   **Timeline:** 2-3 weeks
*   **Priority:** High

**Tasks:**

1.  Create a new `web` module and move the Flask web server code from `cyberbackup_api_server.py` to this new module.
2.  Create a new `process_manager` module and move the C++ client process management logic from `cyberbackup_api_server.py` to this new module.
3.  Create a new `state_manager` module and move the backup job state management logic from `cyberbackup_api_server.py` to this new module.
4.  Update the `cyberbackup_api_server.py` file to use the new modules.

## 2. Secure the Client Communication

*   **Timeline:** 1-2 weeks
*   **Priority:** High

**Tasks:**

1.  Implement a secure communication channel between the API server and the C++ client. A named pipe or a socket would be a good option.
2.  Update the API server to send the backup configuration to the C++ client over the new secure communication channel.
3.  Update the C++ client to read the backup configuration from the new secure communication channel.

## 3. Centralize the Configuration

*   **Timeline:** 1 week
*   **Priority:** Medium

**Tasks:**

1.  Create a new `config.yml` file and move all the configuration from the various configuration files and the source code to this new file.
2.  Use a configuration library, such as `pyyaml`, to read the `config.yml` file.
3.  Update the source code to get its configuration from the new configuration system.
