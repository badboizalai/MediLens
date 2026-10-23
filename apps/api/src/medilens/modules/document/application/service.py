from uuid import UUID

from medilens.modules.document.domain.models import (
    ALLOWED_TYPES,
    EVENT_DOCUMENT_UPLOADED,
    MAX_BYTES,
    MAX_PENDING_UPLOADS,
    PRESIGN_TTL_SECONDS,
    SNIFF_BYTES,
    STATUS_PENDING,
    STATUS_UPLOADED,
    Document,
    DocumentNotFound,
    DuplicateDocument,
    FileTooLarge,
    Presigned,
    TooManyPendingUploads,
    UnsupportedFileType,
    UploadMissing,
    quarantine_key,
    sniff_mime,
)
from medilens.modules.document.domain.ports import (
    DocumentRepository,
    EventOutbox,
    ObjectStorage,
    ProfileOwnership,
)


class UploadService:
    """The caller commits the DB transaction; the outbox row shares it."""

    def __init__(
        self,
        storage: ObjectStorage,
        repo: DocumentRepository,
        owners: ProfileOwnership,
        outbox: EventOutbox,
    ) -> None:
        self._storage, self._repo, self._owners, self._outbox = storage, repo, owners, outbox

    def _scope(self, subject: str) -> list[UUID]:
        ids = list(self._owners.owned_profile_ids(subject))
        self._repo.scope_to(ids)
        return ids

    def request_upload(
        self, subject: str, profile_id: UUID, content_type: str, size_bytes: int
    ) -> tuple[Document, Presigned]:
        if profile_id not in self._scope(subject):
            raise DocumentNotFound
        if content_type not in ALLOWED_TYPES:
            raise UnsupportedFileType("Accepted formats: JPEG, PNG, HEIC, PDF.")
        if size_bytes > MAX_BYTES:
            raise FileTooLarge("Maximum file size is 20 MB.")
        if self._repo.count_pending() >= MAX_PENDING_UPLOADS:
            raise TooManyPendingUploads("Finish or wait for your pending uploads first.")
        doc_id = self._repo.new_id()
        doc = Document(
            doc_id, profile_id, quarantine_key(profile_id, doc_id), content_type, STATUS_PENDING
        )
        self._repo.add_pending(doc)
        presigned = self._storage.presign_put(
            doc.storage_key, content_type, size_bytes, PRESIGN_TTL_SECONDS
        )
        return doc, presigned

    def get(self, subject: str, document_id: UUID) -> Document:
        self._scope(subject)
        doc = self._repo.get(document_id)
        if doc is None:
            raise DocumentNotFound
        return doc

    def complete(self, subject: str, document_id: UUID) -> Document:
        self._scope(subject)
        doc = self._repo.get(document_id)
        if doc is None:
            raise DocumentNotFound
        if doc.status == STATUS_UPLOADED:
            return doc  # idempotent retry: no second event
        size = self._storage.size(doc.storage_key)
        if size is None:
            raise UploadMissing("No uploaded object found for this document.")
        if size > MAX_BYTES:
            self._reject(doc)
            raise FileTooLarge("Maximum file size is 20 MB.")
        if sniff_mime(self._storage.read_head(doc.storage_key, SNIFF_BYTES)) != doc.mime:
            self._reject(doc)
            raise UnsupportedFileType("File content does not match an accepted format.")
        digest = self._storage.sha256(doc.storage_key)
        if self._repo.has_duplicate(doc.profile_id, digest, doc.id):
            self._reject(doc)
            raise DuplicateDocument("This file was already uploaded for this profile.")
        try:
            self._repo.mark_uploaded(doc.id, digest)
        except DuplicateDocument:  # lost the race against a concurrent complete
            self._reject(doc)
            raise
        self._outbox.add(
            EVENT_DOCUMENT_UPLOADED,
            {
                "document_id": str(doc.id),
                "profile_id": str(doc.profile_id),
                "mime": doc.mime,
                "storage_key": doc.storage_key,
            },
        )
        return Document(doc.id, doc.profile_id, doc.storage_key, doc.mime, STATUS_UPLOADED, digest)

    def _reject(self, doc: Document) -> None:
        self._repo.mark_rejected(doc.id)  # sha256 stays '': outside the unique index
        self._storage.delete(doc.storage_key)  # U-08: no rejected leftovers in quarantine
