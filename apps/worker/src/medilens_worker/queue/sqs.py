"""SQS implementation (cloud, or LocalStack via endpoint_url)."""

import boto3

from medilens_worker.queue.base import Message


class SqsQueue:
    def __init__(
        self, queue_url: str, dlq_url: str, endpoint_url: str | None = None, wait_seconds: int = 20
    ) -> None:
        self._c = boto3.client("sqs", endpoint_url=endpoint_url)
        self._url, self._dlq, self._wait = queue_url, dlq_url, wait_seconds

    def receive(self) -> Message | None:
        r = self._c.receive_message(
            QueueUrl=self._url, MaxNumberOfMessages=1, WaitTimeSeconds=self._wait
        )
        for m in r.get("Messages", []):
            return Message(m["ReceiptHandle"], m["Body"])
        return None

    def send(self, body: str, delay_seconds: int = 0) -> None:
        self._c.send_message(
            QueueUrl=self._url, MessageBody=body, DelaySeconds=min(delay_seconds, 900)
        )

    def ack(self, msg: Message) -> None:
        self._c.delete_message(QueueUrl=self._url, ReceiptHandle=msg.receipt)

    def extend_visibility(self, msg: Message, seconds: int) -> None:
        self._c.change_message_visibility(
            QueueUrl=self._url, ReceiptHandle=msg.receipt, VisibilityTimeout=seconds
        )

    def send_dlq(self, msg: Message, reason: str) -> None:
        self._c.send_message(
            QueueUrl=self._dlq,
            MessageBody=msg.body,
            MessageAttributes={"reason": {"DataType": "String", "StringValue": reason[:200]}},
        )
        self.ack(msg)
