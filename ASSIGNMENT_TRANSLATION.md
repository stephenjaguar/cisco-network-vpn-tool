# Candidate Lab - Networking Mercado Libre

## Automation Challenge

## General Objective

Evaluate the candidate's ability to develop automation scripts that configure Cisco network devices using a frontend, plan the automation of an IPSec VPN configuration between security devices from different vendors, implement configuration validation mechanisms, and use a version control system (Git) to manage the project in an organized way.

## Part 1: Cisco Switch Automation with Configuration Frontend and Git

### Requirements

The candidate must develop a Python automation script, managed with Git, that interacts with a Cisco switch, simulated or real, to configure VLANs and the hostname through a frontend.

### 1. Git Repository

- Create a public Git repository, preferably on a platform such as GitHub, GitLab, or Bitbucket.
- Initialize the repository with a README file that briefly describes the project.

### 2. VLAN Configuration Frontend

- Develop a frontend, either a graphical interface using Tkinter, PyQt, another GUI library, or a simple Flask web interface, that allows the user to enter the VLAN information to configure.
- The interface must allow specifying the ID and name of at least the following VLANs:
  - VLAN 10: name `VLAN_DATA`
  - VLAN 20: name `VLAN_VOICE`
  - VLAN 50: name `VLAN_SECURITY`

### 3. VLAN Configuration

- Use the information provided through the frontend to generate and apply the VLAN configuration on the Cisco switch using network automation libraries.

### 4. Switch Hostname Change

- Implement configuration of the switch hostname to a specific value, for example `AUTOMATED_SWITCH`.
- This value can be predefined in the script or entered through the frontend.

### 5. Save Configuration

- Include functionality to execute the command required to save the current switch configuration to NVRAM.

### 6. Configuration Backup

- Implement a function to back up the switch configuration and save it to a local file whose filename includes the hostname and date/time, or optionally upload it to a remote server.

### 7. Configuration Validation

- After applying the configuration, the script must validate that the current switch configuration matches the desired configuration for VLANs and hostname.
- If any deviation is detected, the script must show a clear alert in the frontend or script output indicating the non-standard configuration found.

### 8. Version Control

- Make regular, meaningful commits in the Git repository, with descriptive messages explaining the changes made.

### 9. README

The README file must contain:

- A general project description.
- Detailed instructions for running the script, including dependency installation.
- Information on how to interact with the frontend.
- Any other relevant implementation notes.
- Optional screenshots of the frontend and/or script output.

### Part 1 Deliverables

- Git repository URL containing all Python source code for backend and frontend.
- README file in the repository.
- Evidence that the frontend works, through screenshots in the README or a separate repository file.
- Evidence of switch configuration, such as switch CLI screenshots showing created VLANs and changed hostname.
- Configuration backup file, either in the repository or with its location documented in the README.
- Evidence of validation and alert execution, through screenshots or script output.
- Commit history in Git demonstrating proper use of version control, if applicable.

## Part 2: Automation Planning for IPSec VPN Configuration Between FortiGate and Palo Alto

### Requirements

The candidate must plan automation for configuring an IPSec VPN between a FortiGate device and a Palo Alto firewall, documenting the plan in the same Git repository.

### 1. Automation Plan

Create a document, preferably Markdown, inside the Git repository that details the plan to automate the IPSec VPN configuration between FortiGate and Palo Alto. The document must include:

- Parameter definition: VPN parameters such as WAN IP addresses, example local networks, tunnel network `169.255.1.0/30` with IP assignment to each endpoint, and compatible Phase 1 and Phase 2 proposals.
- Tool/API identification: possible tools or APIs such as Fortinet REST API, Palo Alto REST API, SSH with specific libraries, or centralized management tools.
- Automation steps: logical steps that an automation script should follow to configure the VPN on both firewalls, including object creation, proposal definition, firewall policies, and tunnel establishment.
- Specific considerations: challenges and special considerations when automating configuration between devices from different manufacturers.
- Configuration validation and alerts: strategy to validate that the VPN configuration was correctly applied on both devices, including verification methods, commands or API calls, and how alerts would be generated for failures or deviations.

### Optional Git Deliverables

- If possible, include conceptual or partial example scripts or configuration files for both firewalls.
- If possible, include a script to test connectivity through the IPSec tunnel, assuming a test environment can be established.

### Part 2 Deliverables

- Same Git repository as Part 1.
- Document with the detailed IPSec VPN automation plan, in Markdown or another readable format, inside the repository.
- Optional FortiGate and Palo Alto example scripts or configuration files in the repository.
- Optional connectivity test script in the repository.

## Evaluation Criteria

### Part 1

- Functionality and efficiency of the automation script and frontend.
- Clarity and organization of backend and frontend code.
- Basic frontend design and usability.
- Correct configuration of VLANs and hostname using the frontend.
- Successful implementation of configuration save and backup.
- Effective implementation of configuration validation logic and alert presentation.
- Proper Git usage for version control, including meaningful commits and repository organization.
- Quality and clarity of the README file.

### Part 2

- Understanding of IPSec VPN concepts.
- Correct definition of VPN parameters.
- Quality, detail, and feasibility of the automation plan documented in Git.
- Proper identification of relevant tools or APIs for FortiGate and Palo Alto.
- Understanding of automation challenges in heterogeneous environments.
- Clarity and effectiveness of the VPN configuration validation strategy and proposed alert handling.
- Optional quality and usefulness of VPN example scripts or configuration files.
- Optional quality and functionality of the connectivity test script.

## Candidate Instructions

- Any resources may be used, including documentation and internet resources.
- Estimated completion time is 7 days.
- The main deliverable is the Git repository URL containing all requested code and documentation. Ensure the repository is accessible for review.

## Additional Considerations

- A functional VPN simulation is not expected. If provided, it is a bonus.
- For Part 1, simulation with Packet Tracer or GNS3 is expected.
