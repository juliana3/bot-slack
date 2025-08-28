# bot-slack

Automation of new employee onboarding in PeopleForce.

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/juliana3/bot-slack)

## Table of Contents

- [Description](#description)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Directory Structure](#directory-structure)
- [Contributing](#contributing)
- [License](#license)

## Description

The `bot-slack` project is a Python-based Slack bot designed to automate the process of onboarding new employees within the PeopleForce HR management system. This bot streamlines the initial setup and integration of new hires, reducing manual effort and ensuring a consistent onboarding experience.

## Features

- **Automated Onboarding:** Automates the creation and setup of new employee accounts in PeopleForce.
- **Slack Integration:** Seamlessly integrates with Slack to provide real-time updates and notifications.
- **Customizable Workflows:** Supports customizable workflows to adapt to different onboarding processes.
- **Error Handling:** Robust error handling and logging to ensure reliable operation.
- **Cron Job Scheduling:** Utilizes cron jobs for scheduled tasks and reprocessing.

## Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/juliana3/bot-slack.git
    cd bot-slack
    ```

2.  **Create a virtual environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate  # On Windows
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  **Set up environment variables:**

    Create a `.env` file in the root directory with the following variables:

    ```
    SLACK_BOT_TOKEN=your_slack_bot_token
    PEOPLEFORCE_API_KEY=your_peopleforce_api_key
    DATABASE_URL=your_database_url
    ```

    Replace `your_slack_bot_token`, `your_peopleforce_api_key`, and `your_database_url` with your actual credentials.

2.  **Configure the database:**

    Ensure your database is properly configured and accessible. The application uses the `DATABASE_URL` environment variable to connect to the database.

## Usage

1.  **Run the bot:**

    ```bash
    python app.py
    ```

    This command starts the Slack bot, which will listen for events and respond accordingly.

2.  **Run the cron job (optional):**

    ```bash
    python cron_reproceso.py
    ```

    This script is used for scheduled tasks and reprocessing.  Configure a cron job to run this script at desired intervals.

## Directory Structure

```
bot-slack/
├── .gitignore              # Specifies intentionally untracked files that Git should ignore
├── .vscode/               # VS Code configuration directory
├── README.md               # Project README file
├── app.py                  # Main application file
├── cron_reproceso.py       # Script for cron job scheduling
├── db/                     # Database related files
├── handlers/               # Directory containing event handlers
├── requirements.txt        # List of Python dependencies
├── services/               # Directory containing external services integration
├── static/                 # Directory for static files (e.g., images, CSS)
└── templates/              # Directory for HTML templates
```

## Contributing

We welcome contributions to the `bot-slack` project! Here's how you can contribute:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Implement your changes and write tests.
4.  Submit a pull request with a clear description of your changes.

## License

This project is open source and available under the [MIT License](LICENSE).
