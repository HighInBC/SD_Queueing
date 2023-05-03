# SD_Queueing

**Note:** This software is still in development and not ready for use yet.

SD_Queueing is a Redis-based queuing system for Stable Diffusion, designed for managing jobs with different priorities.

## Overview

The system is designed to manage a Redis queue for ingressing job requests from clients needing to run Stable Diffusion jobs. A job can have a priority between 0 and 5 and will contain all required parameters to perform the job, as well as a client-specific return queue.

### Client-side

Clients send a job request and then monitor the return queue for the response. The request and response are JSON objects with the following structures:

A client request looks like:

```json
{
  "payload": "<stable diffusion api request>",
  "return_queue": "<client specific return queue>",
  "label": "<optional label>"
}
```

### Server-side

The server is responsible for monitoring the ingress queue, performing the Stable Diffusion API call, packaging the response, and sending it to the return queue.

The response from the server looks like:

```json
{
  "request": "<original request object>",
  "server_id": "<server identifier>",
  "response": "<array of base64 images>"
}
```

The system supports any number of clients and servers.

## Usage

This module provides functions for creating an SSH tunnel, connecting to a Redis instance, sending job requests to the ingress queue, reading from the ingress queue, sending responses to the return queue, and reading from the return queue.

Please refer to the code comments for detailed descriptions and usage examples of each function.

### AI assisted

The development of this software is assisted by Github Copilot and ChatGPT.