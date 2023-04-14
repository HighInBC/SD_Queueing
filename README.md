# SD_Queueing

**Note:** This software is still in development and not ready for use yet.

SD_Queueing is a Redis-based queuing system for Stable Diffusion, designed for those who appreciate consecutive vowels in the word "queueing".

## Overview

The system is designed to manage a Redis queue that ingresses from clients needing to run Stable Diffusion jobs. A job can have a batch size between 1 and 8 and will contain all required parameters to perform the job, as well as a client-specific return queue.

### Client-side

Clients send a job request and then monitor the return queue for the response. The response will be in the form of a JSON object with the following structure:

```json
{
  "request": "<original request object>",
  "response": "<array of base64 images>"
}
```

arduino
Copy code

### Server-side

The server is responsible for monitoring the ingress queue, performing the Stable Diffusion API call, packaging the response, and sending it to the return queue.

The system supports any number of clients and servers.
