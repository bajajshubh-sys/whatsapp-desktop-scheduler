# WhatsApp Desktop Message Scheduler

A lightweight Python utility for sending one-time or recurring messages through the native WhatsApp Desktop client on Windows without browser automation overhead.

## Key Features

- **Dual Scheduling Modes**:
  - `once`: Dispatches a single message at a specific future date and time (like scheduled email).
  - `recurring`: Periodically sends messages at custom intervals within a defined daily window.
- **Fast & Browser-Free**: Uses native Windows `whatsapp://` URL protocols via shell commands.
- **Workspace Retention**: Automatically restores window focus or minimizes WhatsApp so your work isn't disrupted.
- **Secure Configuration**: Uses `.env` variables to prevent leaking personal phone numbers and text data.

## Requirements

- **OS**: Windows 10 or 11
- **Python**: 3.8+
- **WhatsApp**: Official WhatsApp Desktop application installed and logged in

## Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/](https://github.com/)<your-username>/whatsapp-desktop-scheduler.git
   cd whatsapp-desktop-scheduler