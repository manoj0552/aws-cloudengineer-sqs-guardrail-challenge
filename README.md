# Cloud Engineer Guardrail Challenge: SQS Security Compliance

## Overview

In this assignment you will build an enterprise-grade solution using AWS CloudFormation (YAML only) and a Python Lambda function. The solution will serve as a guardrail for newly created SQS queues. You will deploy your solution via GitHub by forking the repository and submitting a pull request. Use of GitHub Actions for CI/CD is a bonus.

---

## Assignment Requirements

### 1. CloudFormation Template (YAML Only)

- **Template Language:** YAML exclusively.
- **Resources:**
  - **Lambda Function:** Deploy a Python-based Lambda function.
  - **IAM Role:** Create an IAM role for the Lambda function with an attached permission boundary. You can define the managed policy in the same template or reference an external policy via a parameter.
  - **EventBridge Rule:** Configure an EventBridge rule to trigger the Lambda function on SQS queue creation events (for example, when the `CreateQueue` API call is made).
  - **Optional Alerting Mechanism:** Optionally, create an SNS topic that the Lambda function can use to publish alerts.
  - **Control Tower Guardrail:** Via CloudFormation, add a native Control Tower enabled control that enforces a guardrail requiring any Amazon SQS queue to have a dead-letter queue configured in **us-east-1**. This enabled control should be applied to an example Organizational Unit (OU). DO NOT use a Lambda function to enable this control, it must be done via Cloudformation resource.
- **Parameters & Outputs:**
  - Parameterize key properties such as Lambda runtime, memory size, permission boundary ARN, and SNS topic ARN (if used).
  - Include outputs that provide resource ARNs (e.g., Lambda function ARN, IAM role ARN).

### 2. Python Lambda Function

- **Trigger:** The function must be invoked upon an SQS queue creation event.
- **Functionality:** The Lambda function should perform the following checks:
  - **VPC Endpoint Check:** Verify that a VPC endpoint for SQS exists.
  - **Encryption-at-Rest:** Ensure that the SQS queue has encryption enabled.
  - **Customer-Managed Key (CMK):** Confirm that the queue uses a customer-managed key (CMK) rather than an AWS-managed key.
  - **Tag Verification:** Check that the queue is tagged with the following keys (values can be arbitrary):
    - **Name**
    - **Created By**
    - **Cost Center**
  - **Alerting:** If any check fails, trigger an alert (for example, by publishing a message to an SNS topic or by logging an error).
- **Code Quality:**  
  - Follow Python best practices (logging, error handling, modularity, and inline documentation).
  - Ensure that the very first line of your Python file contains a comment in the following format:
    ```
    # SecretCode: <YourGitHubUsername>-2025-<YourRandom3CharCode>
    ```
    *(Replace `<YourGitHubUsername>` and `<YourRandom3CharCode>` with your own values.)*

### 3. Documentation (README)

Your README file should include:

- **Deployment Instructions:**  
  - Step-by-step guidance to deploy the CloudFormation stack using the AWS CLI or AWS Console.
  - Explanation of any required parameters.
- **Design Decisions:**  
  - A brief description of your approach to implementing the permission boundary and how your solution can be extended or applied in a multi-account environment.
- **Bonus (Optional):**  
  - Any GitHub Actions configuration you add to demonstrate CI/CD capabilities is a bonus.

### 4. Packaging & Submission

- **Suggested File Structure:**

  ```
  /CloudGuardRailChallenge.zip
  ├── README.md
  ├── template.yaml         # CloudFormation template in YAML
  └── lambda_function
      └── lambda_function.py  # Python Lambda code
  ```

- **Submission:**  
  - Fork this GitHub repository for this test.
  - Commit your changes and submit a pull request for evaluation.

# testing git push