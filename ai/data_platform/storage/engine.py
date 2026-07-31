"""Storage engine."""
from .models import DataPartition, StorageBucket, StorageType, StoredObject


class StorageEngine:
    def __init__(self):
        self._buckets: dict[str, StorageBucket] = {}
        self._objects: dict[str, StoredObject] = {}
        self._partitions: dict[str, DataPartition] = {}

    def create_bucket(self, bucket: StorageBucket) -> StorageBucket:
        self._buckets[bucket.bucket_id] = bucket
        return bucket

    def get_bucket(self, bucket_id: str) -> StorageBucket | None:
        return self._buckets.get(bucket_id)

    def list_buckets(self, storage_type: StorageType | None = None) -> list[StorageBucket]:
        buckets = list(self._buckets.values())
        if storage_type:
            buckets = [b for b in buckets if b.storage_type == storage_type]
        return buckets

    def store_object(self, obj: StoredObject) -> StoredObject:
        self._objects[obj.object_id] = obj
        bucket = self._buckets.get(obj.bucket_id)
        if bucket:
            bucket.used_bytes += obj.size_bytes
        return obj

    def get_object(self, object_id: str) -> StoredObject | None:
        return self._objects.get(object_id)

    def get_objects_by_bucket(self, bucket_id: str) -> list[StoredObject]:
        return [o for o in self._objects.values() if o.bucket_id == bucket_id]

    def delete_object(self, object_id: str) -> bool:
        obj = self._objects.get(object_id)
        if not obj:
            return False
        bucket = self._buckets.get(obj.bucket_id)
        if bucket:
            bucket.used_bytes = max(0, bucket.used_bytes - obj.size_bytes)
        del self._objects[object_id]
        return True

    def create_partition(self, partition: DataPartition) -> DataPartition:
        self._partitions[partition.partition_id] = partition
        return partition

    def get_partition(self, partition_id: str) -> DataPartition | None:
        return self._partitions.get(partition_id)

    def get_partitions_by_dataset(self, dataset: str) -> list[DataPartition]:
        return [p for p in self._partitions.values() if p.dataset == dataset]

    def get_stats(self) -> dict:
        buckets = list(self._buckets.values())
        return {
            "buckets": len(buckets),
            "objects": len(self._objects),
            "partitions": len(self._partitions),
            "total_used_bytes": sum(b.used_bytes for b in buckets),
        }
